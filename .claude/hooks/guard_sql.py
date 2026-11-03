#!/usr/bin/env python
"""Hook PreToolUse (matcher: Bash) — guardia de reglas de oro del laboratorio.

Claude Code envía por stdin un JSON: {"tool_name": "Bash", "tool_input": {"command": "..."}, ...}
Salida:  exit 0  -> permite
         exit 2  -> BLOQUEA; lo escrito en stderr se le devuelve a Claude para que se corrija.
Solo inspecciona comandos que ejecutan SQL (scripts/sf.py, snow, snowsql) y, si usan -f, el contenido del archivo.
"""
import json
import os
import re
import shlex
import sys

RULES = [
    (r"\bACCOUNTADMIN\b|\bSECURITYADMIN\b|\bSYSADMIN\b",
     "Regla de oro: el laboratorio usa solo COFFEE_LAB_PARTICIPANT (nunca ACCOUNTADMIN/SYSADMIN)."),
    (r"\b(CREATE|DROP)\s+(OR\s+REPLACE\s+)?DATABASE\b",
     "No se crean ni eliminan bases de datos: la infraestructura es fija (COFFEE_BRONZE/SILVER/GOLD)."),
    (r"\bDROP\s+SCHEMA\s+(IF\s+EXISTS\s+)?(COFFEE_\w+\.)?(LANDING|PUBLIC|INFORMATION_SCHEMA)\b",
     "No se eliminan los esquemas compartidos (LANDING, PUBLIC)."),
    (r"\bAI_(SENTIMENT|CLASSIFY|EXTRACT|TRANSLATE|FILTER|COMPLETE|AGG|SUMMARIZE_AGG|PARSE_DOCUMENT|EMBED|SIMILARITY)\b|\bSNOWFLAKE\.CORTEX\.(COMPLETE|SENTIMENT|EXTRACT_ANSWER|SUMMARIZE|TRANSLATE|CLASSIFY_TEXT)\b",
     "Política de IA (standards/ai_functions.md): sin funciones AISQL de enriquecimiento (consumen muchos tokens)."),
    (r"\b(PUT|REMOVE|RM)\s+[^;]*@COFFEE_BRONZE\.LANDING|\bCOPY\s+INTO\s+@COFFEE_BRONZE\.LANDING|\b(INSERT\s+INTO|TRUNCATE\s+TABLE|DROP\s+\w+)\s+COFFEE_BRONZE\.LANDING\b",
     "COFFEE_BRONZE.LANDING es solo lectura para participantes (solo se puede leer el stage)."),
]
SQL_RUNNERS = re.compile(r"scripts[/\\]sf\.py|\bsnow(sql)?\b")


def collect_sql(command: str) -> str:
    """Devuelve el texto SQL a inspeccionar: el comando y el contenido de archivos pasados con -f."""
    text = command
    try:
        tokens = shlex.split(command, posix=True)
    except ValueError:
        tokens = command.split()
    for i, tok in enumerate(tokens):
        if tok in ("-f", "--filename", "--file") and i + 1 < len(tokens):
            path = tokens[i + 1]
            for base in (os.environ.get("CLAUDE_PROJECT_DIR", "."), "."):
                full = os.path.join(base, path)
                if os.path.isfile(full):
                    with open(full, encoding="utf-8", errors="replace") as fh:
                        text += "\n" + fh.read()
                    break
    return text


def strip_comments(sql: str) -> str:
    sql = re.sub(r"--[^\n]*", " ", sql)
    return re.sub(r"/\*.*?\*/", " ", sql, flags=re.S)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    command = (payload.get("tool_input") or {}).get("command", "")
    if not SQL_RUNNERS.search(command):
        return 0
    if re.search(r"\bsnow(sql)?\b", command) and not re.search(r"scripts[/\\]sf\.py", command):
        print("Usa `python scripts/sf.py` en lugar de `snow`/`snowsql` directos: fija rol y warehouse del laboratorio.",
              file=sys.stderr)
        return 2
    sql = strip_comments(collect_sql(command))
    for pattern, message in RULES:
        if re.search(pattern, sql, flags=re.I):
            print(f"BLOQUEADO por .claude/hooks/guard_sql.py\n{message}", file=sys.stderr)
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
