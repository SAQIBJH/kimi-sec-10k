# app/core/ssl_setup.py
import os
import urllib.request
from pathlib import Path

CA_URL = "https://dl.cacerts.digicert.com/DigiCertGlobalRootG2.crt.pem"
CA_FILENAME = "DigiCertGlobalRootG2.crt.pem"

def ensure_ca_cert() -> str:
    """
    Ensure DigiCert Global Root G2 CA cert exists locally and set SSL_CA env var.

    - Writes to a writable path in Azure App Service.
    - Downloads only if missing.
    - Returns absolute path to CA file.
    """
    # Prefer Azure-persistent writable home. Falls back to current directory.
    base_dir = Path(os.getenv("HOME", ".")) / "site" / "wwwroot"
    if not base_dir.exists():
        base_dir = Path.cwd()

    ca_path = (base_dir / CA_FILENAME).resolve()

    if not ca_path.exists():
        # Download to disk
        with urllib.request.urlopen(CA_URL, timeout=15) as resp:
            ca_path.write_bytes(resp.read())

    # Set env var so both SQLAlchemy + mysql.connector can use it
    os.environ["SSL_CA"] = str(ca_path)
    return str(ca_path)