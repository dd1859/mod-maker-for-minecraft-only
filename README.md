# AI Minecraft Mod Generator (All Python, No Server)

This project is a **Python-only CLI pipeline** (no FastAPI, no React server).

It will:

1. Fetch lightweight web context for Forge modding.
2. Call an **ollamafreeapi/OpenAI-compatible** chat endpoint to generate Java code.
3. Create a valid Forge mod structure from a local MDK template.
4. Inject `MainMod.java` + `GeneratedContent.java`.
5. Run `./gradlew build`.
6. Print the output `.jar` path.

## Setup (Windows)

Run:

```bat
setup_windows.bat
```

What it does:

- checks for `python`
- checks for `java` (JDK 17+)
- if missing, downloads installers with `curl` and installs silently
- creates `.venv`
- installs `requirements.txt`

Then start a build with:

```bat
set OLLAMAFREEAPI_URL=https://your-ollamafreeapi-endpoint/v1/chat/completions
set OLLAMAFREEAPI_KEY=your_key
set OLLAMAFREEAPI_MODEL=gpt-4o-mini

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
export OLLAMAFREEAPI_URL="https://your-ollamafreeapi-endpoint/v1/chat/completions"
export OLLAMAFREEAPI_KEY="your_key"
export OLLAMAFREEAPI_MODEL="gpt-4o-mini"

python mod_generator.py "Create a glowing ore block that drops XP" --mod-id glowore
```

Optional args:

- `--template-dir template`
- `--output-dir generated_mods`
- `--ai-url ...`
- `--ai-key ...`
- `--ai-model ...`

## Notes

- Keep builds sandboxed in production (container/VM).
- API keys stay local only.
- `setup_windows.bat` relies on internet access to download installers.
