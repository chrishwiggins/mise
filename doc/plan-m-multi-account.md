# Plan: `m` multi-account syntax (`m h,g meets`, `m h,g,cu i`)

## Goal

`m` currently resolves exactly one account alias per invocation (`$account`,
then `$gmail_acct=(-e "$email")`, threaded through every dispatch branch via
`exec gmail-api-rw "${gmail_acct[@]}" ...`). Every action -- `i`, `sent`,
`urls`, `meets`, etc. -- only ever sees one mailbox.

Success: `m h,g,cu i` (and any other action) runs the same command once per
account in the comma list, in order, with clear per-account headers, using
one invocation instead of three. `m h meets` (single account, today's
behavior) is unchanged. No action-specific code needs to know about
multi-account; it falls out of how the top-level alias is resolved.

Verify: run `m h,g i`, `m h,g,cu meets`, `m h,g sent`, confirm each prints
results for both/all accounts in order, with no cross-account state bleed
(e.g. account A's cache doesn't leak into account B's listing), and that
`m h i` (single account) is byte-identical to pre-change behavior.

## Context

Traced the full account-resolution path in `bash/m`:

- Account alias is captured once, as a scalar, at the arg-parsing loop:
  `elif [[ -z "$account" ]] && [[ -n "${ACCTS[$arg]:-}" ]]; then account="$arg"`
  (`bash/m` ~line 2291). `-z "$account"` means only the FIRST alias-shaped
  token is ever captured; a second one falls through to `rest` today and
  gets treated as a positional arg to the backend (garbage input for most
  actions).
- After parsing, `$account` resolves to `$gmail_flag`/`$account_email` via
  the `ACCTS`/`EMAILS` associative arrays (loaded from
  `~/.config/mail-tools/accounts.json`), producing `gmail_acct=(-e "$email")`
  (~line 2441-2451).
- `gmail_acct` is then passed into 8-9 separate `exec gmail-api-rw
  "${gmail_acct[@]}" ...` call sites scattered across the `case "$action" in`
  dispatch (~line 2459 onward) -- one per action family (i/q, sent, send,
  draft/reply/fwd/..., urls, meets, scheduled). Every one of these is a
  terminal `exec`, meaning the current process is replaced; nothing after
  an `exec` in that branch runs, so there is no existing hook point to loop
  "after the real work, before exit."
- Aliases can collide on the same mailbox: `j`/`joint`, `u`/`cu`, `h`/`hNY`
  all resolve to one email each (verified via `~/.config/mail-tools/accounts.json`).
  A multi-account request should NOT be surprised by this -- `m h,hNY i`
  asking for the same mailbox twice should just run it twice (harmless,
  user's choice), not silently dedupe. Silent dedup would be a surprise
  behavior no one asked for.
- Precedent for "per-account variation" already exists in a different
  form: `--outbox <alias>` reads from one account and sends from another,
  implemented in the Python backend via `_authenticated_service(args,
  scope, email_override=...)`. That pattern is for a different feature
  (asymmetric read/send accounts) and doesn't generalize to "run the same
  read on N accounts" -- it's one extra service object, not a loop over N.
- `m` is explicitly documented (top of file, "MENTAL MODEL" section) as
  the "user-forgiving frontend" where convenience/looping logic belongs,
  with `gmail-api-rw` as the strict single-account backend. This cuts
  toward implementing the fan-out in `bash/m`, not in the Python backend.

## Approach

Chosen approach: self-invocation loop in `bash/m`, before the account is
resolved to a single scalar.

Detect a comma-list in the account slot early (same place the single-alias
branch lives, ~line 2291). If every comma-separated token resolves to a
known alias, do NOT set `$account` to the raw string. Instead, split it,
and for each alias, re-invoke `"$0"` (the same `m` script) with that one
alias substituted back into the original argv, capturing/streaming output
with an account header. Exit after the loop with the worst exit code seen
(so a downstream failure isn't silently swallowed by an earlier success).

This means:
- Every existing single-account code path (arg parsing, dispatch, all 8-9
  `exec` sites) is untouched. Zero risk of breaking single-account usage,
  because single-account usage never enters the new branch.
- Every action gets multi-account for free -- `meets`, `i`, `sent`, `urls`,
  even `reply`/`send` (though sending to N accounts at once from one typed
  command is worth a safety gate, see Risks) -- without editing 8 dispatch
  arms individually.
- The recursion is one level deep and bounded by the length of the comma
  list (never more than ~11, the number of configured aliases), so no
  runaway-recursion concern.

### Considered and rejected

1. Loop inside each of the 8-9 `exec` call sites. Rejected: touches every
   dispatch branch, multiplies the diff size and review surface by ~9x for
   the same behavior, and any new action added later would need to
   remember to add its own loop (the self-invocation approach makes new
   actions multi-account-capable automatically, with no extra code).

2. Push multi-account into the Python backend (`gmail-api-rw`), e.g. a
   `--accounts a,b,c` flag that loops internally. Rejected: violates the
   documented division of labor ("foibles go in m ... infra goes in
   gmail-api-rw"). Also the backend's account resolution
   (`_authenticated_service`/`resolve_account`) is built around exactly one
   OAuth token per invocation; teaching it to juggle N tokens and merge N
   result sets is a much bigger, riskier change for the same user-facing
   outcome.

3. A single Python-level "meta mode" that only `do_meets` uses (loop over
   every account with a live `/tmp/spool` cache, no comma syntax at all).
   This was the original narrower idea. Rejected per explicit user
   correction: the ask is a general `m`-level mechanism (`h,g` or `h,g,cu`
   in the account slot), available to any action, not a `meets`-only
   special case.

4. True parallel fan-out (background each per-account run, join at the
   end). Rejected for v1: output interleaving from N concurrent processes
   writing to the same terminal is a real usability problem (garbled
   interactive prompts, e.g. `meets`'s "open which?" menu, would be
   unusable across accounts run concurrently). Sequential is simpler,
   correct, and fast enough at N<=11. Can revisit if someone actually
   complains about wall-clock time.

## Steps

### 1. Detect and validate the comma-list in the account slot

- Files: `bash/m`
- What: In the arg-parsing loop, where the single-alias branch lives
  (`elif [[ -z "$account" ]] && [[ -n "${ACCTS[$arg]:-}" ]]; then
  account="$arg"`), add a branch that fires when `$arg` contains a comma
  AND every comma-separated piece is a known key in `ACCTS`. On match, set
  a new array `multi_accounts=(...)` (split on comma) instead of the
  scalar `$account`, and remember the argv position so the rest of the
  parse loop treats this arg as "consumed" the same way a single alias
  would (i.e., don't let it fall through to `rest`).
  - If a comma-list has any unknown piece (typo, e.g. `h,gg`), fail loudly
    with the specific bad token named, rather than silently treating the
    whole thing as an unrecognized positional (which today would produce
    a confusing downstream error). Reuses the spirit of the existing
    "unknown action" guard (~line 2356-2371).
- Verify: `m h,bogus i` errors with something like `m: unknown account
  alias 'bogus' in 'h,bogus'` and does not proceed. `m h,g i` (both valid)
  populates `multi_accounts=(h g)` and nothing else changes yet.

### 2. Self-invocation loop, gated right after parsing/validation

- Files: `bash/m`
- What: Immediately after `multi_accounts` is populated (still early,
  before the single-account resolution block at ~line 2395 `action="${action:-i}"`
  and the `ACCTS[$account]` lookup at ~line 2429), branch: if
  `multi_accounts` is non-empty, loop over it. For each alias:
  - Print a header line to stderr identifying which account this chunk of
    output belongs to (e.g. `log_info "=== $alias (${LABELS[$alias]:-$alias}) ==="`),
    so output from different accounts is visually separable.
  - Re-invoke `"$0"` with the original argv, but with the comma-list arg
    replaced by just this one alias. (Reconstruct argv by walking the
    original `$@`/`args` array and substituting at the position recorded
    in step 1 -- do not try to reconstruct from `$rest`, which has already
    been mutated by flag-stripping earlier in the loop.)
  - Track the exit code of each sub-invocation; continue to the next
    account even if one fails (don't let one bad account abort the whole
    batch), but remember the worst (non-zero) code.
  - After the loop, `exit` with that worst code.
  - This whole block replaces (short-circuits before) the normal
    single-account `case "$action" in ...` dispatch -- multi-account mode
    never reaches the existing dispatch code at all; each recursive child
    invocation does, exactly once, exactly as it does today.
- Verify: `m h,g i` prints two labeled sections, one per account, each
  looking identical to running `m h i` / `m g i` separately. `m h,g,cu meets`
  prints three labeled sections. Exit code of `m h,bogus-cache-state i`
  (where one account's auth is broken) is non-zero even if the other
  account succeeds.

### 3. Safety gate for mutating/sending actions

- Files: `bash/m`
- What: Actions that send or destroy mail (`send`, `c`, `reply`,
  `reply-all`, `fwd`, `draft`, `trash`, `archive`, `sfwd`, `sreply`,
  `sreply-all`) should not silently fan out to N accounts from one typed
  command -- firing the same send/reply/trash from 3 mailboxes because the
  user habitually types `h,g` is a plausible real mistake, not a feature.
  Add a check: if `multi_accounts` is set AND `$action` is in that list,
  refuse with a clear message ("multi-account is for read-only actions;
  run each send/reply separately") rather than proceeding. Read-only
  actions (`i`, `sent`, `q`, `urls`, `meets`, `x`, `d`) are unrestricted.
- Verify: `m h,g send someone@example.com` errors before doing anything.
  `m h,g i` still works.

### 4. Update help text

- Files: `bash/m` (the `usage()` function, both the `basic` and `actions`
  topics, and the "Account aliases" line in the `§ PUBLIC API` header
  comment at the top of the file)
- What: Document the new `h,g` / `h,g,cu` syntax with one example each in
  the basic usage block and the advanced-workflows examples, and note the
  read-only restriction from step 3.
- Verify: `m --help` and `m --help=actions` show the new syntax.

## Risks

- Recursive self-invocation correctness: `"$0"` must resolve to the same
  script reliably regardless of how `m` was invoked (alias, full path,
  PATH lookup). `SCRIPT_DIR="$(dirname "$(realpath "$0")")"` already at
  the top of the file confirms `$0` resolves correctly today; reusing
  `$0` directly (not `$SCRIPT_DIR/m`, which would be redundant) for the
  recursive call is the simplest correct choice. Verify explicitly by
  invoking `m` via its normal PATH alias, not just `./m`, during testing.
- Reconstructing argv for the recursive call: the comma-list token's
  position in the original `$@` must be tracked precisely so substitution
  doesn't reorder or drop other flags (e.g. `-w`, `--outbox`). Safer to
  keep a copy of the untouched original `args=("$@")` array (already
  captured at the top of the parse loop) and rebuild from that, not from
  any partially-processed intermediate.
- Interactive actions across accounts: `meets`'s "open which?" prompt will
  fire once per account in the loop (each recursive `m` call is a full
  run, including its own prompt). That's arguably correct (each account's
  menu is genuinely a different set of choices) but should be called out
  to the user during testing as expected behavior, not a bug.
- Failure isolation: one account's OAuth token being expired/broken must
  not abort the whole batch (see step 2's "continue on failure, track
  worst exit code" requirement) -- otherwise `m h,g,cu i` becomes
  all-or-nothing and less useful than running them separately.
- `set -euo pipefail` interaction: the script runs under `set -e`. Calling
  the recursive sub-invocations naively (`"$0" ... || true` per-iteration,
  capturing `$?` explicitly) is required so one non-zero exit doesn't kill
  the parent loop early under `-e`. Must test this specifically, it's an
  easy mistake.

## Out of Scope

- True parallel/concurrent execution across accounts (see Considered and
  Rejected #4). Sequential only, for now.
- Any change to `gmail-api-rw` (the Python backend). This is entirely a
  `bash/m` frontend change.
- Deduplicating aliases that point at the same mailbox (`m h,hNY i`
  running the hackNY account twice). Not harmful, not worth the added
  complexity of detecting it, and arguably the user's call.
- A shorthand for "all configured accounts" (e.g. `m all i` or `m * i`).
  Out of scope for this plan; the ask was specifically comma-lists of
  explicit aliases. Could be a fast follow (`all` expanding to every key
  in `ACCTS`) but is a separate decision or feature, not folded in here.
- Retrofitting the earlier `meets`-specific cross-account idea from
  `/enhance` as a separate code path. Once this plan ships, `m h,g,cu
  meets` supersedes it -- no `meets`-specific multi-account code is
  needed.
