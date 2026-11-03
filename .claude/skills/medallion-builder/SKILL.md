---
name: medallion-builder
description: Lleva una fuente de datos del stage COFFEE_BRONZE.LANDING.STG_DATASETS de Bronze a Silver a Gold siguiendo los estándares del laboratorio Coffee y construye el producto final (semantic view, Cortex Agent, dashboard Streamlit). Úsalo cuando el participante diga "procesa la fuente", "de bronze a gold", "medallion", "pipeline del laboratorio" o pida un agente/dashboard de su fuente.
allowed-tools: Bash(python scripts/sf.py:*), Read, Grep, Glob, Edit(participants/**)
---

# Medallion Builder — versión Claude Code

Un **skill** es un paquete de instrucciones que Claude carga *solo cuando la petición coincide con su `description`*.
Este es el orquestador: decide el orden y delega los productos finales en otros skills.

## Antes de empezar (obligatorio)
1. Lee `standards/bronze.md`, `silver.md`, `gold.md`, `ai_functions.md` y `datasets/CATALOGO.md` (solo la fuente elegida: usa Grep).
   `AGENTS.md` y `naming.md` ya están en contexto por `CLAUDE.md`.
2. Identidad: usa `CLAUDE.local.md`. Si no existe, pide nombre y apellido (o `/lab-start`) y calcula `INI`.
3. Extrae del prompt: **FUENTE**, **producto final** (agente, dashboard, ambos; por defecto semantic view + agente) y **qué quiere ver**.
   Si la fuente no existe: `python scripts/sf.py "LIST @COFFEE_BRONZE.LANDING.STG_DATASETS"` y muestra las disponibles.
4. Colisiones: `SHOW SCHEMAS LIKE '<INI>_<FUENTE>' IN DATABASE COFFEE_BRONZE` y, **antes de cada CREATE**, `SHOW ... LIKE` del objeto
   (regla de existencia de `AGENTS.md`).
5. **Presenta un plan corto** (objetos por capa con su nombre completo) y pide confirmación **una sola vez**.

## Paso 1 — Bronze → `participants/<INI>_<FUENTE>/01_bronze.sql`
Parte de `templates/01_bronze.sql`. Perfila con `INFER_SCHEMA`, crea `RAW_<ENTIDAD>`, carga con `COPY INTO`. Ejecuta con
`python scripts/sf.py -f participants/<INI>_<FUENTE>/01_bronze.sql` y reporta conteos.

## Paso 2 — Silver → `02_silver.sql`
Perfila RAW_ (nulos, duplicados, tipos; delega en el subagente **data-profiler** si hay muchas columnas). Crea `STG_` → `DIM_` / `FCT_`
(`templates/02_silver.sql`). Sin funciones AISQL. Ejecuta y valida unicidad e integridad referencial.

## Paso 3 — Gold → `03_gold.sql`
`AGG_` y `KPI_` alineados a lo que el participante quiere ver. Luego usa el skill **semantic-view-builder** para `SV_<FUENTE>`
y valídala con 3 preguntas.

## Paso 4 — Producto final → `04_product.sql` y `app/`
- Agente → skill **cortex-agent-builder** (`AGT_<FUENTE>`).
- Dashboard → skill **streamlit-dashboard** (`APP_<FUENTE>_DASHBOARD`, lee solo de Gold).

## Paso 5 — Reproceso → `05_refresh.sql`
Un único `SP_REFRESH_<FUENTE>()` con `templates/05_refresh.sql`. Pruébalo con `/refresh <FUENTE>` (dos ejecuciones, mismos conteos).

## Cierre
Tabla resumen de objetos por capa con conteos, el comando de reproceso, la frecuencia (`TARGET_LAG`) y 3 preguntas de ejemplo para el agente.
Sugiere `/validate <FUENTE>` como verificación final.

## Prohibido
Crear bases de datos, usar ACCOUNTADMIN, tocar esquemas de otros participantes, escribir en `COFFEE_BRONZE.LANDING`, AISQL, objetos sin COMMENT.
(Los hooks lo bloquean aunque se olvide.)
