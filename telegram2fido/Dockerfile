# Extends Fidian with Python + Telegram bot
FROM stimpy23/fidian:latest

COPY requirements.txt /tmp/requirements.txt
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-venv \
    python3-pip \
    && python3 -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir -r /tmp/requirements.txt \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY bot.py /usr/local/bin/telegram2fido.py
COPY fetch_latest_posts.py /usr/local/bin/fetch_latest_posts.py
RUN chmod +x /usr/local/bin/telegram2fido.py /usr/local/bin/fetch_latest_posts.py

CMD ["/opt/venv/bin/python", "/usr/local/bin/telegram2fido.py"]
