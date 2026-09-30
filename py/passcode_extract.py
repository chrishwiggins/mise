"""passcode_extract: pull a one-time passcode out of an email, deterministically.

Shared by the `passcode-extract` CLI and gmail-api-rw (`m code`, `m code-add`).
Stdlib only. No guessing: rules run in order, the first rule that finds exactly
one distinct candidate wins, and a rule that finds several stops the search as
AMBIGUOUS so the caller can refuse rather than print a wrong code.

Rules, in order:
  label-line  a label line ("Your verification code is:") followed by a line
              holding one 4-10 char alphanumeric token with a digit (JAGGAER)
  inline      "passcode(s): X", "code is X", "X is your ... code" on one line
              of the body (Google Voice SMS forwards)
  subject     the inline rules applied to the Subject header
  lone-number exactly one plausible 4-8 digit number left in the body after
              dropping URLs, dates, times, phone numbers, years and zip codes,
              and only when the message mentions a code, verifying or signing in
"""

import html
import re
from email import message_from_bytes, policy

_LABEL = r"(?:pass\s*codes?|codes?|pins?|otps?|one[- ]time\s+(?:pass(?:word|code)|code))"
# A passcode token: 4-10 letters/digits containing at least one digit.
_TOKEN = r"(?=[A-Za-z0-9]*\d)[A-Za-z0-9]{4,10}"

_LABEL_LINE = re.compile(rf"\b{_LABEL}\b[^\n]{{0,20}}?(?:\bis\b)?\s*:?\s*$", re.I)
_STANDALONE = re.compile(rf"^\s*({_TOKEN})\s*[.]?\s*$")
_INLINE = [
    # "SMS passcodes: 1996144", "code: 123456", "code is 123456", "code is: 1234"
    re.compile(rf"\b{_LABEL}\b[ \t]*(?:is[ \t]*)?[:\-]?[ \t]*\b({_TOKEN})\b", re.I),
    # "123456 is your verification code"
    re.compile(rf"\b({_TOKEN})\b[ \t]+is[ \t]+your\b[^\n.]{{0,40}}?\b{_LABEL}\b", re.I),
]
_URL = re.compile(r"(?:https?://|www\.)\S+|<[^>\s]*[/@][^>\s]*>", re.I)
_NUMBER = re.compile(r"(?<![\w./:\-+#$])(\d{4,8})(?![\w/:\-]|\.\d)")
_ZIP = re.compile(r"\b[A-Z]{2}\s+(\d{5})\b")
_YEAR = re.compile(r"^(?:19|20)\d\d$")
# Sign-in context that licenses the lone-number rule.
_CONTEXT = re.compile(
    rf"\b(?:{_LABEL}|verif(?:y|ication)|sign(?:ing)?[ -]?in|log(?:ging)?[ -]?in|"
    r"authenticat\w*|two[- ]factor|2fa|mfa)\b", re.I)
# Words that pass _TOKEN's shape but are never codes.
_NOT_CODES = {"2fa", "mp3", "mp4", "utf8", "x264"}


class Result:
    """Outcome of an extraction: code (or None), the rule that decided, all candidates."""

    def __init__(self, code=None, rule=None, candidates=()):
        self.code = code
        self.rule = rule
        self.candidates = list(candidates)

    @property
    def ambiguous(self):
        return self.code is None and len(self.candidates) > 1

    def __repr__(self):
        return f"Result(code={self.code!r}, rule={self.rule!r}, candidates={self.candidates!r})"


def _html_to_text(s):
    s = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", s)
    s = re.sub(r"(?i)<br\s*/?>|</(p|div|tr|li|h\d|td|table)>", "\n", s)
    s = re.sub(r"<[^>]+>", " ", s)
    return html.unescape(s)


def message_parts(raw):
    """(subject, body_text) from raw RFC 822 bytes; text/plain preferred over HTML."""
    msg = message_from_bytes(raw, policy=policy.default)
    subject = str(msg.get("Subject", "") or "")
    plain, rich = [], []
    for part in msg.walk():
        if part.is_multipart() or part.get_content_disposition() == "attachment":
            continue
        ctype = part.get_content_type()
        if ctype not in ("text/plain", "text/html"):
            continue
        try:
            text = part.get_content()
        except (LookupError, UnicodeDecodeError):
            payload = part.get_payload(decode=True) or b""
            text = payload.decode("utf-8", "replace")
        (plain if ctype == "text/plain" else rich).append(text)
    if plain:
        body = "\n".join(plain)
    else:
        body = "\n".join(_html_to_text(t) for t in rich)
    return subject, body


def _distinct(tokens):
    seen = []
    for t in tokens:
        if t.lower() in _NOT_CODES:
            continue
        if t not in seen:
            seen.append(t)
    return seen


def _decide(rule, tokens):
    found = _distinct(tokens)
    if len(found) == 1:
        return Result(found[0], rule, found)
    if found:
        return Result(None, rule, found)
    return None


def _label_line(body):
    lines = body.splitlines()
    hits = []
    for i, line in enumerate(lines):
        if not _LABEL_LINE.search(line):
            continue
        for nxt in lines[i + 1:i + 4]:
            if not nxt.strip():
                continue
            m = _STANDALONE.match(nxt)
            if m:
                hits.append(m.group(1))
            break
    return hits


def _inline(text):
    hits = []
    for line in text.splitlines():
        for rx in _INLINE:
            hits.extend(m.group(1) for m in rx.finditer(line))
    return hits


def _lone_number(subject, body):
    # A bare number is only a passcode when the message is about signing in.
    # Without this gate a newsletter's street number reads as a code.
    if not _CONTEXT.search(subject) and not _CONTEXT.search(body):
        return []
    text = _URL.sub(" ", body)
    zips = set(_ZIP.findall(text))
    nums = []
    for m in _NUMBER.finditer(text):
        n = m.group(1)
        if n in zips or (len(n) == 4 and _YEAR.match(n)):
            continue
        nums.append(n)
    return nums


def extract_text(subject, body):
    """Apply the rules to an already-decoded subject and body."""
    for rule, tokens in (("label-line", lambda: _label_line(body)),
                         ("inline", lambda: _inline(body)),
                         ("subject", lambda: _inline(subject)),
                         ("lone-number", lambda: _lone_number(subject, body))):
        r = _decide(rule, tokens())
        if r is not None:
            return r
    return Result()


def extract(raw):
    """Extract a passcode from raw RFC 822 bytes. Returns a Result."""
    subject, body = message_parts(raw)
    return extract_text(subject, body)
