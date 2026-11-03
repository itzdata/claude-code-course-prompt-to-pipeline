#!/usr/bin/env python
"""Hook SessionStart — lo que imprime en stdout se agrega al contexto de Claude al abrir la sesión.

Comprueba herramientas locales y si el participante ya se identificó con /lab-start (CLAUDE.local.md).
"""
import os
import shutil

root = os.environ.get("CLAUDE_PROJECT_DIR", ".")
lines = ["[laboratorio coffee] Estado del entorno:"]
lines.append(f"- Snowflake CLI (snow): {'OK' if shutil.which('snow') else 'NO INSTALADO (pip install snowflake-cli)'}")
lines.append(f"- Conexión: {os.environ.get('SF_CONNECTION', 'itzdata')} · rol {os.environ.get('SF_ROLE', 'COFFEE_LAB_PARTICIPANT')} · warehouse {os.environ.get('SF_WAREHOUSE', 'COMPUTE_WH')}")
if os.path.isfile(os.path.join(root, "CLAUDE.local.md")):
    lines.append("- Identidad del participante: ver CLAUDE.local.md (ya cargada).")
else:
    lines.append("- El participante aún no se ha identificado: pídele su nombre y apellido o sugiere ejecutar `/lab-start Nombre Apellido`.")
print("\n".join(lines))
