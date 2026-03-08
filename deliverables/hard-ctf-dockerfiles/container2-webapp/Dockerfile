FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    nginx \
    php8.1-fpm \
    php8.1-sqlite3 \
    sqlite3 \
    steghide \
    openssl \
    && rm -rf /var/lib/apt/lists/*

# ── Web root ───────────────────────────────────────────────────────────────────
RUN mkdir -p /var/www/html/secret

# ── SQLite database ────────────────────────────────────────────────────────────
COPY setup_db.sh /tmp/setup_db.sh
RUN chmod +x /tmp/setup_db.sh && /tmp/setup_db.sh

# ── PHP application files ──────────────────────────────────────────────────────
COPY index.php     /var/www/html/index.php
COPY admin.php     /var/www/html/admin.php
COPY style.css     /var/www/html/style.css

# ── /secret/ directory contents ───────────────────────────────────────────────
# ops_briefing.jpg: placeholder image with flag embedded via steghide
# shadow.bak: SHA-512 crypt hash of P@ssw0rd123
COPY ops_briefing.jpg /var/www/html/secret/ops_briefing.jpg
COPY shadow.bak       /var/www/html/secret/shadow.bak

# Embed the steghide payload into ops_briefing.jpg at build time
# The extracted file will contain the Stage 5 flag + Stage 6 SSH credentials
COPY stego_payload.txt /tmp/stego_payload.txt
RUN steghide embed -cf /var/www/html/secret/ops_briefing.jpg \
    -sf /tmp/stego_payload.txt \
    -p "P@ssw0rd123" -f && \
    rm /tmp/stego_payload.txt

# Permissions
RUN chown -R www-data:www-data /var/www/html && \
    find /var/www/html -type f -exec chmod 644 {} \; && \
    find /var/www/html -type d -exec chmod 755 {} \;

# ── nginx config ───────────────────────────────────────────────────────────────
COPY nginx.conf /etc/nginx/sites-available/default
RUN ln -sf /etc/nginx/sites-available/default /etc/nginx/sites-enabled/default

# ── Startup script ─────────────────────────────────────────────────────────────
COPY start.sh /start.sh
RUN chmod +x /start.sh

EXPOSE 80
CMD ["/start.sh"]
