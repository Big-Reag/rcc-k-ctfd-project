#!/bin/bash
# Start PHP-FPM then nginx in foreground
service php8.1-fpm start
nginx -g 'daemon off;'
