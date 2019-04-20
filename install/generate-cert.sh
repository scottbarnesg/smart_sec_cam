#!/bin/bash

# Generate SSL certificate
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
# Move key and cert to correct path
auth_dir="$HOME/smart_sec_cam/auth"
if  [ ! -d "$auth_dir" ]; then
  mkdir "$auth_dir"
fi
mv cert.pem "$auth_dir"
mv key.pem "$auth_dir"
