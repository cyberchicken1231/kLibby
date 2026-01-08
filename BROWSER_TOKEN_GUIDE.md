# Browser Token Authentication Guide

## Why Browser Token?

As of **late 2024**, Libby/OverDrive changed their API to restrict clone code authentication. Clone codes now only give **READ-ONLY** permissions - you can view your loans and holds, but **cannot download books**.

The **browser token method** gives you **full permissions** including downloads.

## How to Get Your Browser Token

### Step-by-Step Instructions

1. **Open Libby in a web browser**
   - Go to: https://libbyapp.com
   - Sign in with your library card

2. **Open Developer Tools**
   - **Easiest:** Right-click anywhere → "Inspect"
   - **Or:** Press `Ctrl+Shift+I` (Windows/Linux) or `Cmd+Option+I` (Mac)
   - **Or:** Press `F12` (if available)
   - **Or:** Browser menu → More tools → Developer tools

3. **Go to Network Tab**
   - Click the "Network" tab in DevTools
   - Make sure "Preserve log" is checked

4. **Trigger a Request**
   - Click on any book in Libby
   - Or browse your loans/holds

5. **Find the Request**
   - In the Network tab, you'll see several requests
   - Look for requests to `sentry-read.svc.overdrive.com`
   - Click on any of these requests

6. **Copy the Authorization Header**
   - In the request details, find "Request Headers"
   - Look for the `Authorization:` header
   - It will look like: `Authorization: Bearer eyJhbGci...` (very long)
   - Copy the **entire value** after "Bearer "
   - The token starts with `eyJ` and is hundreds of characters long

7. **Use in kLibby**
   - Go to kLibby → Settings → Authenticate with Libby
   - Choose "Use Browser Token"
   - Paste the token when prompted
   - You can paste with or without "Bearer " prefix

## Visual Guide

```
DevTools → Network Tab:

┌─────────────────────────────────────────────────────┐
│ Name          Status  Type    Size   Time           │
├─────────────────────────────────────────────────────┤
│ sync          200     json    5.2KB  150ms         │  ← Click this
│ loans         200     json    12KB   200ms         │
└─────────────────────────────────────────────────────┘

Request Details:
┌─────────────────────────────────────────────────────┐
│ Headers   Preview   Response   Timing               │
├─────────────────────────────────────────────────────┤
│ Request Headers                                      │
│                                                      │
│ Authorization: Bearer eyJhbGciOiJSUzI1NiJ9.eyJhdWQ...│  ← Copy this!
│                                                      │
└─────────────────────────────────────────────────────┘
```

## Token Format

A valid token looks like this:
```
eyJhbGciOiJSUzI1NiJ9.eyJhdWQiOiJyZWFkaXZlcnNlIiwiaWF0IjoxNzA0MDY...
```

- Starts with `eyJ`
- Very long (500+ characters)
- Contains dots (`.`) separating sections
- Mix of letters, numbers, hyphens, underscores

## Troubleshooting

### "Token too short" error
- Make sure you copied the **full** token
- It should be 500+ characters long
- Don't copy just part of it

### "Token verification failed"
- Make sure you're signed into Libby in the browser
- Try clicking on a different request
- Some requests might not have the Authorization header
- Look for requests to `sentry-read.svc.overdrive.com`

### "Could not find Authorization header"
- Make sure you're logged into libbyapp.com
- Try interacting with Libby (click a book, view loans)
- This generates new requests with the header

## How Long Does the Token Last?

Browser tokens typically last for **several weeks to months**. When it expires:
- You'll get authentication errors
- Simply repeat the process to get a new token
- kLibby will tell you if your token has expired

## Security Note

Your browser token gives **full access** to your Libby account. Keep it private and don't share it with anyone.

kLibby stores your token in `~/.klibby/settings.json`. Keep this file secure.

## Alternative: Clone Codes (Limited)

If you don't need downloads, clone codes still work for:
- ✅ Viewing loans and holds
- ✅ Managing library cards
- ✅ Browsing the catalog
- ❌ Downloading books (broken as of late 2024)

For full functionality including downloads, use the browser token method.
