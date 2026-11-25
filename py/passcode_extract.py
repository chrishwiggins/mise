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
              and only when a code, verifying or signing in is mentioned within
              two non-blank lines of it; when several are left, the single one
              alone on its own line wins

Refused before any rule: a sale (checkout, redeem, "% off", promo code) with
no sign-in word anywhere. The inline rules skip a label right after an
address or discount word ("Mail Code 2808", "promo code BF55").
"""

import html
import re
from email import message_from_bytes, policy

_LABEL = r"(?:pass\s*codes?|codes?|pins?|otps?|one[- ]time\s+(?:pass(?:word|code)|code))"
# A passcode token: 4-10 letters/digits containing at least one digit.
_TOKEN = r"(?=[A-Za-z0-9]*\d)[A-Za-z0-9]{4,10}"

_LABEL_LINE = re.compile(rf"\b{_LABEL}\b[^\n]{{0,20}}?(?:\bis\b)?\s*:?\s*$", re.I)
_LABEL_WORD = re.compile(rf"\b{_LABEL}\b", re.I)
_STANDALONE = re.compile(rf"^\s*({_TOKEN})\s*[.]?\s*$")
_INLINE = [
    # "SMS passcodes: 1996144", "code: 123456", "code is 123456", "code is: 1234"
    re.compile(rf"\b{_LABEL}\b[ \t]*(?:is[ \t]*)?[:\-]?[ \t]*\b({_TOKEN})\b", re.I),
    # "123456 is your verification code"
    re.compile(rf"\b({_TOKEN})\b[ \t]+is[ \t]+your\b[^\n.]{{0,40}}?\b{_LABEL}\b", re.I),
]
_URL = re.compile(r"(?:https?://|www\.)\S+|<[^>\s]*[/@][^>\s]*>", re.I)
_NUMBER = re.compile(r"(?<![\w./:\-+#$])(\d{4,8})(?![\w/:\-]|\.\d)")
_ALONE_LINE = re.compile(r"(?m)^[^\S\n]*(\d{4,8})[^\S\n]*$")
_ZIP = re.compile(r"\b[A-Z]{2},?\s+(\d{5})\b")
# How many non-blank lines from a lone number a sign-in word may sit.
_NEAR = 2
# "Mail Code 2808", "promo code BF55": the word before the label says the
# token is an address or a discount, not a passcode.
_NOT_AUTH_BEFORE = re.compile(
    r"\b(?:mail|promo(?:tional)?|coupon|discount|gift|referral|voucher|zip|"
    r"postal|area|country|offer)\s*$", re.I)
# What precedes a lone number that is an address, an id or a card tail:
# "Mail Code 2808", "P.O. Box 40770", "Member ID: 60025276", "Amex .... 9002".
_NOT_LONE_BEFORE = re.compile(
    r"(?:\b(?:(?:mail|zip|postal|area)\s+code|box|suite|room|apt|unit|ext|"
    r"id|account|acct|member|ending\s+in)\s*[:#.]?|[.*•xX]{3,})\s*$", re.I)
# A sale: these words with no sign-in word anywhere mean every "code" in the
# message is a discount ("Use code BF55 at checkout").
_COMMERCE = re.compile(
    r"\b(?:checkout|redeem|promo(?:tional)?\s+code|coupon|discount)\b|"
    r"\d+\s*%\s*off\b|\$\d+\s*off\b", re.I)
_AUTH = re.compile(
    r"\b(?:verif(?:y|ication)|sign(?:ing)?[ -]?in|log(?:ging)?[ -]?in|"
    r"pass\s*codes?|one[- ]time|otp|2fa|mfa|two[- ]factor|authenticat\w*|"
    r"authoriz\w*|security\s+code|confirm\w*)\b", re.I)
_YEAR = re.compile(r"^(?:19|20)\d\d$")
# A street number: "4600 East Washington Street", "1600 Main St", "12 W 4th".
_STREET_AFTER = re.compile(
    r"\s+(?:(?:north|south|east|west|[NSEW]\.?)\b|"
    r"[A-Za-z]+\s+(?:st|street|ave|avenue|rd|road|blvd|boulevard|dr|drive|"
    r"ln|lane|way|pl|place|pkwy|parkway|ct|court)\b)", re.I)
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
        # A wrapped sentence puts the label and the colon on different lines:
        # "use the following code to enable your device, it will expire in 30"
        # / "minutes:" / "276a65" (Namecheap). A colon-ended line then counts
        # when the label sits in it or in either of the two lines before it.
        wrapped = (line.rstrip().endswith(":") and
                   _LABEL_WORD.search(" ".join(lines[max(0, i - 2):i + 1])))
        if not (_LABEL_LINE.search(line) or wrapped):
            continue
        # The first NON-BLANK line after the label; HTML-to-text can leave a
        # dozen whitespace-only lines between them, so blanks do not count.
        for nxt in lines[i + 1:i + 30]:
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
        # "Use code BF55 at checkout" in a mail that also says "sign in" in
        # its footer: the line itself says sale.
        if _COMMERCE.search(line):
            continue
        for rx in _INLINE:
            for m in rx.finditer(line):
                if _NOT_AUTH_BEFORE.search(line[:m.start()]):
                    continue
                hits.append(m.group(1))
    return hits


def _is_sale(subject, body):
    text = subject + "\n" + _URL.sub(" ", body)
    return bool(_COMMERCE.search(text)) and not _AUTH.search(text)


def _near_context(text, pos):
    """True when a sign-in word sits on the number's line or within
    _NEAR non-blank lines of it. A footer's account or member number
    ("537048" under a Fidelity address) is far from any such word."""
    lines = text.splitlines()
    row = text.count("\n", 0, pos)
    # Index of each non-blank line, so blank runs between label and code
    # (HTML-to-text leaves many) do not count as distance.
    filled = [i for i, ln in enumerate(lines) if ln.strip()]
    if row not in filled:
        return False
    k = filled.index(row)
    window = filled[max(0, k - _NEAR):k + _NEAR + 1]
    return any(_CONTEXT.search(lines[i]) for i in window)


def _lone_number(subject, body):
    # A bare number is only a passcode when the message is about signing in.
    # Without this gate a newsletter's street number reads as a code. URLs go
    # first: a "login.aspx?u=60025276" link is not the message talking about
    # signing in.
    text = _URL.sub(" ", body)
    if not _CONTEXT.search(subject) and not _CONTEXT.search(text):
        return []
    zips = set(_ZIP.findall(text))
    nums = []
    for m in _NUMBER.finditer(text):
        n = m.group(1)
        if n in zips or (len(n) == 4 and _YEAR.match(n)):
            continue
        if _STREET_AFTER.match(text, m.end()):
            continue
        line_start = text.rfind("\n", 0, m.start()) + 1
        if _NOT_LONE_BEFORE.search(text[line_start:m.start()]):
            continue
        if not _near_context(text, m.start()):
            continue
        nums.append(n)
    # A candidate alone on its own line outranks numbers buried in prose: the
    # code is set off by itself while the footer carries phone-number groups
    # ("0800 014 7539") and a zip after a spelled-out state (Viking).
    alone = set(_ALONE_LINE.findall(text))
    set_off = [n for n in nums if n in alone]
    if len(_distinct(set_off)) == 1:
        return set_off
    return nums


def extract_text(subject, body):
    """Apply the rules to an already-decoded subject and body."""
    if _is_sale(subject, body):
        return Result()
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
