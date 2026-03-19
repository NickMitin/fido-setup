FROM stimpy23/fidian:latest

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY md2fido/post_from_md.py /usr/local/bin/post_from_md.py
COPY posts /posts
RUN chmod +x /usr/local/bin/post_from_md.py && mkdir -p /posts/posted

# Run every 2 minutes
CMD ["/bin/sh", "-c", "while true; do python3 /usr/local/bin/post_from_md.py; sleep 120; done"]
