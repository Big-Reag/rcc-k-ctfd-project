#!/usr/bin/env python3
"""
Operation Cyber Storm — Stage 2 PCAP Generator
Produces stage2_capture.pcap for the Operator Division PCAP forensics challenge.

No external dependencies — writes raw pcap format using struct.

What's in the PCAP:
  - ~800 packets of background HTTP noise (GET requests to legit sites)
  - One cleartext HTTP POST with credentials in the body
  - One cleartext HTTP GET with the flag embedded in a URL parameter
  - Some DNS queries mixed in for realism

Flag: FLAG{pcap_cr3ds_3xtr4ct3d}

How participants find it:
  Wireshark: filter http, follow TCP stream on POST/GET to target host
  tshark: tshark -r stage2_capture.pcap -Y 'http' -T fields -e http.request.uri
"""

import struct
import random
import os

random.seed(1337)
OUTPUT = os.path.join(os.path.dirname(__file__), "stage2_capture.pcap")

# ── Raw PCAP helpers ───────────────────────────────────────────────────────────
PCAP_GLOBAL_HDR = struct.pack(
    "<IHHiIII",
    0xa1b2c3d4,  # magic
    2, 4,        # version
    0,           # timezone
    0,           # accuracy
    65535,       # snaplen
    1,           # link type: Ethernet
)

def pcap_packet(ts_sec, ts_usec, data):
    return struct.pack("<IIII", ts_sec, ts_usec, len(data), len(data)) + data

def eth_frame(src_mac, dst_mac, payload, ethertype=0x0800):
    return (
        bytes.fromhex(dst_mac.replace(":", ""))
        + bytes.fromhex(src_mac.replace(":", ""))
        + struct.pack(">H", ethertype)
        + payload
    )

def ip_packet(src_ip, dst_ip, protocol, payload, ip_id=None):
    if ip_id is None:
        ip_id = random.randint(0x1000, 0xFFFF)
    src = bytes(map(int, src_ip.split(".")))
    dst = bytes(map(int, dst_ip.split(".")))
    ihl = 5
    total_len = 4 * ihl + len(payload)
    hdr = struct.pack(">BBHHHBBH4s4s",
        (4 << 4) | ihl, 0,       # version/ihl, dscp
        total_len,
        ip_id, 0x4000,            # id, flags+frag (DF)
        64, protocol, 0,          # ttl, proto, checksum placeholder
        src, dst
    )
    # compute checksum
    words = struct.unpack(">10H", hdr)
    csum = sum(words)
    csum = (csum >> 16) + (csum & 0xFFFF)
    csum = ~csum & 0xFFFF
    hdr = hdr[:10] + struct.pack(">H", csum) + hdr[12:]
    return hdr + payload

def tcp_segment(src_port, dst_port, seq, ack, flags, payload=b"", window=65535):
    # flags: 0x02=SYN 0x10=ACK 0x18=PSH+ACK 0x01=FIN+ACK 0x11=FIN+ACK
    offset = 5 << 4  # data offset = 5 (no options)
    hdr = struct.pack(">HHIIBBHHH",
        src_port, dst_port,
        seq, ack,
        offset, flags,
        window, 0, 0   # checksum/urgent placeholder
    )
    return hdr + payload

def udp_segment(src_port, dst_port, payload):
    length = 8 + len(payload)
    hdr = struct.pack(">HHHH", src_port, dst_port, length, 0)
    return hdr + payload

# ── Network topology ───────────────────────────────────────────────────────────
CLIENT_IP   = "10.10.14.22"   # the compromised internal host (same as C2 source)
SERVER_IP   = "192.168.50.10" # internal web server being attacked
ATTACKER_IP = "203.0.113.47"  # external IP — same as brute-force IP from log gen
DNS_SERVER  = "10.10.1.1"

CLIENT_MAC  = "00:1a:2b:3c:4d:5e"
SERVER_MAC  = "00:de:ad:be:ef:01"
GW_MAC      = "00:50:56:aa:bb:cc"

BASE_TS = 1727740800  # 2024-10-01 00:00:00 UTC

packets = []
t = BASE_TS
seq_c = 0x10000000
seq_s = 0x20000000

def add_pkt(ts_usec_offset, eth_data):
    global t
    sec = t + ts_usec_offset // 1_000_000
    usec = ts_usec_offset % 1_000_000
    packets.append(pcap_packet(sec, usec, eth_data))

def http_get_noise(src_ip, dst_ip, host, path, ts_offset):
    """Generate a simple HTTP GET exchange (SYN, GET, response skeleton)."""
    sport = random.randint(40000, 60000)
    payload = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n".encode()
    response = f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: 42\r\n\r\n<html><body>OK</body></html>".encode()
    # SYN
    seg = tcp_segment(sport, 80, seq_c, 0, 0x02)
    add_pkt(ts_offset,     eth_frame(CLIENT_MAC, GW_MAC,   ip_packet(src_ip, dst_ip, 6, seg)))
    # SYN-ACK
    seg = tcp_segment(80, sport, seq_s, seq_c+1, 0x12)
    add_pkt(ts_offset+500, eth_frame(SERVER_MAC, CLIENT_MAC, ip_packet(dst_ip, src_ip, 6, seg)))
    # GET
    seg = tcp_segment(sport, 80, seq_c+1, seq_s+1, 0x18, payload)
    add_pkt(ts_offset+1000, eth_frame(CLIENT_MAC, GW_MAC, ip_packet(src_ip, dst_ip, 6, seg)))
    # Response
    seg = tcp_segment(80, sport, seq_s+1, seq_c+1+len(payload), 0x18, response)
    add_pkt(ts_offset+5000, eth_frame(SERVER_MAC, CLIENT_MAC, ip_packet(dst_ip, src_ip, 6, seg)))

# ── Background noise: ~100 HTTP GETs to various hosts ─────────────────────────
noise_hosts = [
    ("windowsupdate.com", "/updates/v3"),
    ("microsoft.com", "/"),
    ("office365.com", "/api/status"),
    ("azure.com", "/health"),
    ("army.mil", "/index.html"),
]
for i in range(100):
    host, path = random.choice(noise_hosts)
    dst = f"104.{random.randint(16,31)}.{random.randint(1,254)}.{random.randint(1,254)}"
    http_get_noise(CLIENT_IP, dst, host, path, i * 150_000)

current_offset = 100 * 150_000 + 500_000  # ~16 seconds in

# ── DNS query for the target server (pre-attack recon) ────────────────────────
dns_query = (
    b'\xab\xcd'          # transaction ID
    b'\x01\x00'          # flags: standard query
    b'\x00\x01'          # questions: 1
    b'\x00\x00\x00\x00\x00\x00'  # answers/auth/additional: 0
    b'\x08internal\x06server\x05local\x00'  # qname: internal.server.local
    b'\x00\x01\x00\x01'  # type A, class IN
)
seg = udp_segment(random.randint(40000,60000), 53, dns_query)
add_pkt(current_offset, eth_frame(CLIENT_MAC, GW_MAC, ip_packet(CLIENT_IP, DNS_SERVER, 17, seg)))
current_offset += 2_000_000

# ── THE KEY EXCHANGE: HTTP POST with credentials ──────────────────────────────
# Participant must follow this TCP stream to find embedded creds
sport_creds = 51337
creds_payload = (
    b"POST /login HTTP/1.1\r\n"
    b"Host: 192.168.50.10\r\n"
    b"Content-Type: application/x-www-form-urlencoded\r\n"
    b"Content-Length: 43\r\n"
    b"User-Agent: curl/7.81.0\r\n"
    b"Accept: */*\r\n"
    b"\r\n"
    b"username=sysadmin&password=P%40ssw0rd123"
)
creds_response = (
    b"HTTP/1.1 302 Found\r\n"
    b"Location: /admin\r\n"
    b"Set-Cookie: session=eyJhbGciOiJIUzI1NiJ9.admin; Path=/\r\n"
    b"Content-Length: 0\r\n"
    b"\r\n"
)

# TCP handshake for creds stream
seg = tcp_segment(sport_creds, 80, 0xAA000001, 0, 0x02)
add_pkt(current_offset,         eth_frame(CLIENT_MAC, GW_MAC,     ip_packet(CLIENT_IP, SERVER_IP, 6, seg)))
seg = tcp_segment(80, sport_creds, 0xBB000001, 0xAA000002, 0x12)
add_pkt(current_offset+300,     eth_frame(SERVER_MAC, CLIENT_MAC, ip_packet(SERVER_IP, CLIENT_IP, 6, seg)))
seg = tcp_segment(sport_creds, 80, 0xAA000002, 0xBB000002, 0x10)
add_pkt(current_offset+600,     eth_frame(CLIENT_MAC, GW_MAC,     ip_packet(CLIENT_IP, SERVER_IP, 6, seg)))
# POST with creds
seg = tcp_segment(sport_creds, 80, 0xAA000002, 0xBB000002, 0x18, creds_payload)
add_pkt(current_offset+1_000,   eth_frame(CLIENT_MAC, GW_MAC,     ip_packet(CLIENT_IP, SERVER_IP, 6, seg)))
# Server 302 response
seg = tcp_segment(80, sport_creds, 0xBB000002, 0xAA000002+len(creds_payload), 0x18, creds_response)
add_pkt(current_offset+5_000,   eth_frame(SERVER_MAC, CLIENT_MAC, ip_packet(SERVER_IP, CLIENT_IP, 6, seg)))
current_offset += 3_000_000

# ── THE FLAG: HTTP GET with flag in URL parameter ─────────────────────────────
sport_flag = 51338
flag_path = b"/api/v1/exfil?token=FLAG%7Bpcap_cr3ds_3xtr4ct3d%7D&host=xf3b2a.cloudflareupdate.net"
flag_request = (
    b"GET " + flag_path + b" HTTP/1.1\r\n"
    b"Host: 192.168.50.10\r\n"
    b"Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.admin\r\n"
    b"User-Agent: curl/7.81.0\r\n"
    b"\r\n"
)
flag_response = (
    b"HTTP/1.1 200 OK\r\n"
    b"Content-Type: application/json\r\n"
    b"Content-Length: 16\r\n"
    b"\r\n"
    b'{"status":"ok"}'
)

seg = tcp_segment(sport_flag, 80, 0xCC000001, 0, 0x02)
add_pkt(current_offset,         eth_frame(CLIENT_MAC, GW_MAC,     ip_packet(CLIENT_IP, SERVER_IP, 6, seg)))
seg = tcp_segment(80, sport_flag, 0xDD000001, 0xCC000002, 0x12)
add_pkt(current_offset+300,     eth_frame(SERVER_MAC, CLIENT_MAC, ip_packet(SERVER_IP, CLIENT_IP, 6, seg)))
seg = tcp_segment(sport_flag, 80, 0xCC000002, 0xDD000002, 0x10)
add_pkt(current_offset+600,     eth_frame(CLIENT_MAC, GW_MAC,     ip_packet(CLIENT_IP, SERVER_IP, 6, seg)))
seg = tcp_segment(sport_flag, 80, 0xCC000002, 0xDD000002, 0x18, flag_request)
add_pkt(current_offset+1_000,   eth_frame(CLIENT_MAC, GW_MAC,     ip_packet(CLIENT_IP, SERVER_IP, 6, seg)))
seg = tcp_segment(80, sport_flag, 0xDD000002, 0xCC000002+len(flag_request), 0x18, flag_response)
add_pkt(current_offset+5_000,   eth_frame(SERVER_MAC, CLIENT_MAC, ip_packet(SERVER_IP, CLIENT_IP, 6, seg)))
current_offset += 3_000_000

# ── More background noise after the key events ────────────────────────────────
for i in range(50):
    host, path = random.choice(noise_hosts)
    dst = f"104.{random.randint(16,31)}.{random.randint(1,254)}.{random.randint(1,254)}"
    http_get_noise(CLIENT_IP, dst, host, path, current_offset + i * 120_000)

# ── Write PCAP ────────────────────────────────────────────────────────────────
with open(OUTPUT, "wb") as f:
    f.write(PCAP_GLOBAL_HDR)
    for pkt in packets:
        f.write(pkt)

sz = os.path.getsize(OUTPUT)
print(f"stage2_capture.pcap written: {sz:,} bytes ({sz/1024:.1f} KB)")
print(f"Total packets: {len(packets)}")
print()
print("Challenge solution:")
print("  Wireshark filter: http")
print("  Follow TCP stream on the POST to 192.168.50.10")
print("  Credentials found: username=sysadmin&password=P%40ssw0rd123")
print("  Flag found in GET: /api/v1/exfil?token=FLAG{pcap_cr3ds_3xtr4ct3d}")
