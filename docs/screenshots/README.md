# README screenshots

PNG files in this folder can be embedded in the root **`README.md`** so visitors see the UI before installing.

## Suggested files

| File | What to capture |
|------|-----------------|
| **`rates.png`** | **Rates** tab: key rates strip + part of the full rates table (league visible in subtitle if possible). |
| **`flips.png`** | **Flips** tab with a few profitable rows (blur character names if any). |
| **`settings.png`** | **Settings** page (optional): game + league + one filter section. |

Use **1280–1600px** width unless the layout needs more. Prefer **dark theme** as the app ships. Avoid huge full-page shots; crop to the main panel.

## How to capture

1. Run **`python app.py`** and open **http://127.0.0.1:5000**.
2. Set league/game as needed (**Settings**).
3. Use your OS screenshot tool (Windows: Snipping Tool / Win+Shift+S; macOS: Cmd+Shift+4).
4. Save as PNG into this directory with the names above.

## Embedding in `README.md`

After the files are committed, add near the top of the README (e.g. under **Screenshots**):

```markdown
![Rates tab](docs/screenshots/rates.png)

![Flips tab](docs/screenshots/flips.png)
```

Keep images reasonably small (compress if needed) so the repo stays light.
