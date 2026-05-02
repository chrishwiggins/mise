# m - Multi-Account Email Dispatcher

A unified command-line interface for managing multiple email accounts with intelligent routing between Gmail API and SMTP backends. All email functionality consolidated into a single script with comprehensive helper utilities.

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
m 1-5 -p # Save messages 1-5 and invoke /peek (Claude Code integration)
m sent 3 # Read sent message #3
```

### Claude Code Integration

The `-p/--peek` flag enables seamless integration with Claude Code:

```bash
m 3 -p # Save message #3 and automatically run: claude /peek <file>
m -q "from:alice" 2 -p # Search for alice, peek at result #2
m u -q "urgent" 1-3 -p # Save multiple messages for batch analysis
```

This saves messages to `/tmp/spool/` and automatically invokes Claude Code's `/peek` skill for AI-powered email analysis.

### Searching and Pagination

```bash
m -q alice # Search for "alice"
m -q "from:bob" # Gmail search syntax
m -q project 2 # Search "project", read result #2
m -q urgent reply # Search "urgent", reply to first result
m w -q meeting # Search work account for "meeting"

# Pagination support
m pp2 # Show page 2 of inbox (messages 21-40)
m pp3 # Show page 3 of inbox (messages 41-60)
m -q "from:alice" pp2 # Search results pagination
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
- **Email blocking hooks**: Claude Code integration prevents accidental sending
- **Credential protection**: Config files in `~/.config/` protected by allowlist git repo

### Email Blocking System

Claude Code integration includes protective hooks to prevent accidental email sending:

- **Hook location**: `~/.claude/hooks/block-email-send.sh`
- **Patterns blocked**: `gmail-api-rw send`, `m send`, direct mutt calls with recipients
- **Override**: Use `! command` prefix to bypass protection when intentional
- **Purpose**: Prevents AI from sending emails without explicit user confirmation

### Configuration Security

Email configuration follows secure patterns:

- **Config location**: `~/.config/mail-tools/accounts.json` (outside code repo)
- **Credential isolation**: SMTP passwords in separate neomutt files
- **OAuth separation**: Gmail API tokens managed independently
- **Backup strategy**: Config backed up separately from credentials

## Performance

- **Caching**: 30-second TTL for message listings
- **Lazy loading**: Only fetches messages when needed
- **API efficiency**: Gmail API preferred for speed and reliability
- **Smart routing**: Automatic backend selection per account

## Code Organization (For Future Maintainers)

### Directory Structure

```
~/mise/
├── bash/
│ └── m # Main email dispatcher script
├── aux/
│ └── m/ # All m-support utilities
│ ├── m-install # Installation helper
│ └── m-config.bash # Optional configuration
├── py/
│ ├── gmail-api-rw # Gmail API client
│ └── other tools...
└── man/
    └── m.md # This documentation

~/gd/local/seiton/ # Private scripts (not in mise)
├── bash/
│ ├── m -> ~/mise/bash/m # Symlink to main script
│ ├── mutt # SMTP wrapper (private)
│ └── other tools...
└── aux/
    └── m/ # Private m-support utilities
        ├── m-doctor # Health checker
        ├── m-queue # Offline queueing
        ├── m-support # Main support utility
        ├── m-completion.bash # Tab completion
        └── 10+ other m-* tools
```

### Architecture After Consolidation (2026-05-02)

**MAJOR CHANGE**: All email logic is now consolidated into the single `m` script. The previous `send` script has been eliminated.

**Old Architecture** (Pre-2026-05-02):
```
m dispatcher → smart_send() → send script → account routing → backends
```

**New Architecture** (Current):
```
m dispatcher → direct_send() → account routing → backends
```

### Key Code Sections in `m` Script

1. **Helper Paths Setup** (Lines 4-6):
   ```bash
   SCRIPT_DIR="$(dirname "$(realpath "$0")")"
   AUX_DIR="$(dirname "$SCRIPT_DIR")/aux/m"
   ```

2. **Dynamic Configuration Loading** (Lines 48-156):
   - Loads accounts from `~/.config/mail-tools/accounts.json`
   - Builds associative arrays: `EMAILS[]`, `LABELS[]`, `ACCTS[]`
   - Keeps all PII in configuration, not code

3. **Account Routing Functions** (Lines 158-215):
   - `_lookup_muttrc()`: Maps account to muttrc path
   - `_is_api_only()`: Decides Gmail API vs SMTP
   - `direct_send()`: Consolidated send logic (replaces send script)

4. **Inbox/Query Action** (Lines 617-694):
   - Handles listing, searching, reading, peek functionality
   - Peek integration: `-p` flag saves messages and invokes Claude Code
   - Pagination support: `pp2`, `pp3` syntax

5. **Send Action** (Lines 626-737):
   - Detects advanced features (attachments, CC/BCC, headers)
   - Routes to gmail-api-rw for advanced features
   - Routes to direct_send() for simple sends

### Configuration System

**Primary Config**: `~/.config/mail-tools/accounts.json`
```json
{
  "accounts": {
    "g": {
      "email": "user@gmail.com",
      "chrome_profile": "Default",
      "label": "Personal",
      "gmail_flag": ""
    },
    "u": {
      "email": "user@columbia.edu",
      "chrome_profile": "Profile 1",
      "label": "Work",
      "gmail_flag": "cu"
    }
  }
}
```

**Routing Decision**:
- `gmail_flag=""` → Default Gmail account
- `gmail_flag="cu"` → Specific backend routing (`-e cu` to gmail-api-rw)
- Chrome profile determines web browser routing

### Transport Backends

1. **Gmail API** (gmail-api-rw):
   - For API-only accounts (Columbia: `gmail_flag="cu"`)
   - Supports attachments, advanced headers, threading
   - OAuth authentication, appears in Gmail Sent folder

2. **SMTP** (mutt wrapper → gmail-smtp-w):
   - For traditional SMTP accounts
   - Uses neomutt configuration files
   - Good for non-Google email providers

### Support Utilities

**Location**: `~/mise/aux/m/` and `~/gd/local/seiton/aux/m/`

Key utilities:
- `m-support`: Main diagnostic and utility functions
- `m-doctor`: Health checking and configuration validation
- `m-queue`: Offline message queueing
- `m-completion.bash`: Tab completion for bash
- `m-config`: Configuration management

**Access Pattern**: All utilities use the `$AUX_DIR` variable to find helpers, enabling easy reorganization.

### Backward Compatibility

**Deprecated**: `send` script (eliminated 2026-05-02)
- Was a thin wrapper doing argument transformation
- All functionality moved into `m` script's `direct_send()` function
- External aliases updated to use `m send` directly

**Preserved**: All user-facing commands work identically
- `m u send file.eml` (same interface)
- `m -q "from:alice" 3 -p` (same search + peek)
- All account switching and flags unchanged

### Development Guidelines

1. **Single Source of Truth**: All email logic is in `m` script
2. **Helper Organization**: Use `$AUX_DIR` for all support utilities
3. **PII-Free Code**: All personal info stays in `~/.config/`
4. **Extensive Comments**: Code is heavily documented for future maintenance
5. **Testing**: Always test both API and SMTP account paths

### Anti-Bloat Engineering Principles

The email system follows strict consolidation principles learned from over-engineering:

1. **Tool count monitoring**: >7 tools in email system = red flag
2. **SWE reality check**: "Would user remember this exists in a week?"
3. **Interface preservation**: User commands never change, backend consolidation is safe
4. **Deletion over addition**: Remove duplicates before building new features
5. **Evidence-based changes**: Every change must cite specific user complaint or failure

### Invisible Dependencies Awareness

Critical dependencies that must be preserved during any changes:

- **Security hooks**: `~/.claude/hooks/block-email-send.sh` patterns
- **Permission allowlists**: `~/.claude/settings.local.json` tool permissions
- **Claude Code skills**: `/reply`, `/inbox`, `/egrab` commands expect specific interfaces
- **Global instructions**: `~/.claude/CLAUDE.md` documents current tool behavior
- **External aliases**: 500+ shell aliases depend on tool names and interfaces

**Protocol**: Before any tool consolidation, audit all hardcoded tool references first.

### Recent Major Changes

- **2026-05-02**: Complete consolidation - eliminated `send` script
- **2026-05-02**: Directory reorganization - `aux/m/` structure
- **2026-05-02**: Fixed peek functionality and query parsing bugs
- **2026-05-02**: Added comprehensive code documentation

The system is now fully consolidated with excellent documentation for future maintenance.

## License

See ~/mise/LICENSE or parent project license.