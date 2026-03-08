FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV SPLUNK_HOME=/opt/splunk
ENV SPLUNK_START_ARGS=--accept-license
ENV SPLUNK_PASSWORD=CyberStorm2024!

# ── Dependencies ───────────────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    tar \
    && rm -rf /var/lib/apt/lists/*

# ── Download and install Splunk Free ──────────────────────────────────────────
# Using Splunk 9.x free/developer license (no login required for CTF use)
# Pin to a known stable version
RUN wget -q -O /tmp/splunk.tgz \
    "https://download.splunk.com/products/splunk/releases/9.2.1/linux/splunk-9.2.1-78803f08aabb-Linux-x86_64.tgz" && \
    tar -xzf /tmp/splunk.tgz -C /opt && \
    rm /tmp/splunk.tgz

# ── Accept license and set admin password ─────────────────────────────────────
RUN /opt/splunk/bin/splunk start --accept-license --answer-yes --no-prompt \
    --seed-passwd "${SPLUNK_PASSWORD}" && \
    /opt/splunk/bin/splunk stop

# ── Copy log files into Splunk monitored directory ────────────────────────────
RUN mkdir -p /opt/splunk/ctf_logs
COPY logs/dns_queries.log  /opt/splunk/ctf_logs/dns_queries.log
COPY logs/web_access.log   /opt/splunk/ctf_logs/web_access.log
COPY logs/auth.log         /opt/splunk/ctf_logs/auth.log
COPY logs/syslog.log       /opt/splunk/ctf_logs/syslog.log

# ── Splunk inputs.conf: tell Splunk what to index and what sourcetype ──────────
RUN mkdir -p /opt/splunk/etc/system/local
COPY inputs.conf /opt/splunk/etc/system/local/inputs.conf
COPY props.conf  /opt/splunk/etc/system/local/props.conf

# ── Pre-index at build time so participants get instant results on connect ─────
RUN /opt/splunk/bin/splunk start --accept-license --answer-yes --no-prompt && \
    sleep 30 && \
    /opt/splunk/bin/splunk add oneshot /opt/splunk/ctf_logs/dns_queries.log \
        -index ctf -sourcetype dns -auth "admin:${SPLUNK_PASSWORD}" && \
    /opt/splunk/bin/splunk add oneshot /opt/splunk/ctf_logs/web_access.log \
        -index ctf -sourcetype access_combined -auth "admin:${SPLUNK_PASSWORD}" && \
    /opt/splunk/bin/splunk add oneshot /opt/splunk/ctf_logs/auth.log \
        -index ctf -sourcetype linux_secure -auth "admin:${SPLUNK_PASSWORD}" && \
    /opt/splunk/bin/splunk add oneshot /opt/splunk/ctf_logs/syslog.log \
        -index ctf -sourcetype syslog -auth "admin:${SPLUNK_PASSWORD}" && \
    sleep 60 && \
    /opt/splunk/bin/splunk stop

# ── Splunk Web settings: disable HTTPS to simplify CTF access ─────────────────
RUN echo "[settings]" >> /opt/splunk/etc/system/local/web.conf && \
    echo "enableSplunkWebSSL = false" >> /opt/splunk/etc/system/local/web.conf && \
    echo "httpport = 8000" >> /opt/splunk/etc/system/local/web.conf

EXPOSE 8000

# Start Splunk in foreground
CMD ["/opt/splunk/bin/splunk", "start", "--nodaemon", \
     "--accept-license", "--answer-yes", "--no-prompt"]
