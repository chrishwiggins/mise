# Google Calendar CLI Tools Reference

## Quick Reference

| Tool | Location | Primary Use |
|------|----------|-------------|
| `gcal-quick` | `~/mise/py/` | Natural language event creation |
| `gcal-simple` | `~/mise/py/` | Structured events with attendees |
| `gcal-invite-advanced` | `~/gd/local/seiton/python/` | Robust invites, flexible auth |
| `gcal-import` | `~/mise/py/` | Import ICS files |
| `gcal-auth-setup` | `~/mise/py/` | OAuth setup/refresh |
| `gcal-attic/` | `~/gd/local/seiton/python/` | Archive of deprecated tools |

---

## Tool Details

### gcal-quick

**Purpose**: Create events using Google's Quick Add natural language parser.

**Location**: `/Users/wiggins/mise/py/gcal-quick`

**Usage**:
```bash
gcal-quick "<natural language text>"
gcal-quick --open "<text>"   # Opens event in browser after creation
```

**Examples**:
```bash
gcal-quick "Lunch with Bob tomorrow at noon"
gcal-quick "Doctor appointment next Monday at 3:30pm"
gcal-quick "Conference call 10am to 11am"
gcal-quick "Vacation Dec 23-30"
gcal-quick --open "Team meeting Friday 2pm"
```

**Features**:
- Uses Google's built-in natural language parsing
- Supports relative dates (today, tomorrow, next Friday)
- Supports time ranges ("10am to 11am")
- Supports all-day events ("Vacation Dec 25-30")
- `--open` flag opens created event in browser

**Limitations**:
- No attendee support (use gcal-simple or gcal-invite-advanced for invites)
- Parsing depends on Google's interpretation

**Auth**: Requires `GCAL_TOKEN_PATH` environment variable.

---

### gcal-simple

**Purpose**: Create structured calendar events with attendees and optional Google Meet.

**Location**: `/Users/wiggins/mise/py/gcal-simple`

**Usage**:
```bash
gcal-simple add <title> <when> <duration_min> <attendees> [description] [location]
gcal-simple list [count]
gcal-simple setup
```

**Examples**:
```bash
# Create event with attendees
gcal-simple add "Team Meeting" "today 2pm" 60 "alice@co.com,bob@co.com" "Weekly standup"

# Create event with location
gcal-simple add "Lunch" "2025-12-25 12:30pm" 90 "friend@gmail.com" "" "Restaurant Name"

# Auto-add Google Meet (triggered by keywords in description)
gcal-simple add "Call" "tomorrow 3pm" 30 "client@company.com" "video call meeting"

# List upcoming events
gcal-simple list 5
```

**Features**:
- Structured event creation with explicit parameters
- Comma-separated attendee list (sends email invites)
- Auto-adds Google Meet if description contains: video, meet, zoom, call
- `list` command shows upcoming events
- Custom reminders: email 24h before, popup 10min before

**Time Formats**:
- `"today 4pm"`, `"tomorrow 2:30pm"`
- `"2025-12-25 3pm"`
- Times without AM/PM: assumes PM if hour < 8

**Auth**: Requires `GCAL_TOKEN_PATH` and `GCAL_CREDENTIALS_PATH` environment variables.

**Timezone**: Hardcoded to America/New_York.

---

### gcal-invite-advanced

**Purpose**: Most robust tool for creating calendar invites. Flexible credential discovery, better time parsing.

**Location**: `/Users/wiggins/gd/local/seiton/python/gcal-invite-advanced`

**Usage**:
```bash
gcal-invite add <title> <when> <duration> <attendees> [description]
gcal-invite meet <title> <when> <duration> <attendees> [description]
gcal-invite quick <natural language text>
```

**Examples**:
```bash
# Structured invite
gcal-invite add "Seminar" "today 4pm" 30 "user@domain.edu" "Weekly seminar"

# Force Google Meet link
gcal-invite meet "Team Sync" "tomorrow 2pm" 60 "team@company.com" "Quarterly review"

# Quick add (same as gcal-quick)
gcal-invite quick "Lunch with Bob tomorrow at noon"
```

**Features**:
- **Flexible credential discovery**: Checks env vars, then `~/.config/gcal/`, `~/.gcal/`, `./.gcal/`, `./`
- **Better time parsing**: Full ISO date support (`2025-12-25 3pm`)
- **Three commands**: `add`, `meet` (forces Meet link), `quick`
- Auto-detects video keywords for Meet
- Sends email invites automatically

**Auth Discovery Order**:
1. `GCAL_TOKEN_PATH` + `GCAL_CREDENTIALS_PATH` env vars
2. `~/.config/gcal/token.pickle` + `credentials.json`
3. `~/.gcal/token.pickle` + `credentials.json`
4. `./.gcal/token.pickle` + `credentials.json`
5. `./token.pickle` + `credentials.json`

**Timezone**: Uses `GCAL_TIMEZONE` env var (default: America/New_York).

---

### gcal-import

**Purpose**: Import events from ICS calendar files (e.g., from email attachments, healthcare portals).

**Location**: `/Users/wiggins/mise/py/gcal-import`

**Usage**:
```bash
gcal-import <ics-file> [options]

Options:
  --dry-run, -n     Preview events without importing
  --calendar <id>   Target calendar ID (default: primary)
  --yes, -y         Skip confirmation prompt
```

**Examples**:
```bash
# Preview what would be imported
gcal-import ~/Downloads/appointment.ics --dry-run

# Import with confirmation prompt
gcal-import ~/Downloads/Physical.ics

# Import without confirmation
gcal-import ~/Downloads/meeting.ics -y

# Import to specific calendar
gcal-import event.ics --calendar work@group.calendar.google.com
```

**Features**:
- Parses standard ICS/iCalendar files
- Handles UTC timestamps (Z suffix) and timezone-aware times
- Supports all-day events
- Preserves location and description
- Handles ICS line folding and escape sequences
- Preview mode (`--dry-run`) before committing
- Multi-event file support

**Common ICS Sources**:
- Healthcare portals (MyChart, etc.)
- Conference/event registration
- Email calendar attachments
- Exported events from other calendars

**Auth**: Requires `GCAL_TOKEN_PATH` environment variable.

---

### gcal-auth-setup

**Purpose**: One-time OAuth2 setup and token refresh for Google Calendar API.

**Location**: `/Users/wiggins/mise/py/gcal-auth-setup`

**Usage**:
```bash
gcal-auth-setup        # Run full OAuth flow
gcal-auth-setup test   # Test that API is working
```

**What It Does**:
1. Checks for `credentials.json` (OAuth client config from Google Cloud Console)
2. Opens browser for OAuth consent flow
3. Saves `token.pickle` for future API calls
4. Tests API access by listing calendars

**When to Run**:
- First-time setup
- After token expires and can't auto-refresh
- After changing OAuth scopes
- When other gcal tools report auth errors

**Auth**: Requires `GCAL_TOKEN_PATH` and `GCAL_CREDENTIALS_PATH` environment variables.

---

### gcal-attic/

**Purpose**: Archive directory containing deprecated/experimental gcal tools.

**Location**: `/Users/wiggins/gd/local/seiton/python/gcal-attic/`

**Contents**:
- `deleted/` - Old tools that have been superseded
  - `gcal-cli` - Early CLI attempt
  - `gcal-quick-setup` - Old setup script
  - `gcal-api-direct` - Direct API experimentation
  - `workshop_to_gcal.py` - Workshop-specific importer
  - `blurb2gcal_verbose` - Text-to-event converter
  - `gcal-add` - Simple add tool
- `reference/` - Useful reference implementations
  - `workshop_to_gcal_v2.py`
  - `blurb2gcal_with_invites`

**Note**: These are NOT in PATH. They exist for reference/archaeology only.

---

## Environment Variables

| Variable | Required By | Purpose |
|----------|-------------|---------|
| `GCAL_TOKEN_PATH` | All tools | Path to `token.pickle` |
| `GCAL_CREDENTIALS_PATH` | gcal-simple, gcal-auth-setup | Path to `credentials.json` |
| `GCAL_TIMEZONE` | gcal-invite-advanced, gcal-import | Default timezone (default: America/New_York) |

**Typical Setup** (in `.cshrc` or `.zshrc`):
```bash
setenv GCAL_TOKEN_PATH "$HOME/.config/gcal/token.pickle"
setenv GCAL_CREDENTIALS_PATH "$HOME/.config/gcal/credentials.json"
setenv GCAL_TIMEZONE "America/New_York"
```

---

## Decision Tree: Which Tool to Use?

```
What are you trying to do?
│
├─ Import an ICS file (from email, healthcare portal, etc.)
│  └─> gcal-import
│
├─ List upcoming events
│  └─> gcal-simple list
│
├─ Create a new event
│  │
│  ├─ Do you need to invite attendees?
│  │  │
│  │  ├─ NO (personal reminder/appointment)
│  │  │  └─> gcal-quick
│  │  │
│  │  └─ YES (meeting with others)
│  │     │
│  │     ├─ Do you need to FORCE a Google Meet link?
│  │     │  │
│  │     │  ├─ YES (guaranteed video call)
│  │     │  │  └─> gcal-invite meet
│  │     │  │
│  │     │  └─ NO (or auto-detect from description is fine)
│  │     │     │
│  │     │     └─ Are your credentials in standard env vars?
│  │     │        │
│  │     │        ├─ YES (GCAL_TOKEN_PATH set correctly)
│  │     │        │  └─> gcal-simple add
│  │     │        │
│  │     │        └─ NO (credentials in ~/.config/gcal/, ~/.gcal/, etc.)
│  │     │           └─> gcal-invite add
│  │     │
│
└─ Fix authentication issues
   └─> gcal-auth-setup
```

---

## Quick Examples by Task

**"Add a quick personal reminder"**
```bash
gcal-quick "Dentist appointment March 15 at 2pm"
```

**"Schedule a meeting with coworkers"**
```bash
gcal-simple add "Sprint Planning" "tomorrow 10am" 60 "alice@co.com,bob@co.com" "Weekly sprint"
```

**"Set up a video call with external client"**
```bash
gcal-invite meet "Client Demo" "2025-02-01 3pm" 45 "client@external.com" "Product walkthrough"
```

**"Import appointment from healthcare portal"**
```bash
gcal-import ~/Downloads/appointment.ics
```

**"Check what's on my calendar"**
```bash
gcal-simple list 10
```

---

## Troubleshooting

**"Not authenticated" error**
```bash
gcal-auth-setup
```

**"Token has wrong scopes" error**
```bash
rm ~/.config/gcal/token.pickle
gcal-auth-setup
```

**"Environment variables not set" error**
```bash
# Check current values
echo $GCAL_TOKEN_PATH
echo $GCAL_CREDENTIALS_PATH

# Set them (csh/tcsh)
setenv GCAL_TOKEN_PATH "$HOME/.config/gcal/token.pickle"
setenv GCAL_CREDENTIALS_PATH "$HOME/.config/gcal/credentials.json"
```

**ICS import shows wrong time**
- ICS files with `Z` suffix are UTC - Google Calendar will display in your local timezone
- Check `GCAL_TIMEZONE` if times seem off
