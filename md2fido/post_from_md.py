#!/usr/bin/env python3
"""
Post markdown files from posts/ to FidoNet echo via hpt.
Each .md file = one post. First line = subject, full content = body.
Posted files are moved to posts/posted/.

Runs hpt inside the fido container (where Husky config exists) via docker exec.
"""

import os
import sys
import subprocess
import shutil
import uuid
from pathlib import Path
from datetime import datetime

POSTS_DIR = Path(os.environ.get("POSTS_DIR", "/posts"))
POSTED_DIR = POSTS_DIR / "posted"
FIDO_ECHO_AREA = os.environ.get("FIDO_ECHO_AREA", "NICKMITIN.SAYS")
FIDO_SENDER_NAME = os.environ.get("FIDO_SENDER_NAME", "MD-Poster")
FIDO_CONTAINER = os.environ.get("FIDO_CONTAINER", "fido-echo")
# Shared with fido container via ftn_spool volume
PENDING_DIR = Path("/var/spool/ftn/.md2fido_pending")


def post_to_fido(subject: str, body: str) -> bool:
    """Run hpt post inside fido container (has proper Husky config)."""
    if not body or not body.strip():
        return False
    try:
        PENDING_DIR.mkdir(parents=True, exist_ok=True)
        tmp_name = f"post_{uuid.uuid4().hex[:8]}.txt"
        tmp_path = PENDING_DIR / tmp_name
        tmp_path.write_text(body, encoding="utf-8")
        try:
            # hpt must run in fido container where fidoconfig/husky is set up
            cmd = [
                "docker", "exec", FIDO_CONTAINER,
                "hpt", "post",
                "-s", subject[:72],
                "-e", FIDO_ECHO_AREA,
                "-nf", FIDO_SENDER_NAME,
                "-z", f"From MD file at {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
                str(tmp_path),
            ]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode != 0:
                print(f"hpt post failed: {result.stderr} {result.stdout}", file=sys.stderr)
                return False
            return True
        finally:
            try:
                tmp_path.unlink()
            except OSError:
                pass
    except Exception as e:
        print(f"post_to_fido error: {e}", file=sys.stderr)
        return False


def main():
    POSTED_DIR.mkdir(parents=True, exist_ok=True)

    md_files = sorted(POSTS_DIR.glob("*.md"))
    # Skip README
    md_files = [f for f in md_files if f.name.upper() != "README.MD"]

    if not md_files:
        return 0

    for path in md_files:
        try:
            body = path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"Skip {path.name}: {e}", file=sys.stderr)
            continue

        lines = body.strip().split("\n")
        subject = (lines[0][:72] if lines else "Post") or "Post"

        if post_to_fido(subject, body):
            dest = POSTED_DIR / path.name
            shutil.move(str(path), str(dest))
            print(f"Posted: {path.name} -> {FIDO_ECHO_AREA}")
        else:
            print(f"Failed: {path.name}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
