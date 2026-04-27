# m - Multi-Account Email Dispatcher

A unified command-line interface for managing multiple email accounts with intelligent routing between Gmail API and SMTP backends.

## Quick Start

```bash
# Install
ln -s ~/mise/bash/m /usr/local/bin/m # or add ~/mise/bash to PATH

# Setup configuration
mkdir -p ~/.config/mail-tools
cat > ~/.config/mail-tools/accounts.json << 'EOF'
{
  "accounts": {
    "g": {
      "email": "your.main@gmail.com",
      "muttrc": "/path/to/gmail.muttrc",
      "chrome_profile": "Default"
    },
    "w": {
      "email": "work@company.com",
      "muttrc": "/dev/null",
      "chrome_profile": "Work"
    }
  },
  "default_account": "g"
}
EOF

# Basic usage
m # Inbox for default account
m w # Work account inbox
m send user@example.com # Compose email
m -q project reply # Search "project", reply to first result
```

## Core Concepts

### Account Abstraction
- Accounts are referenced by single letters (`g`, `w`, `u`)
- Each account maps to an email address and transport configuration
- Automatic routing: API accounts use Gmail API, others use SMTP

### Transport Detection
- `"muttrc": "/dev/null"` → Gmail API (OAuth, faster, better threading)
- `"muttrc": "/path/to/file"` → SMTP (via neomutt, works with any provider)

### Mode Consistency
All read actions support consistent flags:
- Default: Display with `more` paging
- `-save`: Download to `.eml` file
- `-v`: Show full content without paging

## Configuration

### Required: Account Configuration File

Create `~/.config/mail-tools/accounts.json`:

```json
{
  "accounts": {
    "g": {
      "email": "personal@gmail.com",
      "muttrc": "/Users/you/.config/mutt/gmail",
      "chrome_profile": "Default"
    },
    "w": {
      "email": "work@company.com",
      "muttrc": "/dev/null",
      "chrome_profile": "Work"
    }
  },
  "default_account": "g"
}
```

### Account Configuration Fields

- **email**: The email address for this account
- **muttrc**: Path to neomutt config, or `/dev/null` for Gmail API
- **chrome_profile**: Chrome profile name for web interface

### SMTP Setup (muttrc ≠ "/dev/null")

For SMTP accounts, create a neomutt configuration file:

```bash
# ~/.config/mutt/gmail
set from = "your@gmail.com"
set realname = "Your Name"
set smtp_url = "smtps://your@gmail.com@smtp.gmail.com:465/"
set smtp_pass = "your-app-password"
```

### Gmail API Setup (muttrc = "/dev/null")

For API accounts:
1. Enable Gmail API in Google Cloud Console
2. Download credentials to `~/.config/google/credentials.json`
3. Install dependencies: `pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client`

## Usage

### Basic Commands

```bash
m # Default account inbox
m w # Work account inbox
m sent # Sent messages (default account)
m w sent # Work account sent messages
m drafts # Draft messages
m spam # Spam folder
```

### Reading Messages

```bash
m 5 # Read message #5 (with paging)
m 5 -v # Read message #5 (full content, no paging)
m 5 -save # Download message #5 to .eml file
m 1-5 # Read messages 1 through 5
m sent 3 # Read sent message #3
```

### Searching

```bash
m -q alice # Search for "alice"
m -q "from:bob" # Gmail search syntax
m -q project 2 # Search "project", read result #2
m -q urgent reply # Search "urgent", reply to first result
m w -q meeting # Search work account for "meeting"
```

### Composing and Sending

```bash
m send user@example.com # Compose new email
m send -s "Subject" user@example.com # With subject
echo "Body" | m send -s "Hi" user@ex # With body via stdin
m w send user@company.com # Send from work account
```

### Interactive Actions

```bash
m 3 reply # Reply to message #3
m 3 reply-all # Reply-all to message #3
m 3 fwd user@ex.com # Forward message #3
m 3 draft # Save message #3 as draft
m -q project fwd # Search "project", forward first result
```

### Web Interface

```bash
m -w # Open default account in browser
m w -w # Open work account in browser
m -w -q "from:alice" # Search in web Gmail
```

### URL Extraction

```bash
m urls # Extract URLs from newest message
m 5 urls # Extract URLs from message #5
m -q meeting urls # Search "meeting", extract URLs from first result
```

## Advanced Usage

### Account Switching Mid-Composition

When composing, you can edit the From: header to switch accounts:

```bash
m send user@example.com
# Editor opens with:
# From: personal@gmail.com <- Edit this line
# To: user@example.com
# Subject:
#
# # Available accounts:
# # g: personal@gmail.com
# # w: work@company.com
```

Change the From line to switch which account sends the email.

### Batch Operations

```bash
m 1-10 -save # Download messages 1-10 to files
m -q "label:urgent" 1-5 # Search urgent, read first 5 results
m sent 1-3 -v # Show sent messages 1-3 without paging
```

### Caching

Message listings are cached for 30 seconds to improve performance:

```bash
m # Cached if within 30s
m -N # Force refresh, bypass cache
```

## Workflow Patterns

### Daily Email Triage

```bash
m # Check default inbox
m w # Check work inbox
m -q "is:unread" 1-5 # Read first 5 unread messages
```

### Project Communication

```bash
m -q "project-alpha" # Find project emails
m -q "project-alpha" reply # Reply to newest
m send -s "Update" team@company.com # Send update
```

### Account-Specific Tasks

```bash
m w -q "budget" # Search work emails for budget
m send -s "Personal" friend@example.com # Personal email
m w send -s "Work" colleague@company.com # Work email
```

## Troubleshooting

### Configuration Issues

```bash
# Test configuration loading
m --help=accounts # Shows configured accounts

# Common config problems
ls ~/.config/mail-tools/accounts.json # File exists?
jq '.' ~/.config/mail-tools/accounts.json # Valid JSON?
```

### SMTP Authentication

```bash
# Test neomutt config
neomutt -F ~/.config/mutt/gmail -s "Test" yourself@example.com
```

### Gmail API Issues

```bash
# Check credentials
ls ~/.config/google/credentials.json

# Test Gmail API access
python3 -c "
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import pickle, os
if os.path.exists('token.pickle'):
    print('API credentials found')
else:
    print('Run Gmail API authentication')
"
```

### Performance

```bash
# Clear cache if stale
rm /tmp/spool/.gmails-last-listing-*.txt

# Bypass cache for fresh data
m -N
```

## Integration

### Shell Aliases

```bash
# Add to ~/.bashrc or ~/.zshrc
alias mi="m" # Shorter command
alias mw="m w" # Quick work account
alias ms="m send" # Quick compose
alias mq="m -q" # Quick search
```

### Scripts and Automation

```bash
#!/bin/bash
# daily-email-check.sh
echo "=== Personal Inbox ==="
m -q "is:unread" | head -5

echo "=== Work Inbox ==="
m w -q "is:unread" | head -5
```

## Dependencies

### Required

- **bash** 4.0+ (for associative arrays)
- **jq** (JSON config parsing)
- **neomutt** (for SMTP accounts)

### Optional

- **gdate** (GNU date, for precise timestamps on macOS)
- **chrome/brave** (for web interface)
- **Python 3 + Google API libraries** (for Gmail API accounts)

## Security Model

- **No PII in code**: All email addresses stored in external config
- **OAuth tokens**: Managed by Google libraries, not exposed
- **SMTP passwords**: Stored in neomutt config files (user responsibility)
- **Multi-account**: Each Chrome profile isolated for security

## Performance

- **Caching**: 30-second TTL for message listings
- **Lazy loading**: Only fetches messages when needed
- **API efficiency**: Gmail API preferred for speed and reliability
- **Smart routing**: Automatic backend selection per account

## License

See ~/mise/LICENSE or parent project license.