# Google Calendar API Setup Guide

## Step 1: Create a New Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Enter project name: `gcal-cli-tool` (or any name you prefer)
4. Click "Create"

## Step 2: Enable Google Calendar API

1. In the new project, go to "APIs & Services" → "Library"
2. Search for "Google Calendar API"
3. Click on it and press "Enable"

## Step 3: Create OAuth2 Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. If prompted, configure the OAuth consent screen:
   - Choose "External" user type
   - Fill in required fields:
     - App name: `GCal CLI Tool`
     - User support email: `chris.wiggins@gmail.com`
     - Developer contact: `chris.wiggins@gmail.com`
   - Add scopes: `https://www.googleapis.com/auth/calendar`
   - Add test users: `chris.wiggins@gmail.com`
4. For Application type, choose "Desktop application"
5. Name it: `GCal CLI Desktop App`
6. Click "Create"
7. Download the JSON file

## Step 4: Update Credentials

1. Replace the contents of `~/.config/gcal/credentials.json` with the downloaded JSON
2. Make sure it has the "installed" section (not "web")

## Step 5: Test the Setup

Run: `python3 gcal-api-setup`

The new project should work without verification issues since it's in development mode with you as a test user.
