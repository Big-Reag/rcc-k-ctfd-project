=====================================================
  OPERATION CYBER STORM — OPERATOR DIVISION
  KALI LINUX SHARED ATTACK BOX
=====================================================

Welcome, Operator. This is your dedicated Kali Linux
environment for the duration of the event.

YOUR CREDENTIALS:
  Username: op[N]    (as assigned at check-in)
  Password: CyberStorm[N]!

FILES IN THIS DIRECTORY:
  stage2_capture.pcap   - Network capture for Stage 2 (PCAP Forensics)
  README.txt            - This file

ALL CHALLENGE URLS ARE PROVIDED IN CTFd.
  Log into CTFd to get the IP/port for each challenge container.

TOOL REFERENCE:
  Splunk Web (Stage 1):   http://[splunk-ip]:8000
  Web app (Stage 3+4):    http://[webapp-ip]/
  Stage 6 SSH:            ssh ctfuser@[privesc-ip]  (creds from Stage 5)

QUICK COMMANDS:
  gobuster dir -u http://TARGET/ -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -x .bak,.jpg
  john shadow.bak --wordlist=/usr/share/wordlists/rockyou.txt
  steghide extract -sf image.jpg
  wireshark stage2_capture.pcap &
  tshark -r stage2_capture.pcap -Y 'http'
  sqlmap -u "http://TARGET/" --forms --dump

RULES:
  - Attack only designated challenge IPs listed on CTFd
  - Do not attack CTFd itself
  - Do not access other participants' home directories
  - No lateral movement from the Stage 6 privesc box

Good hunting.
=====================================================
