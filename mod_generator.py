#!/usr/bin/env python3
"""AI Minecraft Forge mod generator (no server; Python-only CLI)."""

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


def sanitize_mod_id(mod_id: str) -> str:
    mod_id = re.sub(r"[^a-z0-9_]", "", mod_id.lower().strip())
    return (mod_id or "generatedmod")[:50]


def _http_get_json(url: str, timeout: int = 20) -> dict[str, Any]:
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _http_post_json(url: str, payload: dict[str, Any], headers: dict[str, str], timeout: int = 90) -> dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_web_context(prompt: str) -> str:
    query = urllib.parse.quote_plus(f"Minecraft Forge mod example {prompt}")
    url = f"https://api.duckduckgo.com/?q={query}&format=json"
    try:
        data = _http_get_json(url, timeout=20)
        return data.get("AbstractText") or DEFAULT_CONTEXT
    except Exception:
        return DEFAULT_CONTEXT


def ollamafreeapi_chat(prompt: str, web_context: str, api_url: str, api_key: str, model: str) -> str:
    headers: dict[str, str] = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    payload: dict[str, Any] = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You generate valid Java code for Minecraft Forge mods. "
                    "Return Java source only with no markdown fences. "
                    f"Reference context: {web_context}"
                ),
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
    }

    data = _http_post_json(api_url, payload, headers, timeout=90)
    text = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
    if not text:
        raise RuntimeError("AI response was empty.")
    return text


def create_base_class(mod_id: str) -> str:
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
    required = [template_dir / "build.gradle", template_dir / "gradlew"]
    missing = [str(x) for x in required if not x.exists()]
    if missing:
        raise FileNotFoundError("Template missing files: " + ", ".join(missing))


def build_mod(template_dir: Path, output_dir: Path, mod_id: str, ai_code: str) -> Path:
    build_id = uuid.uuid4().hex[:12]
    project_dir = output_dir / build_id
    shutil.copytree(template_dir, project_dir)

    src = project_dir / "src" / "main" / "java" / "com" / "example" / mod_id
    src.mkdir(parents=True, exist_ok=True)
    (src / "MainMod.java").write_text(create_base_class(mod_id), encoding="utf-8")
    (src / "GeneratedContent.java").write_text(ai_code, encoding="utf-8")

    gradlew = "gradlew.bat" if os.name == "nt" else "./gradlew"
    result = subprocess.run(
        [gradlew, "build"],
        cwd=project_dir,
        capture_output=True,
        text=True,
        check=False,
        timeout=900,
    )
    if result.returncode != 0:
        tail = (result.stdout + "\n" + result.stderr)[-4000:]
        raise RuntimeError(f"Gradle build failed:\n{tail}")

    libs = project_dir / "build" / "libs"
    jars = sorted([x for x in libs.glob("*.jar") if x.is_file()])
    if not jars:
        raise RuntimeError("Gradle build passed but no JAR found in build/libs")

    meta = {
        "build_id": build_id,
        "mod_id": mod_id,
        "project_dir": str(project_dir),
        "jar": str(jars[0]),
    }
    (project_dir / "build_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return jars[0]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate and compile a Minecraft Forge mod from a prompt")
    p.add_argument("prompt", help="Mod idea prompt")
    p.add_argument("--mod-id", default="generatedmod", help="Forge mod id (default: generatedmod)")
    p.add_argument("--template-dir", default="template", help="Path to Forge MDK template")
    p.add_argument("--output-dir", default="generated_mods", help="Where generated projects are created")
    p.add_argument("--ai-url", default=os.getenv("OLLAMAFREEAPI_URL", ""), help="ollamafreeapi/OpenAI-compatible chat endpoint")
    p.add_argument("--ai-key", default=os.getenv("OLLAMAFREEAPI_KEY", ""), help="API key/token")
    p.add_argument("--ai-model", default=os.getenv("OLLAMAFREEAPI_MODEL", "gpt-4o-mini"), help="Model name")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if not args.ai_url:
        print("error: provide --ai-url or set OLLAMAFREEAPI_URL", file=sys.stderr)
        return 2

    mod_id = sanitize_mod_id(args.mod_id)
    template_dir = Path(args.template_dir).resolve()
    output_dir = Path(args.output_dir).resolve()

    try:
        ensure_template(template_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        web_context = fetch_web_context(args.prompt)
        ai_code = ollamafreeapi_chat(args.prompt, web_context, args.ai_url, args.ai_key, args.ai_model)
        jar_path = build_mod(template_dir, output_dir, mod_id, ai_code)

        print("Build complete")
        print(f"Mod ID: {mod_id}")
        print(f"JAR: {jar_path}")
        return 0
    except (urllib.error.URLError, TimeoutError) as exc:
        print(f"error: network request failed: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
