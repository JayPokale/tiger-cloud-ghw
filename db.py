"""Shared connection helper: reads the service URI from the Tiger CLI."""
import os
import subprocess

import psycopg


def uri() -> str:
    if os.environ.get("DATABASE_URL"):
        return os.environ["DATABASE_URL"]
    out = subprocess.run(["tiger", "db", "uri", "--with-password"], capture_output=True, text=True, check=True)
    return out.stdout.strip()


def connect(**kw) -> psycopg.Connection:
    return psycopg.connect(uri(), **kw)
