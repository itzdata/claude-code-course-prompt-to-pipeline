# Guía Claude Code — cómo Claude interactúa con la configuración de este repo

Este repo ya no depende de Cortex Code: **todo el comportamiento del laboratorio vive en archivos versionados** que Claude Code lee solo.
Esta guía mapea cada elemento → qué hace → cuándo se activa → cómo verlo.

## Mapa de elementos

| # | Elemento | Archivo(s) | Quién lo activa | Para qué sirve en el laboratorio |
|---|---|---|---|---|
| 1 | **Memoria de proyecto** | `CLAUDE.md` (+ `@AGENTS.md`, `@standards/naming.md`) | Claude, al iniciar la sesión | Reglas de oro y estándar de nombres siempre en contexto |
| 2 | **Memoria personal** | `CLAUDE.local.md` (gitignored) | `/lab-start` | Nombre e INI de cada participante |
| 3 | **Reglas por ruta** | `.claude/rules/*.md` (`paths:`) | Claude, al tocar archivos que coinciden | Estándares de capa y política de IA cargados *solo cuando hacen falta* |
| 4 | **Permisos** | `.claude/settings.json` → `permissions` | El arnés, en cada herramienta | `allow` (sf.py, editar participants/), `ask` (editar estándares), `deny` (snow/snowsql directos, tokens) |
| 5 | **Variables de entorno** | `.claude/settings.json` → `env` | Al iniciar | Conexión, rol y warehouse (`SF_CONNECTION`, `SF_ROLE`, `SF_WAREHOUSE`) |
| 6 | **Hook SessionStart** | `.claude/hooks/session_start.py` | Al abrir la sesión | Diagnóstico del entorno inyectado al contexto |
| 7 | **Hook UserPromptSubmit** | `.claude/hooks/prompt_policy.py` | Con cada mensaje | Si piden AISQL, agrega el recordatorio de política |
| 8 | **Hook PreToolUse** | `.claude/hooks/guard_sql.py` | Antes de cada `Bash` | **Bloquea** ACCOUNTADMIN, CREATE DATABASE, AISQL, escritura en LANDING y `snow` directo |
| 9 | **Hook PostToolUse** | `.claude/hooks/lint_sql.py` | Después de cada Write/Edit | Revisa COMMENT/owner, nombres completos y prefijos; Claude se autocorrige |
| 10 | **Skills** | `.claude/skills/*/SKILL.md` | Claude, por la `description` | `medallion-builder` (orquestador), `semantic-view-builder`, `cortex-agent-builder`, `streamlit-dashboard` |
| 11 | **Archivos de apoyo del skill** | `semantic-view-builder/references/syntax.md` | Claude, bajo demanda | Carga progresiva: detalle solo si hace falta |
| 12 | **Comandos slash** | `.claude/commands/*.md` | El usuario: `/lab-start`, `/sources`, `/validate`, `/refresh` | Atajos con argumentos (`$ARGUMENTS`) y contexto en vivo (`!`comando``) |
| 13 | **Subagentes** | `.claude/agents/*.md` | Claude o un comando | `data-profiler` (haiku, perfila datos), `standards-auditor` (sonnet, solo lectura) en contextos aislados |
| 14 | **Estilo de salida** | `.claude/output-styles/instructor.md` | El usuario (`/output-style`) | Claude explica qué elemento usa — ideal para clases |
| 15 | **Línea de estado** | `.claude/statusline.py` | Siempre | Muestra INI y rol activos |
| 16 | **Servidor MCP** | `.mcp.json` + `.claude/snowflake_mcp_services.yaml` | Al aprobar el servidor | Herramientas de Snowflake de solo lectura (opcional) |
| 17 | **Script de apoyo** | `scripts/sf.py` | Claude, vía Bash | Un solo punto de entrada a Snowflake con el rol fijo |

## Cómo se encadenan en una petición

> *"Soy Gustavo Gamboa. Procesa la fuente VENTAS de bronze a gold; quiero un agente y un dashboard."*

1. **CLAUDE.md** ya está cargado (reglas + naming). El hook **SessionStart** dijo si el participante estaba identificado.
2. **UserPromptSubmit** revisa el mensaje (no pide AISQL → no inyecta nada).
3. Claude reconoce la intención → carga el skill **medallion-builder** (por su `description`) y presenta el plan.
4. Al escribir `participants/GG_VENTAS/01_bronze.sql`, la **regla por ruta** carga el estándar de Bronze y **lint_sql.py** valida el archivo.
5. Para ejecutar usa `python scripts/sf.py -f ...`: el permiso `allow` lo deja pasar y **guard_sql.py** inspecciona el SQL.
6. Silver: perfila con el subagente **data-profiler**. Gold: skill **semantic-view-builder**. Producto: **cortex-agent-builder** y **streamlit-dashboard**.
7. `/validate VENTAS` → subagente **standards-auditor** + conteos; `/refresh VENTAS` → prueba de idempotencia del `SP_REFRESH_`.

## Demostración de "configurar en lenguaje natural"
Claude también puede *escribir su propia configuración*. Prompts para la clase:
- "Agrega un hook que bloquee cualquier `DROP TABLE` en COFFEE_GOLD." → edita `.claude/settings.json` y crea el script.
- "Crea un comando `/top-ventas` que muestre las 5 tiendas con más ventas de mi fuente." → crea `.claude/commands/top-ventas.md`.
- "Crea un subagente que revise que cada `FCT_` tenga su grano documentado en el COMMENT."
- "Permite a Claude ejecutar `git status` sin pedirme permiso." → agrega la regla `allow`.
- "Cambia el estilo de respuesta a instructor." → output style.

## Resultados verificados contra Snowflake (cuenta ITZDATALLC_PARTNER, rol COFFEE_LAB_PARTICIPANT)
Fuente de prueba `participants/CC_VENTAS_DEMO` (18,053 filas sintéticas con duplicados, espacios, precios vacíos y fechas inválidas):

| Capa | Objeto | Resultado |
|---|---|---|
| Bronze | `RAW_ORDERS` | 18,053 filas cargadas |
| Silver | `STG_ORDERS` / `FCT_SALES` | 18,028 deduplicadas / 18,013 válidas; `DIM_PRODUCT` 10, `DIM_STORE` 5 |
| Gold | `AGG_SALES_DAILY_STORE`, `KPI_SALES`, `SV_VENTAS_DEMO` | SUM(FCT) − SUM(AGG) = 0; la semantic view responde |
| Producto | `AGT_VENTAS_DEMO` | "¿Qué tienda vendió más?" → Zona 10, USD 46,826 |
| Producto | `APP_VENTAS_DEMO_DASHBOARD` | Streamlit creado |
| Reproceso | `SP_REFRESH_VENTAS_DEMO()` | Dos `CALL` consecutivos, conteos idénticos |
| Hooks | `guard_sql.py` | Bloquea ACCOUNTADMIN, AISQL, `snow` directo y escritura en LANDING; deja pasar SQL válido |

Limpieza de la prueba: `DROP SCHEMA COFFEE_BRONZE.CC_VENTAS_DEMO; DROP SCHEMA COFFEE_SILVER.CC_VENTAS_DEMO; DROP SCHEMA COFFEE_GOLD.CC_VENTAS_DEMO;`

## Configuración para otro participante
Cada participante ajusta su conexión en `.claude/settings.local.json` (no se versiona):
```json
{ "env": { "SF_CONNECTION": "mi_conexion" } }
```
Conexión con Snowflake CLI: `snow connection add` (usa el rol `COFFEE_LAB_PARTICIPANT`).
