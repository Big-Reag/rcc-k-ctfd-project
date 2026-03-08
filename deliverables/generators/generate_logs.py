#!/usr/bin/env python3
"""
Operation Cyber Storm — Synthetic Log Generator
Generates ~500MB of realistic enterprise logs for Container 1 (Splunk).

Output files (written to ./logs/):
  dns_queries.log      - DNS query logs with planted C2 domain
  web_access.log       - Apache-style HTTP access log
  auth.log             - Linux PAM/sshd authentication log
  syslog.log           - Generic syslog entries

C2 domain: xf3b2a.cloudflareupdate.net  (obviously fake, educational use)
Flag embedded in: DNS query log — the C2 domain beacon entries
Flag value: FLAG{c2_d0m41n_1d3nt1f13d}

How participants find it:
  index=* sourcetype=dns | stats count by query | sort -count
  The C2 domain appears ~8 times over 30 days (realistic beacon frequency).
  All legitimate domains appear 100s-1000s of times. Outlier is obvious.
"""

import random
import os
import datetime

random.seed(42)
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Configuration ─────────────────────────────────────────────────────────────
START_DATE = datetime.datetime(2024, 10, 1, 0, 0, 0)
END_DATE   = datetime.datetime(2024, 10, 30, 23, 59, 59)
TOTAL_DAYS = 30

C2_DOMAIN  = "xf3b2a.cloudflareupdate.net"
C2_BEACON_TIMES = [  # exact timestamps when C2 beacon fires — low freq, irregular
    datetime.datetime(2024, 10,  3, 2, 17, 44),
    datetime.datetime(2024, 10,  7, 3, 52, 11),
    datetime.datetime(2024, 10, 11, 1,  8, 33),
    datetime.datetime(2024, 10, 14, 4, 41, 55),
    datetime.datetime(2024, 10, 18, 2, 29,  7),
    datetime.datetime(2024, 10, 21, 3, 14, 22),
    datetime.datetime(2024, 10, 25, 1, 55, 48),
    datetime.datetime(2024, 10, 28, 4,  3, 16),
]
C2_SOURCE_IP = "10.10.14.22"  # the internal host that was compromised

# Legitimate domain pool — high frequency background noise
LEGIT_DOMAINS = [
    ("google.com",              800),
    ("microsoft.com",           600),
    ("windowsupdate.com",       500),
    ("office365.com",           700),
    ("teams.microsoft.com",     650),
    ("outlook.com",             400),
    ("azure.com",               350),
    ("akamaiedge.net",          300),
    ("cloudfront.net",          280),
    ("amazonaws.com",           450),
    ("army.mil",                200),
    ("disa.mil",                180),
    ("cdn.jsdelivr.net",        150),
    ("fonts.googleapis.com",    120),
    ("api.github.com",          100),
    ("ocsp.digicert.com",        90),
    ("crl.microsoft.com",       110),
    ("ctldl.windowsupdate.com",  80),
    ("login.microsoftonline.com",300),
    ("graph.microsoft.com",     260),
]

INTERNAL_HOSTS = [f"10.10.{random.randint(1,14)}.{random.randint(2,254)}" for _ in range(80)]
INTERNAL_HOSTS += [C2_SOURCE_IP]

USERNAMES = ["jsmith", "adavis", "mwilson", "tlee", "rgarcia", "kpatel",
             "ljohnson", "bwilliams", "aanderson", "cmartinez",
             "sysadmin", "ctfadmin", "noc_monitor", "backup_svc"]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0",
    "Microsoft-WNS/10.0",
    "Windows-Update-Agent/10.0.10011.16384",
    "Microsoft NCSI",
    "curl/7.81.0",
]

WEB_PATHS = [
    ("/", 200), ("/index.html", 200), ("/login", 200), ("/dashboard", 200),
    ("/api/v1/status", 200), ("/api/v1/users", 200), ("/static/app.js", 200),
    ("/static/style.css", 200), ("/favicon.ico", 200), ("/robots.txt", 200),
    ("/admin", 403), ("/phpmyadmin", 404), ("/.env", 404), ("/wp-admin", 404),
    ("/api/v1/logout", 200), ("/api/v1/search", 200),
]

def rand_ts(start, end):
    delta = end - start
    secs = random.randint(0, int(delta.total_seconds()))
    return start + datetime.timedelta(seconds=secs)

def fmt_ts(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def fmt_syslog_ts(dt):
    return dt.strftime("%b %d %H:%M:%S")

def fmt_apache_ts(dt):
    return dt.strftime("%d/%b/%Y:%H:%M:%S +0000")

# ── Generator 1: DNS Query Log ─────────────────────────────────────────────────
print("Generating dns_queries.log...")
dns_lines = []

# Background legitimate queries
for domain, weight in LEGIT_DOMAINS:
    count = weight * TOTAL_DAYS // 10
    for _ in range(count):
        ts = rand_ts(START_DATE, END_DATE)
        src = random.choice(INTERNAL_HOSTS)
        qtype = random.choice(["A", "A", "A", "AAAA", "CNAME", "MX"])
        dns_lines.append((ts, f'{fmt_ts(ts)} src_ip={src} query="{domain}" qtype={qtype} response_code=NOERROR answer_count=1 resolver=10.10.1.1\n'))

# C2 beacon entries — the flag is hidden in these
for ts in C2_BEACON_TIMES:
    dns_lines.append((ts, f'{fmt_ts(ts)} src_ip={C2_SOURCE_IP} query="{C2_DOMAIN}" qtype=A response_code=NOERROR answer_count=1 resolver=10.10.1.1\n'))

# Sort by timestamp and write
dns_lines.sort(key=lambda x: x[0])
with open(os.path.join(OUTPUT_DIR, "dns_queries.log"), "w") as f:
    for _, line in dns_lines:
        f.write(line)

print(f"  dns_queries.log: {len(dns_lines):,} entries")

# ── Generator 2: Web Access Log ────────────────────────────────────────────────
print("Generating web_access.log...")
web_lines = []
for _ in range(180000):
    ts = rand_ts(START_DATE, END_DATE)
    src = random.choice(INTERNAL_HOSTS)
    path, status = random.choice(WEB_PATHS)
    ua = random.choice(USER_AGENTS)
    size = random.randint(200, 48000)
    method = "GET" if status in (200, 403, 404) else "POST"
    web_lines.append((ts, f'{src} - - [{fmt_apache_ts(ts)}] "{method} {path} HTTP/1.1" {status} {size} "-" "{ua}"\n'))

web_lines.sort(key=lambda x: x[0])
with open(os.path.join(OUTPUT_DIR, "web_access.log"), "w") as f:
    for _, line in web_lines:
        f.write(line)
print(f"  web_access.log: {len(web_lines):,} entries")

# ── Generator 3: Auth Log ──────────────────────────────────────────────────────
print("Generating auth.log...")
auth_lines = []
hostnames = [f"srv-{i:02d}" for i in range(1, 12)]

for _ in range(60000):
    ts = rand_ts(START_DATE, END_DATE)
    host = random.choice(hostnames)
    user = random.choice(USERNAMES)
    src = random.choice(INTERNAL_HOSTS)
    pid = random.randint(1000, 65000)
    outcome = random.choices(["Accepted", "Failed"], weights=[85, 15])[0]
    method = "publickey" if outcome == "Accepted" else "password"
    auth_lines.append((ts, f"{fmt_syslog_ts(ts)} {host} sshd[{pid}]: {outcome} {method} for {user} from {src} port {random.randint(1024,65535)} ssh2\n"))

# Brute force cluster from external IP — adds narrative texture
brute_ip = "203.0.113.47"
brute_start = datetime.datetime(2024, 10, 14, 22, 0, 0)
for i in range(120):
    ts = brute_start + datetime.timedelta(seconds=i * 3)
    auth_lines.append((ts, f"{fmt_syslog_ts(ts)} srv-05 sshd[{random.randint(1000,65000)}]: Failed password for invalid user {random.choice(['admin','root','test','ubuntu','deploy'])} from {brute_ip} port {random.randint(30000,65000)} ssh2\n"))

# Successful login from C2 host after the brute force — adds story
post_brute = brute_start + datetime.timedelta(minutes=12)
auth_lines.append((post_brute, f"{fmt_syslog_ts(post_brute)} srv-05 sshd[{random.randint(1000,65000)}]: Accepted password for sysadmin from {C2_SOURCE_IP} port 52341 ssh2\n"))

auth_lines.sort(key=lambda x: x[0])
with open(os.path.join(OUTPUT_DIR, "auth.log"), "w") as f:
    for _, line in auth_lines:
        f.write(line)
print(f"  auth.log: {len(auth_lines):,} entries")

# ── Generator 4: Syslog (bulk filler to reach ~500MB total) ───────────────────
print("Generating syslog.log (bulk filler)...")
SYSLOG_FACILITIES = [
    "kernel", "user", "daemon", "cron", "local0", "local1"
]
SYSLOG_MSGS = [
    "systemd[1]: Started Session {} of user {}.",
    "CRON[{}]: (root) CMD ({})",
    "kernel: [{}] EXT4-fs (sda1): mounted filesystem",
    "NetworkManager[{}]: <info> device (eth0): state change: {} -> {}",
    "systemd-logind[{}]: New session {} of user {}.",
    "rsyslogd: [origin software=\"rsyslogd\" swVersion=\"8.2001.0\"] start",
    "kernel: audit: type=1400 audit({}.{}:{}): apparmor=\"ALLOWED\"",
    "puppet-agent[{}]: Applied catalog in {:.2f} seconds",
]

syslog_lines = []
for _ in range(500000):
    ts = rand_ts(START_DATE, END_DATE)
    host = random.choice(hostnames)
    msg_tpl = random.choice(SYSLOG_MSGS)
    nums = [random.randint(1, 9999) for _ in range(6)]
    floats = [random.uniform(0.1, 30.0) for _ in range(2)]
    words = ["running", "stopped", "degraded", "inactive", "active"]
    user = random.choice(USERNAMES)
    try:
        msg = msg_tpl.format(*nums[:3], user, words[nums[0]%5], floats[0])
    except (IndexError, KeyError):
        msg = msg_tpl.format(*([str(n) for n in nums] + words + [user]))
    syslog_lines.append((ts, f"{fmt_syslog_ts(ts)} {host} {msg}\n"))

syslog_lines.sort(key=lambda x: x[0])
with open(os.path.join(OUTPUT_DIR, "syslog.log"), "w") as f:
    for _, line in syslog_lines:
        f.write(line)
print(f"  syslog.log: {len(syslog_lines):,} entries")

# ── Size report ────────────────────────────────────────────────────────────────
total = 0
for fname in ["dns_queries.log", "web_access.log", "auth.log", "syslog.log"]:
    sz = os.path.getsize(os.path.join(OUTPUT_DIR, fname))
    total += sz
    print(f"  {fname}: {sz/1024/1024:.1f} MB")
print(f"  TOTAL: {total/1024/1024:.1f} MB")
print()
print(f"C2 domain beacon: '{C2_DOMAIN}'")
print(f"C2 source IP:      {C2_SOURCE_IP}")
print(f"Beacon count:      {len(C2_BEACON_TIMES)} entries over 30 days")
print(f"Flag: FLAG{{c2_d0m41n_1d3nt1f13d}}")
print()
print("Splunk SPL to find flag:")
print('  index=* sourcetype=dns | stats count by query | sort count')
print('  -- look for the outlier domain with count=8')
