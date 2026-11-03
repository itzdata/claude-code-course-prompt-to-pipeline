---
description: Identifica al participante, calcula su INI, valida la conexión a Snowflake y guarda CLAUDE.local.md
argument-hint: Nombre Apellido
allowed-tools: Bash(python scripts/sf.py:*), Edit(CLAUDE.local.md)
---

El participante se llama: **$ARGUMENTS**

1. Si `$ARGUMENTS` está vacío, pregunta nombre y apellido con una sola pregunta y detente.
2. Calcula `INI` (1ª letra del nombre + 1ª letra del apellido, MAYÚSCULAS). Si ya existe un esquema `<INI>_*` de otra persona
   (mira el `owner:` del COMMENT con `SHOW SCHEMAS LIKE '<INI>\_%' IN DATABASE COFFEE_GOLD`), usa 1ª letra del nombre + 2 primeras del apellido.
3. Valida la conexión: `python scripts/sf.py "SELECT CURRENT_ROLE(), CURRENT_WAREHOUSE(), CURRENT_ACCOUNT()"`.
   El rol debe ser `COFFEE_LAB_PARTICIPANT`. Si falla, explica cómo corregir la conexión (`SF_CONNECTION` en `.claude/settings.json`).
4. Escribe `CLAUDE.local.md` (archivo personal, está en `.gitignore`) con este formato exacto:

```
# Participante (CLAUDE.local.md)
- Nombre: <Nombre Apellido>
- INI: `<INI>`
- Esquema de trabajo: `<INI>_<FUENTE>` en COFFEE_BRONZE / COFFEE_SILVER / COFFEE_GOLD
- Owner para COMMENT: `owner: <Nombre Apellido>`
```

5. Termina con 3 líneas: identidad, conexión OK y siguiente paso sugerido (`/sources`).
