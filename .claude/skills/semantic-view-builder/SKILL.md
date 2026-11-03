---
name: semantic-view-builder
description: Crea y valida una semantic view SV_<FUENTE> de Snowflake (Cortex Analyst) sobre las tablas FCT_/DIM_ de Silver o AGG_ de Gold. Úsalo cuando haya que crear, mejorar o probar la capa semántica de una fuente.
allowed-tools: Bash(python scripts/sf.py:*), Read, Edit(participants/**)
---

# Semantic view builder

1. Lee `standards/gold.md` §2 y el ejemplo de `templates/03_gold.sql` (bloque `CREATE OR REPLACE SEMANTIC VIEW`).
2. Inspecciona las tablas reales: `python scripts/sf.py "DESCRIBE TABLE COFFEE_SILVER.<INI>_<FUENTE>.FCT_<PROCESO>"`.
3. Escribe la semantic view en `participants/<INI>_<FUENTE>/03_gold.sql` con:
   - `TABLES` con `PRIMARY KEY` y `COMMENT`; `RELATIONSHIPS` entre hechos y dimensiones.
   - `DIMENSIONS` y `METRICS` con `WITH SYNONYMS` en español **e inglés** y `COMMENT`.
   - `COMMENT = '... | owner: <Nombre Apellido> | fuente: <FUENTE>'` al final.
4. Ejecútala y valida: `SELECT * FROM SEMANTIC_VIEW(<SV> DIMENSIONS ... METRICS ...)` con **3 preguntas de negocio**
   (por ejemplo: total por categoría, por tienda, por mes) y compara con SQL directo sobre FCT_.
5. Reporta preguntas probadas y resultados. Reglas del archivo `references/syntax.md` de este skill si hay errores de sintaxis.

Los detalles de sintaxis y errores comunes están en [references/syntax.md](references/syntax.md) (se lee solo si hace falta: *carga progresiva*).
