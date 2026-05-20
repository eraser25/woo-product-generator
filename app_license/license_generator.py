"""
Lisans anahtarı üretici araç.
Bu dosya sana özel kalmalı; uygulama ile aynı paket içinde dağıtma.
"""

from __future__ import annotations

import argparse
import base64
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def generate_keypair(public_path: Path, private_path: Path) -> None:
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    public_path.parent.mkdir(parents=True, exist_ok=True)
    private_path.parent.mkdir(parents=True, exist_ok=True)

    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    public_path.write_bytes(public_pem)
    private_path.write_bytes(private_pem)


def load_private_key(private_path: Path) -> ed25519.Ed25519PrivateKey:
    private_pem = private_path.read_bytes()
    return serialization.load_pem_private_key(private_pem, password=None)


def issue_license(
    private_path: Path,
    customer: str,
    plan_name: str,
    days: int,
    output_path: Path,
    features: List[str],
    max_activations: int = 1,
) -> str:
    private_key = load_private_key(private_path)

    issued_at = _utc_now()
    expires_at = issued_at + timedelta(days=int(days))

    payload: Dict[str, Any] = {
        "license_id": f"lic_{issued_at.strftime('%Y%m%d%H%M%S')}",
        "customer": customer,
        "plan_name": plan_name,
        "issued_at": issued_at.isoformat(),
        "expires_at": expires_at.isoformat(),
        "max_activations": int(max_activations),
        "features": features,
        "version": 1,
    }

    payload_bytes = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    signature = private_key.sign(payload_bytes)

    token = "KYX1.{payload}.{signature}".format(
        payload=_b64url_encode(payload_bytes),
        signature=_b64url_encode(signature),
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(token, encoding="utf-8")

    return token


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Offline lisans anahtarı üretici")

    sub = parser.add_subparsers(dest="command", required=True)

    init_keys = sub.add_parser("init-keys", help="Yeni key pair oluştur")
    init_keys.add_argument("--public", type=Path, required=True)
    init_keys.add_argument("--private", type=Path, required=True)

    issue = sub.add_parser("issue", help="Yeni lisans anahtarı üret")
    issue.add_argument("--private", type=Path, required=True)
    issue.add_argument("--customer", type=str, required=True)
    issue.add_argument("--plan", type=str, default="monthly")
    issue.add_argument("--days", type=int, required=True)
    issue.add_argument("--output", type=Path, required=True)
    issue.add_argument(
        "--features",
        type=str,
        default="product_builder,csv_export,ftp_upload",
        help="Virgülle ayrılmış özellik listesi",
    )
    issue.add_argument("--max-activations", type=int, default=1)

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.command == "init-keys":
        generate_keypair(args.public, args.private)
        print(f"Public key written: {args.public}")
        print(f"Private key written: {args.private}")
        return

    if args.command == "issue":
        features = [x.strip() for x in args.features.split(",") if x.strip()]
        token = issue_license(
            private_path=args.private,
            customer=args.customer,
            plan_name=args.plan,
            days=args.days,
            output_path=args.output,
            features=features,
            max_activations=args.max_activations,
        )
        print(token)
        print(f"License file written: {args.output}")
        return


if __name__ == "__main__":
    main()
