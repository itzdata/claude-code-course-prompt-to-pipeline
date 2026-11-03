---
paths:
  - "participants/**/01_bronze.sql"
  - "participants/**/02_silver.sql"
  - "participants/**/03_gold.sql"
  - "templates/**"
---

# Reglas por capa (se cargan SOLO cuando Claude trabaja con estos archivos)

Los archivos de `.claude/rules/` con `paths:` son **reglas condicionales**: no ocupan contexto hasta que Claude lee o edita
un archivo que coincide con el patrón. Así CLAUDE.md se mantiene corto.

Antes de escribir SQL de una capa, lee su estándar completo:
- Bronze → `standards/bronze.md`: copia fiel, sin transformar; `RAW_<ENTIDAD>`; columnas `_FILE_NAME`, `_FILE_ROW`, `_LOADED_TS`; `ON_ERROR = CONTINUE` y validar con conteos.
- Silver → `standards/silver.md`: `STG_` tipado con `TRY_TO_*`, dedupe con `QUALIFY ROW_NUMBER()`, `DIM_` con `_SK`, `FCT_` con grano en el COMMENT; dynamic tables con `TARGET_LAG = '1 day'`.
- Gold → `standards/gold.md`: `AGG_`, `KPI_`, `SV_<FUENTE>`, producto final y **un único** `SP_REFRESH_<FUENTE>`.

Checklist rápido para cualquier `CREATE`:
1. Nombre completamente calificado `BASE.ESQUEMA.OBJETO`.
2. `COMMENT = '<descripción> | owner: <Nombre Apellido> | fuente: <FUENTE>'`.
3. Verificado antes con `SHOW <TIPO> LIKE '<NOMBRE>' IN SCHEMA ...` que el nombre no existe (o es del mismo owner).
4. Idempotente (`CREATE OR REPLACE` / `IF NOT EXISTS`).
