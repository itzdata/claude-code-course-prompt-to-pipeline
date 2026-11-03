---
description: Ejecuta el procedimiento único de reproceso SP_REFRESH_<FUENTE> y compara conteos (idempotencia)
argument-hint: <FUENTE>
allowed-tools: Bash(python scripts/sf.py:*), Read
---

Reprocesa la fuente **$ARGUMENTS** del participante de `CLAUDE.local.md`:

1. Verifica que existe el procedimiento: `SHOW PROCEDURES LIKE 'SP_REFRESH_$ARGUMENTS' IN SCHEMA COFFEE_GOLD.<INI>_$ARGUMENTS`.
2. Ejecuta `CALL COFFEE_GOLD.<INI>_$ARGUMENTS.SP_REFRESH_$ARGUMENTS();` **dos veces** y guarda los conteos de cada ejecución.
3. Compara: deben ser idénticos (idempotencia, `standards/gold.md` §4). Muestra la tabla de conteos.
4. Si difieren, diagnostica (¿falta `TRUNCATE`? ¿`FORCE = TRUE`?) y propón la corrección.
