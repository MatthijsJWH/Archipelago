"""Extract a domain's TLS cert/key from Traefik's acme.json (as managed by Coolify's proxy).

Room game servers listen directly on the host network, bypassing Coolify's
proxy, so they need their own copy of the domain's certificate to terminate
TLS themselves. Run this at container startup and periodically thereafter to
pick up Let's Encrypt renewals.
"""
import base64
import json
import os
import sys

ACME_JSON_PATH = os.environ.get("ACME_JSON_PATH", "/acme.json")
CERT_DOMAIN = os.environ.get("CERT_DOMAIN", "ap.halvemaan.dev")
CERT_OUT = os.environ.get("SELFLAUNCHCERT_PATH", "/app/certs/fullchain.pem")
KEY_OUT = os.environ.get("SELFLAUNCHKEY_PATH", "/app/certs/privkey.pem")


def find_cert(acme: dict, domain: str):
    for resolver in acme.values():
        for entry in resolver.get("Certificates", []) or []:
            names = {entry.get("domain", {}).get("main", "")}
            names.update(entry.get("domain", {}).get("sans", []) or [])
            if domain in names:
                return entry.get("certificate"), entry.get("key")
    return None, None


def main() -> int:
    if not os.path.exists(ACME_JSON_PATH):
        print(f"extract_cert: {ACME_JSON_PATH} not found, skipping", file=sys.stderr)
        return 1

    with open(ACME_JSON_PATH, "r", encoding="utf-8") as f:
        acme = json.load(f)

    cert_b64, key_b64 = find_cert(acme, CERT_DOMAIN)
    if not cert_b64 or not key_b64:
        print(f"extract_cert: no certificate found for {CERT_DOMAIN} in {ACME_JSON_PATH}", file=sys.stderr)
        return 1

    os.makedirs(os.path.dirname(CERT_OUT), exist_ok=True)
    with open(CERT_OUT, "wb") as f:
        f.write(base64.b64decode(cert_b64))
    with open(KEY_OUT, "wb") as f:
        f.write(base64.b64decode(key_b64))
    os.chmod(KEY_OUT, 0o600)

    print(f"extract_cert: wrote {CERT_OUT} and {KEY_OUT} for {CERT_DOMAIN}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
