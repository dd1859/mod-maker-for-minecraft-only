#!/usr/bin/env python3
"""Generate and build a Minecraft Forge mod from a text prompt."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path
from typing import Any

DEFAULT_CONTEXT = "Minecraft Forge modding context"


def load_dotenv(path: Path = Path('.env')) -> None:
    if not path.exists():
        return
    for raw in path.read_text(encoding='utf-8').splitlines():
        line = raw.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def sanitize_mod_id(mod_id: str) -> str:
    mod_id = re.sub(r'[^a-z0-9_]', '', mod_id.lower().strip())
    return (mod_id or 'generatedmod')[:50]


def http_get_json(url: str, timeout: int = 20) -> dict[str, Any]:
    req = urllib.request.Request(url, method='GET')
    with urllib.request.urlopen(req, timeout=timeout) as res:
        return json.loads(res.read().decode('utf-8'))


def http_post_json(url: str, payload: dict[str, Any], headers: dict[str, str], timeout: int = 90) -> dict[str, Any]:
    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')
    with urllib.request.urlopen(req, timeout=timeout) as res:
        return json.loads(res.read().decode('utf-8'))


def fetch_web_context(prompt: str) -> str:
    q = urllib.parse.quote_plus(f'Minecraft Forge mod example {prompt}')
    url = f'https://api.duckduckgo.com/?q={q}&format=json'
    try:
        data = http_get_json(url)
        return data.get('AbstractText') or DEFAULT_CONTEXT
    except Exception:
        return DEFAULT_CONTEXT


def generate_ai_java(prompt: str, context: str, api_url: str, api_key: str, model: str) -> str:
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {api_key}'}
    payload: dict[str, Any] = {
        'model': model,
        'messages': [
            {
                'role': 'system',
                'content': (
                    'Generate valid Java for Minecraft Forge. '
                    'Return Java only (no markdown). '
                    f'Context: {context}'
                ),
            },
            {'role': 'user', 'content': prompt},
        ],
        'temperature': 0.2,
    }
    data = http_post_json(api_url, payload, headers)
    result = data.get('choices', [{}])[0].get('message', {}).get('content', '').strip()
    if not result:
        raise RuntimeError('AI response was empty')
    return result


def base_class(mod_id: str) -> str:
    return f'''package com.example.{mod_id};

import net.minecraftforge.fml.common.Mod;

@Mod("{mod_id}")
public class MainMod {{
    public MainMod() {{
        System.out.println("{mod_id} loaded!");
    }}
}}
'''


def ensure_template(template_dir: Path) -> None:
    required = [template_dir / 'build.gradle', template_dir / 'gradlew']
    missing = [str(p) for p in required if not p.exists()]
    if missing:
        raise FileNotFoundError('Missing template files: ' + ', '.join(missing))


def build_project(template_dir: Path, output_dir: Path, mod_id: str, ai_java: str) -> Path:
    build_id = uuid.uuid4().hex[:12]
    project_dir = output_dir / build_id
    shutil.copytree(template_dir, project_dir)

    src = project_dir / 'src' / 'main' / 'java' / 'com' / 'example' / mod_id
    src.mkdir(parents=True, exist_ok=True)
    (src / 'MainMod.java').write_text(base_class(mod_id), encoding='utf-8')
    (src / 'GeneratedContent.java').write_text(ai_java, encoding='utf-8')

    gradlew = 'gradlew.bat' if os.name == 'nt' else './gradlew'
    run = subprocess.run([gradlew, 'build'], cwd=project_dir, capture_output=True, text=True, check=False, timeout=900)
    if run.returncode != 0:
        tail = (run.stdout + '\n' + run.stderr)[-4000:]
        raise RuntimeError(f'Gradle build failed:\n{tail}')

    jars = sorted((project_dir / 'build' / 'libs').glob('*.jar'))
    if not jars:
        raise RuntimeError('No jar found in build/libs after successful build')

    meta = {
        'build_id': build_id,
        'mod_id': mod_id,
        'project_dir': str(project_dir),
        'jar': str(jars[0]),
    }
    (project_dir / 'build_meta.json').write_text(json.dumps(meta, indent=2), encoding='utf-8')
    return jars[0]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description='Generate and compile a Minecraft Forge mod')
    p.add_argument('prompt', help='Prompt describing the mod')
    p.add_argument('--mod-id', default='generatedmod')
    p.add_argument('--template-dir', default='template')
    p.add_argument('--output-dir', default='generated_mods')
    p.add_argument('--ai-url', default=os.getenv('OLLAMAFREEAPI_URL') or os.getenv('OPENAI_API_URL') or 'https://api.openai.com/v1/chat/completions')
    p.add_argument('--ai-key', default=os.getenv('OLLAMAFREEAPI_KEY') or os.getenv('OPENAI_API_KEY') or '')
    p.add_argument('--ai-model', default=os.getenv('OLLAMAFREEAPI_MODEL') or os.getenv('OPENAI_MODEL') or 'gpt-4o-mini')
    return p.parse_args()


def main() -> int:
    load_dotenv()
    args = parse_args()

    if not args.ai_key:
        print('error: missing key (set OPENAI_API_KEY or OLLAMAFREEAPI_KEY)', file=sys.stderr)
        return 2

    try:
        mod_id = sanitize_mod_id(args.mod_id)
        template = Path(args.template_dir).resolve()
        out = Path(args.output_dir).resolve()
        ensure_template(template)
        out.mkdir(parents=True, exist_ok=True)

        context = fetch_web_context(args.prompt)
        java_code = generate_ai_java(args.prompt, context, args.ai_url, args.ai_key, args.ai_model)
        jar = build_project(template, out, mod_id, java_code)

        print('Build complete')
        print(f'Mod ID: {mod_id}')
        print(f'JAR: {jar}')
        return 0
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='ignore') if hasattr(e, 'read') else ''
        print(f'error: AI HTTP {e.code} {e.reason}\n{body}', file=sys.stderr)
        return 1
    except (urllib.error.URLError, TimeoutError) as e:
        print(f'error: network request failed: {e}', file=sys.stderr)
        return 1
    except Exception as e:
        print(f'error: {e}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
