#!/usr/bin/env python3
"""harvest_agent_stacks_api.py — Static Data Covenant harvester for the
loadDynamicStacks/createStackTemplate fallback path in index.html.

That path is a manifest.json-unavailable fallback that fetched, from the
visitor's browser: the agent_stacks/ directory listing, each stack's
metadata.json, and each stack's files/ directory — all via unauthenticated
GitHub "contents" API calls. It now reads committed snapshots under
data/api/contents/ instead, in the identical GitHub contents-API response
shape, so the page's parsing code (atob(metadata.content), etc.) is
unchanged — only the fetch URLs moved.

This is a *local* harvest: CI already has the full repo checked out, so this
script builds the contents-API shape by walking agent_stacks/ on disk. No
network call, no rate limit, no api.github.com dependency.

Layout (mirrors the API path the page used to build, plus a trailing
_listing.json for directory listings so a directory and same-named file
snapshot never collide):
  data/api/contents/agent_stacks/_listing.json                     (dir listing)
  data/api/contents/agent_stacks/<industry>/<stack>/metadata.json  (file, API-wrapped)
  data/api/contents/agent_stacks/<industry>/<stack>/files/_listing.json  (dir listing, only if files/ exists)
"""

import base64
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STACKS_PATH = "agent_stacks"
STACKS_DIR = ROOT / STACKS_PATH
OUT_ROOT = ROOT / "data" / "api" / "contents"
REPO = "kody-w/AI-Agent-Templates-Pilot"
BRANCH = "main"


def git_blob_sha(path: Path) -> str:
    try:
        return subprocess.run(
            ["git", "hash-object", str(path)],
            cwd=ROOT, capture_output=True, text=True, check=True
        ).stdout.strip()
    except Exception:
        return hashlib.sha1(path.read_bytes()).hexdigest()


def dir_entry(path: Path, rel: str) -> dict:
    is_dir = path.is_dir()
    size = 0 if is_dir else path.stat().st_size
    sha = "" if is_dir else git_blob_sha(path)
    return {
        "name": path.name,
        "path": rel,
        "sha": sha,
        "size": size,
        "url": f"https://api.github.com/repos/{REPO}/contents/{rel}?ref={BRANCH}",
        "html_url": f"https://github.com/{REPO}/blob/{BRANCH}/{rel}" if not is_dir else f"https://github.com/{REPO}/tree/{BRANCH}/{rel}",
        "git_url": f"https://api.github.com/repos/{REPO}/git/trees/{sha}",
        "download_url": None if is_dir else f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/{rel}",
        "type": "dir" if is_dir else "file",
    }


def write_dir_listing(dir_path: Path, rel: str):
    entries = sorted(dir_path.iterdir(), key=lambda p: p.name)
    listing = [dir_entry(p, f"{rel}/{p.name}") for p in entries]
    out = OUT_ROOT / rel / "_listing.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(listing, indent=1) + "\n")
    return out


def write_file_wrapper(file_path: Path, rel: str):
    content = file_path.read_bytes()
    wrapper = dir_entry(file_path, rel)
    wrapper["content"] = base64.b64encode(content).decode("ascii")
    wrapper["encoding"] = "base64"
    out = OUT_ROOT / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(wrapper, indent=1) + "\n")
    return out


def main():
    if not STACKS_DIR.is_dir():
        print(f"✗ {STACKS_PATH}/ not found", file=sys.stderr)
        return 1

    written = 0

    # Top-level agent_stacks/ listing (industries)
    write_dir_listing(STACKS_DIR, STACKS_PATH)
    written += 1

    for industry_dir in sorted(p for p in STACKS_DIR.iterdir() if p.is_dir()):
        for stack_dir in sorted(p for p in industry_dir.iterdir() if p.is_dir()):
            rel = f"{STACKS_PATH}/{industry_dir.name}/{stack_dir.name}"

            metadata_file = stack_dir / "metadata.json"
            if metadata_file.is_file():
                write_file_wrapper(metadata_file, f"{rel}/metadata.json")
                written += 1

            files_dir = stack_dir / "files"
            if files_dir.is_dir():
                write_dir_listing(files_dir, f"{rel}/files")
                written += 1

    print(f"✓ {written} contents-API snapshot(s) harvested from {STACKS_PATH}/ into {OUT_ROOT.relative_to(ROOT)}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
