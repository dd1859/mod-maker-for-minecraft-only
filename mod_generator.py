#!/usr/bin/env python3
"""Tkinter UI for generating and building Minecraft Forge mods."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import threading
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path
from tkinter import END, Button, Entry, Label, StringVar, Text, Tk, messagebox

API_URL = "https://api.openai.com/v1/chat/completions"
MODEL = "gpt-4o-mini"
DEFAULT_CONTEXT = "Minecraft Forge modding context"


def sanitize_mod_id(mod_id: str) -> str:
    mod_id = re.sub(r"[^a-z0-9_]", "", mod_id.lower().strip())
    return (mod_id or "generatedmod")[:50]


def http_get_json(url: str, timeout: int = 20) -> dict:
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as res:
        return json.loads(res.read().decode("utf-8"))


def http_post_json(url: str, payload: dict, headers: dict, timeout: int = 90) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as res:
        return json.loads(res.read().decode("utf-8"))


def fetch_web_context(prompt: str) -> str:
    q = urllib.parse.quote_plus(f"Minecraft Forge mod example {prompt}")
    url = f"https://api.duckduckgo.com/?q={q}&format=json"
    try:
        data = http_get_json(url)
        return data.get("AbstractText") or DEFAULT_CONTEXT
    except Exception:
        return DEFAULT_CONTEXT


def generate_ai_java(prompt: str, context: str, api_key: str) -> str:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Generate valid Java for a Minecraft Forge mod. "
                    "Return Java source only, no markdown. "
                    f"Context: {context}"
                ),
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
    }
    data = http_post_json(API_URL, payload, headers)
    out = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
    if not out:
        raise RuntimeError("AI response was empty")
    return out


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
    required = [template_dir / "build.gradle", template_dir / "gradlew"]
    missing = [str(p) for p in required if not p.exists()]
    if missing:
        raise FileNotFoundError("Missing template files: " + ", ".join(missing))


def build_project(template_dir: Path, output_dir: Path, mod_id: str, ai_java: str) -> Path:
    build_id = uuid.uuid4().hex[:12]
    project_dir = output_dir / build_id
    shutil.copytree(template_dir, project_dir)

    src = project_dir / "src" / "main" / "java" / "com" / "example" / mod_id
    src.mkdir(parents=True, exist_ok=True)
    (src / "MainMod.java").write_text(base_class(mod_id), encoding="utf-8")
    (src / "GeneratedContent.java").write_text(ai_java, encoding="utf-8")

    gradlew = "gradlew.bat" if os.name == "nt" else "./gradlew"
    run = subprocess.run(
        [gradlew, "build"],
        cwd=project_dir,
        capture_output=True,
        text=True,
        check=False,
        timeout=900,
    )
    if run.returncode != 0:
        tail = (run.stdout + "\n" + run.stderr)[-4000:]
        raise RuntimeError(f"Gradle build failed:\n{tail}")

    jars = sorted((project_dir / "build" / "libs").glob("*.jar"))
    if not jars:
        raise RuntimeError("No jar found in build/libs after successful build")

    meta = {
        "build_id": build_id,
        "mod_id": mod_id,
        "project_dir": str(project_dir),
        "jar": str(jars[0]),
    }
    (project_dir / "build_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return jars[0]


def run_generator(api_key: str, prompt: str, mod_id: str, log: Text, button: Button) -> None:
    def worker() -> None:
        try:
            template = Path("template").resolve()
            output = Path("generated_mods").resolve()
            ensure_template(template)
            output.mkdir(parents=True, exist_ok=True)

            clean_mod_id = sanitize_mod_id(mod_id)
            log.insert(END, "Fetching web context...\n")
            context = fetch_web_context(prompt)

            log.insert(END, "Generating Java with OpenAI...\n")
            java_code = generate_ai_java(prompt, context, api_key)

            log.insert(END, "Running Gradle build...\n")
            jar_path = build_project(template, output, clean_mod_id, java_code)

            log.insert(END, f"Done! JAR: {jar_path}\n")
            messagebox.showinfo("Success", f"Build complete\n\nJAR:\n{jar_path}")
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="ignore") if hasattr(e, "read") else ""
            log.insert(END, f"HTTP error {e.code}: {e.reason}\n{body}\n")
            messagebox.showerror("HTTP Error", f"{e.code} {e.reason}")
        except Exception as e:
            log.insert(END, f"Error: {e}\n")
            messagebox.showerror("Error", str(e))
        finally:
            button.config(state="normal")

    button.config(state="disabled")
    threading.Thread(target=worker, daemon=True).start()


def main() -> None:
    app = Tk()
    app.title("AI Minecraft Mod Generator")
    app.geometry("780x560")

    api_key_var = StringVar()
    mod_id_var = StringVar(value="generatedmod")

    Label(app, text="OpenAI API Key:").pack(anchor="w", padx=12, pady=(12, 2))
    Entry(app, textvariable=api_key_var, show="*", width=90).pack(anchor="w", padx=12)

    Label(app, text="Mod ID:").pack(anchor="w", padx=12, pady=(10, 2))
    Entry(app, textvariable=mod_id_var, width=45).pack(anchor="w", padx=12)

    Label(app, text="Prompt:").pack(anchor="w", padx=12, pady=(10, 2))
    prompt_box = Text(app, height=10, width=90)
    prompt_box.insert(END, "Create a glowing ore block that drops XP.")
    prompt_box.pack(padx=12)

    Label(app, text="Logs:").pack(anchor="w", padx=12, pady=(10, 2))
    log_box = Text(app, height=12, width=90)
    log_box.pack(padx=12, pady=(0, 12))

    def on_generate() -> None:
        api_key = api_key_var.get().strip()
        prompt = prompt_box.get("1.0", END).strip()
        mod_id = mod_id_var.get().strip()

        if not api_key:
            messagebox.showerror("Missing Key", "Please enter your API key.")
            return
        if not prompt:
            messagebox.showerror("Missing Prompt", "Please enter a prompt.")
            return

        log_box.insert(END, "Starting generation...\n")
        run_generator(api_key, prompt, mod_id, log_box, generate_btn)

    generate_btn = Button(app, text="Generate + Build", command=on_generate)
    generate_btn.pack(pady=(0, 10))

    app.mainloop()


if __name__ == "__main__":
    main()
