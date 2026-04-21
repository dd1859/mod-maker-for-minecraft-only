# AI Minecraft Mod Generator (Tkinter UI)

This is now a **desktop Tkinter app** (Python only).

## What changed

- No API URL/model configuration needed in UI.
- The app only asks for a **Gemini API key**.
- Uses fixed Gemini endpoint + model internally:
  - `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent`
  - `gemini-2.0-flash`
- Sends only one AI request per generation (no extra web-context request).

## Windows quick start

1. Run setup:

```bat
setup_windows.bat
```

2. Launch app:

```bat
start_windows.bat
```

3. In the UI:
   - Paste Gemini API key
   - Enter Mod ID + prompt
   - Click **Generate + Build**

## Manual launch

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python mod_generator.py
```

## Forge template requirements

Put a Forge MDK template in `template/` with at least:

- `build.gradle`
- `gradlew`
- `gradlew.bat`
- `gradle/wrapper/*`

## Troubleshooting

- `Missing template files`: copy full Forge MDK to `template/`.
- `HTTP 401/403`: invalid Gemini API key.
- Gradle build errors: ensure Java 17+ is installed.
