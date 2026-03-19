#!/usr/bin/env python3
"""
Telegram → FidoNet bridge bot.
Reposts new channel posts to a FidoNet echo area via hpt post.
Requires: bot as channel admin, TELEGRAM_BOT_TOKEN, FIDO_ECHO_AREA in env.
"""

import os
import subprocess
import tempfile
import logging
from datetime import datetime

from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
FIDO_ECHO_AREA = os.environ.get("FIDO_ECHO_AREA", "NICKMITIN.SAYS")
FIDO_SENDER_NAME = os.environ.get("FIDO_SENDER_NAME", "TG-Bot")
TELEGRAM_CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID")  # optional filter, e.g. -100123456


def post_to_fido(subject: str, body: str) -> bool:
    """Run hpt post to add message to echo area."""
    if not body.strip():
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
            # Container runs as fido user; hpt reads config from /etc/husky
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
                env={**os.environ, "FIDOCONFIG": "/etc/husky"},
            )
            if result.returncode != 0:
                logger.error("hpt post failed: %s %s", result.stderr, result.stdout)
                return False
            logger.info("Posted to %s: %s", FIDO_ECHO_AREA, subject[:40])
            return True
        finally:
            os.unlink(tmp_path)
    except Exception as e:
        logger.exception("post_to_fido error: %s", e)
        return False


def _get_post(update: Update):
    """Get channel post (new or edited)."""
    return update.channel_post or update.edited_channel_post


async def channel_post_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle new or edited channel post — repost to FidoNet echo."""
    msg = _get_post(update)
    if not msg:
        return
    if TELEGRAM_CHANNEL_ID and str(msg.chat.id) != str(TELEGRAM_CHANNEL_ID):
        return
    text = msg.text or msg.caption
    if not text:
        logger.info("Skipping post without text (e.g. media-only)")
        return
    # First line or first 72 chars as subject
    lines = text.strip().split("\n")
    subject = (lines[0][:72] if lines else "Re: Telegram") or "Re: Telegram"
    if not post_to_fido(subject, text):
        logger.warning("Failed to repost: %s", subject[:40])


def main() -> None:
    if not TELEGRAM_BOT_TOKEN:
        raise SystemExit("Set TELEGRAM_BOT_TOKEN in environment")
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(
        MessageHandler(filters.UpdateType.CHANNEL_POST, channel_post_handler)
    )
    app.add_handler(
        MessageHandler(filters.UpdateType.EDITED_CHANNEL_POST, channel_post_handler)
    )
    logger.info("Starting bot, reposting to echo %s", FIDO_ECHO_AREA)
    app.run_polling(allowed_updates=[Update.CHANNEL_POST, Update.EDITED_CHANNEL_POST])


if __name__ == "__main__":
    main()
