"""
Cihaz parmak izi üretimi.
"""

from __future__ import annotations

import getpass
import hashlib
import platform
import socket
import uuid


def get_machine_fingerprint() -> str:
    """
    Bir bilgisayarı olabildiğince stabil tanımlamak için parmak izi üretir.
    """
    parts = [
        platform.system(),
        platform.release(),
        platform.version(),
        platform.machine(),
        platform.processor(),
        socket.gethostname(),
        getpass.getuser(),
        str(uuid.getnode()),
    ]
    raw = "|".join(parts).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()
