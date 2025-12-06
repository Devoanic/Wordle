# Wordle Solver Extension - Quick Setup

## Step 1: Install Dependencies

```bash
pip install flask flask-cors
```

## Step 2: Start the Server

```bash
python scripts/wordle_server.py
```

You should see:

```
Wordle Solver Web Server
Server running at: http://127.0.0.1:5000
```

Keep this terminal window open!

## Step 3: Load the Extension

### Chrome/Edge:

1. Open `chrome://extensions/` (or `edge://extensions/`)
2. Enable **"Developer mode"** (toggle in top right)
3. Click **"Load unpacked"**
4. Navigate to and select the `extension` folder in this project

### Firefox:

1. Open `about:debugging`
2. Click **"This Firefox"**
3. Click **"Load Temporary Add-on"**
4. Select `extension/manifest.json`

## Step 4: Use It!

1. Go to https://www.nytimes.com/games/wordle/
2. The extension will automatically:
   - Show best starting words before you guess
   - Read your guesses and feedback automatically
   - Display top 5 suggestions in a panel on the right
   - Track solved words automatically

## Features

✅ **Automatic Reading** - No typing needed, reads game state directly  
✅ **Real-time Suggestions** - Updates as you play  
✅ **Best Starting Words** - Shows optimal first guesses  
✅ **Auto-tracking** - Learns from solved words

## Troubleshooting

**"Server not running" error:**

- Make sure `python scripts/wordle_server.py` is running
- Check it's on port 5000

**Suggestions not appearing:**

- Refresh the Wordle page
- Check browser console (F12) for errors
- Make sure extension is enabled

**Game state not detected:**

- Wait a few seconds after page loads
- Try refreshing the page
- Check that you're on the official Wordle site

