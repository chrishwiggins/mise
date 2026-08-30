# txt2doc / md2doc - Google Doc creation tools

Two tools turn a local file into a Google Doc and optionally share it.

| Tool | Auth backend | Conversion | Status |
|------|-------------|------------|--------|
| `txt2doc` | `gws` CLI + OS keyring | Drive upload-convert (native, real formatting) | preferred |
| `md2doc` | standalone OAuth (`~/.config/thoughtgun/token.json`) | regex batch-update | legacy |

## txt2doc usage

```
txt2doc notes.md # create doc, print URL
txt2doc notes.md alice@x.com # share alice as editor (writer)
txt2doc notes.md alice@x.com bob@y.com # both editors
txt2doc notes.md -c carol@x.com # commenter
txt2doc notes.md -v dave@x.com # viewer
txt2doc notes.md -t "My Title" # override title
txt2doc notes.md alice@x.com -n # also email alice the share notice
```

By default no notification email is sent (you hand over the URL yourself); pass
`-n`/`--notify` to have Drive email each recipient.

Positional emails default to **editor**. Source `.md/.txt/.html` is uploaded
with the matching MIME type and Drive converts it to a native Doc.

## Account

txt2doc rides on whatever account `gws` is logged in as. The default account is
**chris.wiggins@gmail.com**.

## Required gws scopes

txt2doc needs exactly two OAuth scopes:

- `https://www.googleapis.com/auth/drive.file` (create + share its own files)
- `https://www.googleapis.com/auth/documents` (Docs API)

Log in non-interactively (skips the confusing scope picker):

```
gws auth login --scopes https://www.googleapis.com/auth/drive.file,https://www.googleapis.com/auth/documents
```

Sign in as chris.wiggins@gmail.com and leave BOTH consent boxes checked.

## OAuth project

The gws OAuth client lives in GCP project **gcalcli20220904t09h51m28s**
(client_id `64761076517-...`). The Drive and Docs APIs MUST be enabled there:

```
gcloud services enable drive.googleapis.com docs.googleapis.com --project=gcalcli20220904t09h51m28s
gcloud services list --enabled --project=gcalcli20220904t09h51m28s | grep -E 'drive|docs'
```

(Note: gcloud's *active* project may differ, e.g. `zeroshot-runner`. Always
pass `--project=gcalcli20220904t09h51m28s` explicitly.)

## Debugging 403 "insufficient authentication scopes"

This error has THREE independent causes. Check in this order:

1. **Stale token cache (most common).** gws caches access tokens at
   `~/.config/gws/token_cache.json` (and `cache/`). After re-logging-in with new
   scopes, gws may keep serving the OLD cached token. Symptom: `auth status`
   shows the right scopes, `docs documents create` works, but `drive files
   create` 403s. Fix:
   ```
   rm -f ~/.config/gws/token_cache.json; rm -rf ~/.config/gws/cache/*
   ```
   Next call re-mints from the refresh token.

2. **API not enabled on the OAuth project.** Token has the scope but the project
   can't call the API. Fix with the `gcloud services enable` above (propagation
   can take a minute or two).

3. **Wrong scope granted at consent.** The gws scope picker preselects
   `drive.readonly` + `drive.file` and is easy to mis-toggle. `auth status`
   reports REQUESTED scopes, not GRANTED ones, so they can disagree. Use the
   non-interactive `--scopes` login above to bypass the picker entirely.

Note: `drive about get` legitimately requires broad `drive` scope and WILL 403
under `drive.file`. That is not a bug; do not use it as a scope-health probe.
Use `drive files create` (which `drive.file` permits) instead.

## gws gotchas

- `--upload` is sandboxed to the current directory. txt2doc copies the source to
  a temp file in cwd before uploading, then removes it.
- gws prints `Using keyring backend: keyring` to stdout before JSON; strip
  everything before the first `{` when parsing.

## md2doc (legacy) fix

md2doc used to crash with `Error: invalid_grant: Token has been expired or
revoked` when its refresh token died. Patched: a `RefreshError` now falls back
to a fresh browser login instead of erroring (`~/mise/py/md2doc`).
