#!/bin/bash
# File source from:
# https://github.com/Senui/src-advanced-training-docker/blob/master/init.sh

# Define the Nginx configuration file path
nginx_conf="/etc/nginx/conf.d/ssl_main.conf"

# Let Nginx serve the docker container running on port 8080 instead of a static web page
sed -i 's|root /var/www/html;|location \/ {\n    \tproxy_pass http:\/\/localhost:8080;\n    \tproxy_set_header Host $host;\n    \tproxy_set_header X-Real-IP $remote_addr;\n    }|' "$nginx_conf"
sed -i 's|index index.html index.htm;||' "$nginx_conf"

systemctl restart nginx.service
