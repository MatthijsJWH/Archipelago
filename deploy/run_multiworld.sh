#!/bin/sh
set -e

# Populate the room-server TLS cert from Coolify's Traefik acme.json.
# Non-fatal if missing/unmatched -- rooms just fall back to plaintext ws://.
python deploy/extract_cert.py || echo "extract_cert: continuing without room TLS"

# Let's Encrypt renews the underlying cert periodically; refresh our copy
# daily so SELFLAUNCHCERT/SELFLAUNCHKEY pick up renewals (customserver.py's
# get_ssl_context() reloads from these files once per day).
(
  while true; do
    sleep 86400
    python deploy/extract_cert.py || true
  done
) &

exec python WebHost.py --config_override deploy/selflaunch.yaml
