#!/usr/bin/env python
"""Ejecuta SQL en Snowflake con el rol del laboratorio (envoltorio de Snowflake CLI).

Uso:
  python scripts/sf.py "SELECT CURRENT_ROLE()"
  python scripts/sf.py -f participants/GG_VENTAS/01_bronze.sql
  python scripts/sf.py --json "SELECT ..."          # salida JSON
  python scripts/sf.py --role COFFEE_LAB_PARTICIPANT --connection itzdata "..."

Variables de entorno (definidas en .claude/settings.json -> "env"):
  SF_CONNECTION  nombre de la conexión en ~/.snowflake/connections.toml (por defecto: itzdata)
  SF_ROLE        rol (por defecto: COFFEE_LAB_PARTICIPANT)
  SF_WAREHOUSE   warehouse (por defecto: COMPUTE_WH)

Por qué existe: el rol y el warehouse quedan fijos, así Claude nunca ejecuta como ACCOUNTADMIN.
"""
import argparse
import os
import subprocess
import sys

NOISE = ("UserWarning", "warnings.warn", "Skipping connection", "Reading connections from",
         "New version of Snowflake CLI", "Encoding mismatch")


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("sql", nargs="?", help="sentencia(s) SQL")
    ap.add_argument("-f", "--file", help="archivo .sql a ejecutar")
    ap.add_argument("--json", action="store_true", help="salida en JSON")
    ap.add_argument("--connection", default=os.environ.get("SF_CONNECTION", "itzdata"))
    ap.add_argument("--role", default=os.environ.get("SF_ROLE", "COFFEE_LAB_PARTICIPANT"))
    ap.add_argument("--warehouse", default=os.environ.get("SF_WAREHOUSE", "COMPUTE_WH"))
    a = ap.parse_args()
    if not a.sql and not a.file:
        ap.error("indica SQL o -f archivo.sql")
    if a.role.upper() == "ACCOUNTADMIN":
        print("BLOQUEADO: el laboratorio nunca usa ACCOUNTADMIN (AGENTS.md, reglas de oro).", file=sys.stderr)
        return 2

    cmd = ["snow", "sql", "-c", a.connection, "--role", a.role, "--warehouse", a.warehouse]
    cmd += ["-f", a.file] if a.file else ["-q", a.sql]
    if a.json:
        cmd += ["--format", "json"]
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
    for stream, out in ((p.stdout, sys.stdout), (p.stderr, sys.stderr)):
        for line in stream.splitlines():
            if not any(n in line for n in NOISE):
                print(line, file=out)
    return p.returncode


if __name__ == "__main__":
    sys.exit(main())
