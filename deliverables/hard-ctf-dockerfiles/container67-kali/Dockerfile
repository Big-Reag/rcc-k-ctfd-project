FROM kalilinux/kali-rolling:latest

ENV DEBIAN_FRONTEND=noninteractive

# ── Core tool suite ────────────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y \
    openssh-server \
    sudo \
    # Web tools
    gobuster \
    dirb \
    nikto \
    curl \
    wget \
    # SQL tools
    sqlmap \
    # Password cracking
    john \
    hashcat \
    # Steganography
    steghide \
    stegseek \
    # Network / forensics
    wireshark \
    tshark \
    nmap \
    netcat-openbsd \
    # Web proxy
    burpsuite \
    # SSH / general
    net-tools \
    iputils-ping \
    dnsutils \
    python3 \
    python3-pip \
    vim \
    nano \
    git \
    file \
    binwalk \
    exiftool \
    && rm -rf /var/lib/apt/lists/*

# ── Wordlist: ensure rockyou.txt is present and uncompressed ──────────────────
RUN if [ -f /usr/share/wordlists/rockyou.txt.gz ]; then \
        gunzip /usr/share/wordlists/rockyou.txt.gz; \
    fi && \
    # Verify P@ssw0rd123 is in the list (critical for Stage 4B chain)
    grep -qF 'P@ssw0rd123' /usr/share/wordlists/rockyou.txt && \
    echo "[OK] P@ssw0rd123 confirmed in rockyou.txt" || \
    echo "P@ssw0rd123" >> /usr/share/wordlists/rockyou.txt

# ── Create 10 isolated operator accounts ──────────────────────────────────────
# op1 through op10 — each gets their own home dir, no cross-reading
RUN for i in $(seq 1 10); do \
        useradd -m -s /bin/bash "op${i}" && \
        echo "op${i}:CyberStorm${i}!" | chpasswd && \
        chmod 700 "/home/op${i}"; \
    done

# ── Stage resources pre-loaded into each home dir ────────────────────────────
# PCAP file for Stage 2 — same file for all operators
COPY stage2_capture.pcap /opt/challenges/stage2_capture.pcap
RUN chmod 644 /opt/challenges/stage2_capture.pcap

# Symlink the PCAP into each user's home (read-only reference)
RUN for i in $(seq 1 10); do \
        ln -s /opt/challenges/stage2_capture.pcap "/home/op${i}/stage2_capture.pcap"; \
    done

# ── README in each home dir ────────────────────────────────────────────────────
COPY operator_readme.txt /opt/challenges/README.txt
RUN for i in $(seq 1 10); do \
        cp /opt/challenges/README.txt "/home/op${i}/README.txt" && \
        chown "op${i}:op${i}" "/home/op${i}/README.txt"; \
    done

# ── SSH configuration ──────────────────────────────────────────────────────────
RUN mkdir -p /var/run/sshd && \
    sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin no/' /etc/ssh/sshd_config && \
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config && \
    echo "MaxAuthTries 10" >> /etc/ssh/sshd_config && \
    # Prevent users from seeing other users' processes
    echo "session optional pam_umask.so umask=0077" >> /etc/pam.d/sshd

EXPOSE 22
CMD ["/usr/sbin/sshd", "-D"]
