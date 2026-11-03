---
description: Audita estándares y valida conteos de una fuente en Bronze, Silver y Gold
argument-hint: <FUENTE> (ej. VENTAS)
allowed-tools: Bash(python scripts/sf.py:*), Read, Grep, Glob, Task
---

Valida la fuente **$ARGUMENTS** del participante indicado en `CLAUDE.local.md`.

1. Delega la auditoría de estándares al subagente **standards-auditor** (Task) sobre `participants/<INI>_$ARGUMENTS/`.
   Pídele solo el informe de hallazgos; no necesitas sus lecturas intermedias.
2. En paralelo, en Snowflake (`python scripts/sf.py`), cuenta filas por objeto con `INFORMATION_SCHEMA.TABLES`
   de `COFFEE_BRONZE`, `COFFEE_SILVER` y `COFFEE_GOLD` para el esquema `<INI>_$ARGUMENTS`.
3. Ejecuta las validaciones de `standards/silver.md` y `standards/gold.md`: unicidad de llaves, hechos sin dimensión,
   `SUM(FCT)` = `SUM(AGG)`.
4. Entrega una tabla ✅/❌ por regla y, si hay ❌, propón la corrección (no la apliques sin confirmación).
