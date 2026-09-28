"""fname_norm: shell-safe filename normalization shared by unspace-mvit and gmail-api-rw.

One copy on purpose: the file renamer and the mail attachment saver must agree
on what a clean name is, and two copies of a regex drift.

normalize_basename(name) operates on a single path component (no directory):
  - strips [bracketed] segments (YouTube ids and the like)
  - replaces whitespace, punctuation and shell-hostile characters with `_`
  - collapses runs of `_` and trims them from both ends
  - keeps `.` inside the stem, and keeps the extension as-is unless it
    itself contains a character from the replaced set
  - never returns an empty stem: `[id].mp4` becomes `file.mp4`, not `.mp4`
  - leaves a real dotfile (`.DS_Store`) alone, but never MAKES a name hidden
"""
import os
import re

BRACKET_PATTERN = re.compile(r"\[[^]]*\]")
# Whitespace, dashes, brackets, quotes (straight and curly), full-width colon
# and bar, plus the shell-hostile set: & ; ! ? $ # * < > { } \ ` / ~ ^ = + %
# and @. `/` matters for mail: a sender-chosen name like `../x` must not
# become a path.
PUNCT_PATTERN = re.compile(
    r"[,\s\-\[\]\(\)'\"\u2018\u2019\u201c\u201d\uff1a:\uff5c|&;!?$#*<>{}\\`/~^=+%@]+"
)


def _clean(s):
    s = PUNCT_PATTERN.sub("_", s)
    s = re.sub(r"_+", "_", s)
    return s.strip("_")


def normalize_basename(name, placeholder="file"):
    """Return a shell-safe version of one filename component."""
    # A sender-supplied name can carry a path (`../../x.txt`). Keep the
    # segments as words but drop the `.`/`..` ones rather than turning them
    # into `.._.._x.txt`.
    name = "_".join(s for s in re.split(r"[/\\]", name) if s not in ("", ".", ".."))
    was_hidden = name.startswith(".")
    # splitext treats a whole dotfile name as the stem, so `.DS_Store` has
    # root `.DS_Store` and no extension and survives unchanged below.
    root, ext = os.path.splitext(name)
    root = _clean(BRACKET_PATTERN.sub("", root))
    if not was_hidden:
        # Normalizing must not produce a hidden file (`_.pdf` trimmed to
        # `.pdf`), nor `.`/`..`.
        root = root.lstrip(".")
    if root in ("", ".", ".."):
        root = placeholder
    if ext and PUNCT_PATTERN.search(ext[1:]):
        cleaned = _clean(ext[1:])
        ext = f".{cleaned}" if cleaned else ""
    return f"{root}{ext}"
