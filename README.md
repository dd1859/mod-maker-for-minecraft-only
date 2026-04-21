# AI Minecraft Mod Generator (All Python, No Server)

This project is a **Python-only CLI pipeline** (no FastAPI, no React server).

It will:

1. Fetch lightweight web context for Forge modding.
2. Call an **ollamafreeapi/OpenAI-compatible** chat endpoint to generate Java code.
3. Create a valid Forge mod structure from a local MDK template.
4. Inject `MainMod.java` + `GeneratedContent.java`.
5. Run `./gradlew build`.
6. Print the output `.jar` path.

## API key support

The CLI supports both variable styles:

- `OLLAMAFREEAPI_URL`, `OLLAMAFREEAPI_KEY`, `OLLAMAFREEAPI_MODEL`
- `OPENAI_API_URL`, `OPENAI_API_KEY`, `OPENAI_MODEL`

> Security: never commit real API keys into source control.

## Setup (Windows)

## Quick local key use (do not commit)

Use your key only in your terminal session (or local `.env`), for example on Windows:

```bat
set OPENAI_API_KEY=YOUR_KEY_HERE
set OPENAI_API_URL=https://api.openai.com/v1/chat/completions
set OPENAI_MODEL=gpt-4o-mini
start_windows.bat
```

Run:

```bat
setup_windows.bat
```

Then run:

```bat
start_windows.bat
```

`start_windows.bat` is interactive and can save values in `.env`.

You can also pass args directly:

```bat
start_windows.bat "Create a glowing ore block that drops XP" glowore
```

## Setup (manual / Linux / macOS)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Forge template

Put a Forge MDK template in `template/` with at least:

- `build.gradle`
- `gradlew`
- `gradlew.bat`
- `gradle/wrapper/*`

## Direct CLI run

```bash
export OPENAI_API_URL="https://api.openai.com/v1/chat/completions"
export OPENAI_API_KEY="your_key"
export OPENAI_MODEL="gpt-4o-mini"

python mod_generator.py "Create a glowing ore block that drops XP" --mod-id glowore
```

## Troubleshooting

- If you get key missing errors, set `OPENAI_API_KEY` or `OLLAMAFREEAPI_KEY`.
- If you get template missing errors, copy a full Forge MDK into `template/`.
- If Gradle fails, confirm Java 17+ with `java -version`.
- If AI HTTP fails (401/403/404), verify URL/key/model.
