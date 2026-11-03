#!/usr/bin/env python
"""Hook PostToolUse (matcher: Write|Edit) — linter de estándares sobre participants/**/*.sql.

Se ejecuta DESPUÉS de que Claude escribe un archivo. Si encuentra incumplimientos sale con código 2 y escribe
el detalle en stderr: Claude lo lee como retroalimentación y corrige el archivo en el mismo turno.

Revisa (standards/naming.md y AGENTS.md):
  1. CREATE con nombre completamente calificado (BASE.ESQUEMA.OBJETO; esquemas: BASE.ESQUEMA).
  2. COMMENT con el patrón '... | owner: <Nombre Apellido> | fuente: <FUENTE>'.
  3. Sin ACCOUNTADMIN y sin funciones AISQL.
  4. Prefijo por tipo de objeto (RAW_, STG_, DIM_, FCT_, AGG_, KPI_, SV_, AGT_, APP_, SP_REFRESH_).
"""
import json
import re
import sys

AI = re.compile(r"\bAI_[A-Z_]+\s*\(|\bSNOWFLAKE\.CORTEX\.", re.I)
CREATE = re.compile(
    r"^\s*CREATE\s+(?:OR\s+REPLACE\s+)?(?:TEMP(?:ORARY)?\s+|TRANSIENT\s+)?"
    r"(SCHEMA|DYNAMIC\s+TABLE|TABLE|VIEW|SEMANTIC\s+VIEW|AGENT|PROCEDURE|STREAMLIT|TASK|STREAM|STAGE)\s+"
    r"(?:IF\s+NOT\s+EXISTS\s+)?([\w.\"$]+)", re.I | re.S)
PREFIX = {  # (tipo, esquema) -> prefijos válidos del nombre
    "SEMANTIC VIEW": ("SV_",), "AGENT": ("AGT_",), "STREAMLIT": ("APP_",),
    "TASK": ("TSK_",), "STREAM": ("STRM_",), "PROCEDURE": ("SP_",),
}
LAYER_PREFIX = {
    "COFFEE_BRONZE": ("RAW_", "VW_", "STG_"),
    "COFFEE_SILVER": ("STG_", "DIM_", "FCT_", "DT_", "VW_"),
    "COFFEE_GOLD": ("AGG_", "KPI_", "SV_", "AGT_", "APP_", "SP_", "DT_", "VW_", "TSK_", "STRM_"),
}


def split_statements(sql: str):
    sql = re.sub(r"--[^\n]*", " ", sql)
    sql = re.sub(r"/\*.*?\*/", " ", sql, flags=re.S)
    sql = re.sub(r"\$\$.*?\$\$", "$$BODY$$", sql, flags=re.S)  # cuerpos de procedimientos/apps
    return [s.strip() for s in sql.split(";") if s.strip()]


def lint(sql: str):
    problems = []
    if re.search(r"\bACCOUNTADMIN\b", sql, re.I):
        problems.append("Usa ACCOUNTADMIN: solo se permite COFFEE_LAB_PARTICIPANT.")
    if AI.search(sql):
        problems.append("Usa funciones AISQL/Cortex de enriquecimiento (prohibido por standards/ai_functions.md).")
    for stmt in split_statements(sql):
        m = CREATE.match(stmt)
        if not m:
            continue
        kind, name = re.sub(r"\s+", " ", m.group(1).upper()), m.group(2).replace('"', "")
        if kind == "STAGE" and "STG_" not in name.upper():
            pass
        parts = name.split(".")
        need = 2 if kind == "SCHEMA" else 3
        if len(parts) != need:
            problems.append(f"{kind} {name}: nombre no calificado (usa BASE.ESQUEMA{'' if kind == 'SCHEMA' else '.OBJETO'}).")
        if kind != "STAGE" and not re.search(r"COMMENT\s*=?\s*'[^']*\|\s*owner:\s*[^|']+\|\s*fuente:\s*[^']+'", stmt, re.I):
            problems.append(f"{kind} {name}: falta COMMENT '<descripción> | owner: <Nombre Apellido> | fuente: <FUENTE>'.")
        obj = parts[-1].upper()
        db = parts[0].upper()
        allowed = PREFIX.get(kind) or (("SP_",) if kind == "PROCEDURE" else None)
        if kind in ("TABLE", "DYNAMIC TABLE", "VIEW") and db in LAYER_PREFIX:
            allowed = LAYER_PREFIX[db]
        if allowed and kind != "SCHEMA" and not obj.startswith(allowed):
            problems.append(f"{kind} {name}: el prefijo debe ser uno de {', '.join(allowed)} (standards/naming.md).")
    return problems


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    path = ((payload.get("tool_input") or {}).get("file_path") or "").replace("\\", "/")
    if not path.endswith(".sql") or "/participants/" not in path:
        return 0
    try:
        with open(path, encoding="utf-8") as fh:
            problems = lint(fh.read())
    except OSError:
        return 0
    if problems:
        print(f"lint_sql.py encontró {len(problems)} incumplimiento(s) en {path}:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        print("Corrige el archivo antes de ejecutarlo.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
