FROM nginx:alpine

# Remove default content
RUN rm -rf /usr/share/nginx/html/*

# ── Recruit Stage 1: Web Recon ─────────────────────────────────────────────────
# Served at /
COPY index.html   /usr/share/nginx/html/index.html
COPY robots.txt   /usr/share/nginx/html/robots.txt

# /staging/ path — reachable via robots.txt disallow
RUN mkdir -p /usr/share/nginx/html/staging
COPY staging.html /usr/share/nginx/html/staging/index.html

# ── Recruit Stage 7: Phishing Email Analysis ───────────────────────────────────
# Served at /webmail/ — listed in robots.txt as Disallow to act as a breadcrumb
# Path is obscure enough that Stage 1 participants won't stumble on it naturally
RUN mkdir -p /usr/share/nginx/html/webmail
COPY inbox.html /usr/share/nginx/html/webmail/index.html

# ── nginx config ───────────────────────────────────────────────────────────────
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
