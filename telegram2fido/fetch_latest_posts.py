#!/usr/bin/env python3
"""
One-time migration: Fetch the N latest posts from a Telegram channel
and post them to a FidoNet echo area via hpt.

Requires: Telethon, TELEGRAM_BOT_TOKEN, TELEGRAM_API_ID, TELEGRAM_API_HASH,
          TELEGRAM_CHANNEL_ID, FIDO_ECHO_AREA. Run inside the fido/telegram
          container where hpt is available.

Usage:
  docker exec -it fido-telegram-bot python3 /usr/local/bin/fetch_latest_posts.py [N]
  Default N=5.
"""

import os
import sys
import subprocess
import tempfile
import asyncio
from datetime import datetime

# Telethon for fetching channel history (Bot API cannot get past posts)
try:
    from telethon import TelegramClient
    from telethon.tl.types import Message
except ImportError:
    print("Install telethon: pip install telethon")
    sys.exit(1)


TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_API_ID = os.environ.get("TELEGRAM_API_ID")
TELEGRAM_API_HASH = os.environ.get("TELEGRAM_API_HASH")
TELEGRAM_CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID")
FIDO_ECHO_AREA = os.environ.get("FIDO_ECHO_AREA", "NICKMITIN.SAYS")
FIDO_SENDER_NAME = os.environ.get("FIDO_SENDER_NAME", "TG-Bot")
FIDOCONFIG = os.environ.get("FIDOCONFIG", "/etc/husky")


def post_to_fido(subject: str, body: str) -> bool:
    """Run hpt post to add message to echo area."""
    if not body or not body.strip():
        return False
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".txt",
            delete=False,
            encoding="utf-8",
        ) as f:
            f.write(body)
            tmp_path = f.name
        try:
            cmd = [
                "hpt", "post",
                "-s", subject[:72],
                "-e", FIDO_ECHO_AREA,
                "-nf", FIDO_SENDER_NAME,
                "-z", f"Reposted from Telegram at {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
                tmp_path,
            ]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                env={**os.environ, "FIDOCONFIG": FIDOCONFIG},
            )
            if result.returncode != 0:
                print(f"hpt post failed: {result.stderr} {result.stdout}")
                return False
            print(f"Posted to {FIDO_ECHO_AREA}: {subject[:50]}...")
            return True
        finally:
            os.unlink(tmp_path)
    except Exception as e:
        print(f"post_to_fido error: {e}")
        return False


async def main():
    limit = 5
    if len(sys.argv) > 1:
        try:
            limit = int(sys.argv[1])
        except ValueError:
            pass

    if not TELEGRAM_BOT_TOKEN:
        print("Set TELEGRAM_BOT_TOKEN in environment")
        sys.exit(1)
    if not TELEGRAM_CHANNEL_ID:
        print("Set TELEGRAM_CHANNEL_ID in environment (e.g. -1001201901113)")
        sys.exit(1)
    if not TELEGRAM_API_ID or not TELEGRAM_API_HASH:
        print("For channel history, Telethon needs API credentials from https://my.telegram.org")
        print("Set TELEGRAM_API_ID and TELEGRAM_API_HASH in environment")
        sys.exit(1)

    channel_id = int(TELEGRAM_CHANNEL_ID)
    client = TelegramClient(
        "fetch_session",
        int(TELEGRAM_API_ID),
        TELEGRAM_API_HASH,
    ).start(bot_token=TELEGRAM_BOT_TOKEN)

    try:
        messages = []
        async for msg in client.iter_messages(channel_id, limit=limit * 3):
            if not isinstance(msg, Message):
                continue
            text = getattr(msg, 'message', None) or getattr(msg, 'text', None)
            if not text or not text.strip():
                continue
            messages.append((msg.date, text))
            if len(messages) >= limit:
                break

        # Oldest first (chronological order for echo)
        messages.reverse()

        if not messages:
            print("No text posts found in the last messages.")
            return

        print(f"Found {len(messages)} posts. Posting to {FIDO_ECHO_AREA}...")

        for date, text in messages:
            lines = text.strip().split("\n")
            subject = (lines[0][:72] if lines else "Re: Telegram") or "Re: Telegram"
            post_to_fido(subject, text)

        print("Done.")
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
