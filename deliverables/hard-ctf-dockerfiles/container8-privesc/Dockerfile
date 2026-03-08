FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    openssh-server \
    python3 \
    sudo \
    findutils \
    && rm -rf /var/lib/apt/lists/*

# ── Create users ───────────────────────────────────────────────────────────────
RUN useradd -m -s /bin/bash ctfuser && \
    echo "ctfuser:Str0ng3rThanY0u" | chpasswd

# ── Plant the flag (root-owned, root-readable only) ───────────────────────────
RUN echo "FLAG{r00t_4cc3ss_4ch13v3d}" > /root/flag.txt && \
    chmod 600 /root/flag.txt

# ── Escalation Path A: misconfigured sudo rule ────────────────────────────────
# ctfuser can run /usr/bin/find as root without password
# GTFOBins: sudo find . -exec /bin/bash \; -quit
RUN echo "ctfuser ALL=(ALL) NOPASSWD: /usr/bin/find" \
    > /etc/sudoers.d/ctfuser && \
    chmod 440 /etc/sudoers.d/ctfuser

# ── Escalation Path B: SUID python3 (stretch path) ───────────────────────────
# GTFOBins: python3 -c 'import os; os.execl("/bin/sh", "sh", "-p")'
RUN chmod u+s /usr/bin/python3*

# ── SSH configuration ──────────────────────────────────────────────────────────
RUN mkdir -p /var/run/sshd && \
    sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin no/' /etc/ssh/sshd_config && \
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config && \
    echo "MaxAuthTries 10" >> /etc/ssh/sshd_config

# ── Briefing for ctfuser ───────────────────────────────────────────────────────
RUN echo "You have low-privilege access to this host as ctfuser.\n\
Your mission: escalate to root and read /root/flag.txt\n\
Useful commands: sudo -l   id   find / -perm -u=s -type f 2>/dev/null" \
    > /home/ctfuser/README.txt && \
    chown ctfuser:ctfuser /home/ctfuser/README.txt

EXPOSE 22
CMD ["/usr/sbin/sshd", "-D"]
