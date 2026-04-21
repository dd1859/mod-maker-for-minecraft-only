# AI Minecraft Mod Generator (Python CLI)

Generate and compile a Minecraft Forge mod from a prompt using an OpenAI/ollamafreeapi-compatible endpoint.

## API variables supported

You can use either naming style:

- `OPENAI_API_URL`, `OPENAI_API_KEY`, `OPENAI_MODEL`
- `OLLAMAFREEAPI_URL`, `OLLAMAFREEAPI_KEY`, `OLLAMAFREEAPI_MODEL`

> Never commit real API keys to git.

## Windows quick start

1. Run setup:

```bat
setup_windows.bat
```

2. Run interactive starter:

```bat
start_windows.bat
```

Or run with args:

```bat
start_windows.bat "Create a glowing ore block that drops XP" glowore
```

## Manual run (Linux/macOS/PowerShell)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export OPENAI_API_URL="https://api.openai.com/v1/chat/completions"
export OPENAI_API_KEY="YOUR_KEY"
export OPENAI_MODEL="gpt-4o-mini"
python mod_generator.py "Create a glowing ore block that drops XP" --mod-id glowore
```

## Forge template requirements

Put a Forge MDK template in `template/` with at least:

- `build.gradle`
- `gradlew`
- `gradlew.bat`
- `gradle/wrapper/*`

## Troubleshooting

- Missing key: set `OPENAI_API_KEY` or `OLLAMAFREEAPI_KEY`.
- Missing template files: copy full Forge MDK into `template/`.
- Gradle errors: verify Java 17+ with `java -version`.
- AI HTTP errors (401/403/404): verify URL/key/model.


## If GitHub still says "This branch has conflicts"

That means conflict is against the remote base branch, not just local conflict markers.
Use:

```bash
./resolve_conflicts.sh origin main
```

Then fix any files listed as unmerged, `git add` them, and commit.
