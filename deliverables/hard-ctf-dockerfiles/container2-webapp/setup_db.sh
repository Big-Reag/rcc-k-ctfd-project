#!/bin/bash
# Generates the SHA-512 crypt hash for P@ssw0rd123 and populates the SQLite DB

set -e

DB_PATH="/var/www/html/ctf.db"
mkdir -p /var/www/html

# Generate the SHA-512 crypt hash (same as /etc/shadow format)
HASH=$(openssl passwd -6 -salt "rcckorea2024" "P@ssw0rd123")

echo "[*] Creating SQLite database at $DB_PATH"
sqlite3 "$DB_PATH" <<SQL
CREATE TABLE IF NOT EXISTS users (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    password_hash TEXT,
    role     TEXT DEFAULT 'user'
);

INSERT INTO users (username, password, password_hash, role)
VALUES ('admin', 'password123', NULL, 'admin');

INSERT INTO users (username, password, password_hash, role)
VALUES ('sysadmin', 'P@ssw0rd123', '$HASH', 'sysadmin');
SQL

echo "[*] Database created with users:"
sqlite3 "$DB_PATH" "SELECT id, username, role, password_hash FROM users;"

# Also generate shadow.bak (same hash, shadow file format)
echo "[*] Generating shadow.bak"
mkdir -p /var/www/html/secret
echo "sysadmin:${HASH}:19000:0:99999:7:::" > /var/www/html/secret/shadow.bak

echo "[*] Done"
