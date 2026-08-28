#!/bin/sh
set -e

# .apworld files placed in deploy/custom_worlds/ are copied from there into
# custom_worlds/ (where WebHost.py looks for them) on every start, since /app
# is a persistent volume that doesn't reflect deploy/ changes in newer images.
mkdir -p custom_worlds
for f in /deploy/custom_worlds/*.apworld; do
  [ -e "$f" ] && cp -f "$f" custom_worlds/
done

# Populate the room-server TLS cert from Coolify's Traefik acme.json.
# Non-fatal if missing/unmatched -- rooms just fall back to plaintext ws://.
python /deploy/extract_cert.py || echo "extract_cert: continuing without room TLS"

# Let's Encrypt renews the underlying cert periodically; refresh our copy
# daily so SELFLAUNCHCERT/SELFLAUNCHKEY pick up renewals (customserver.py's
# get_ssl_context() reloads from these files once per day).
(
  while true; do
    sleep 86400
    python /deploy/extract_cert.py || true
  done
) &

exec python WebHost.py --config_override /deploy/selflaunch.yaml
