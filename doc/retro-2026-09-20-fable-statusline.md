# Retro: Fable quota statusline, 2026-09-20

Scope: this covers one session, the Fable warning. The repo-wide retro.md in the
mise root is from 2026-09-05 and describes the tcsh2bash migration; it was left
alone.

## What went well

The verification discipline paid for itself, twice. The docs lookup for the
statusline contract went to a subagent rather than being guessed from training,
and it came back with a fact I would not have invented: the payload carries
`rate_limits.five_hour` and `rate_limits.seven_day`. That turned the deliverable
from "says FABLE" into "says FABLE and shows you 63% of your five-hour window is
gone", which is the half that actually stops you running out.

The second payoff was refusing to believe an exit code. `tc -t 002 red` returned
0 and I could have reported a red titlebar on that basis. Screenshotting instead
showed the only changed pixels were the menu-bar clock. Your own CLAUDE.md rule
(a command exiting 0 without doing anything is a diagnosis) is what caught it,
and the rule earned its keep here.

I also did not ship the broken half. The tab-color hook was written, linted, and
stdin-tested before the pixel check killed it; withdrawing it was better than
leaving a no-op wired into settings.json where it would have read as working.

## Where this session was weak

The real cost was ordering. I built the tab-color hook completely, including
shellcheck and stdin tests, before testing whether the underlying mechanism did
anything at all. One `tc -t <tty> red` against a Claude window plus a screenshot
would have taken two calls and killed the approach before any code existed. I
wrote a script to drive a mechanism I had never confirmed worked. Map before
moving, in your terms, and I moved first.

Then the pixel verification itself cost about eight calls because I kept
chasing window geometry: AppleScript bounds, a crop that showed the wrong
window, a focus attempt using the wrong numbering scheme, a Quartz import that
does not exist in that interpreter. The thing that finally settled it was the
simplest possible experiment, and one I could have run at the start: apply the
color to a window I KNOW is a plain shell, and diff. When a mechanism's
viability is in question, test it on the case most likely to succeed before
testing it on the case you care about. A negative on the hard case alone cannot
distinguish "mechanism is broken" from "my targeting is wrong", which is exactly
the ambiguity I spent those calls in.

Third, smaller: the screenshot work belonged in a subagent. Each full-screen
capture plus crop plus a returned image is expensive context, and the conclusion
I kept was one line. Your CLAUDE.md already says screenshot-heavy work is the
silent context killer.

## Playbook

Chris: run /push in /Users/wiggins/mise to commit bash/claude-statusline. It is
untracked and every new session already runs it, so right now a live piece of
your harness exists in no commit. This is doc/NEXT.md item G.

Chris: decide whether you want the background-window version (doc/NEXT.md item
H). The statusline only shows in the window you are looking at, so a Fable
session in one of your other eleven windows still says nothing. The tab-title
route can be built and verified; it needs your go-ahead, not more investigation.

Claude (encoded at /Users/wiggins/.claude/CLAUDE.md, the paragraph beginning
"`tc` CANNOT COLOR A WINDOW THAT IS RUNNING CLAUDE"): tc writes an OSC escape to
a tty, so it is inert against a window running the Claude TUI and exits 0 while
failing. The same paragraph records the two traps that cost calls here: a diff
bbox of a few dozen pixels is the menu-bar clock rather than your change, and an
occluded window screenshots as whatever covers it.

Claude (judgment, not encodable): confirm a mechanism works before writing the
code that depends on it, and when testing viability, run the case most likely to
succeed first so a negative is interpretable. This is general enough that adding
it to CLAUDE.md would dilute rather than sharpen the file, and specific enough
that the tc paragraph above already carries the instance.
