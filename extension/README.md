# Wordle Solver Browser Extension

This extension automatically reads your Wordle game and provides AI-powered suggestions.

## Installation

1. **Install Python dependencies:**

   ```bash
   pip install flask flask-cors
   ```

2. **Start the Python server:**

   **Baseline solver (default, no model needed):**

   ```bash
   python scripts/wordle_server.py
   ```

   **ML model (optional, requires trained model):**

   ```bash
   python scripts/wordle_server.py --model models/mlp_model.pth
   ```

   The server will run on `http://localhost:5000`

3. **Load the extension in Chrome/Edge:**

   - Open `chrome://extensions/` (or `edge://extensions/`)
   - Enable "Developer mode"
   - Click "Load unpacked"
   - Select the `extension` folder

4. **Load the extension in Firefox:**
   - Open `about:debugging`
   - Click "This Firefox"
   - Click "Load Temporary Add-on"
   - Select `extension/manifest.json`

## Usage

1. Start the Python server (see above)
2. Go to any Wordle game:
   - **NYTimes Wordle:** https://www.nytimes.com/games/wordle/
   - **Wordle Unlimited:** https://wordleunlimited.org/ or https://wordleunlimited.com/
   - Other Wordle sites (if they use similar tile structure)
3. The extension will automatically:

   - Read your guesses and feedback
   - Display top 5 suggestions
   - Show best starting words if you haven't guessed yet
   - Track solved words automatically
   - Detect when you solve or fail the puzzle

4. **Toggle between Baseline and ML solver:**
   - Use the checkbox in the extension panel to switch between Baseline and ML solver
   - ML mode requires the server to be started with `--model` flag
   - Your preference is saved and persists across page reloads

## Features

- ✅ Automatic game state reading
- ✅ Real-time suggestions
- ✅ Best starting word recommendations
- ✅ Automatic word tracking
- ✅ Toggle between Baseline and ML solver
- ✅ Works with baseline solver (no ML model needed)
- ✅ Optional ML model support (requires trained model)

## Troubleshooting

- **Suggestions not appearing:** Make sure the Python server is running
- **Connection errors:** Check that the server is on `http://localhost:5000`
- **Game not detected:** Refresh the Wordle page after loading the extension
- **ML mode not working:** Make sure the server was started with `--model` flag pointing to a trained model file
