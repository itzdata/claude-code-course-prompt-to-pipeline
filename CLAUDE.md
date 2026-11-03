# CLAUDE.md — Laboratorio Coffee Medallion con Claude Code

Este archivo lo carga Claude Code **automáticamente al iniciar cada sesión** en este repo (es su "memoria de proyecto").
Es la versión Claude Code del laboratorio que antes corría con Cortex Code (`AGENTS.md`).

## Reglas del laboratorio (importadas)
Las reglas globales viven en `AGENTS.md` y se reutilizan sin duplicarlas con un *import* (`@archivo`):

@AGENTS.md

Estándares que siempre aplican (también importados, así Claude los tiene en contexto desde el primer mensaje):

@standards/naming.md

Los demás estándares (`bronze.md`, `silver.md`, `gold.md`, `ai_functions.md`) se cargan bajo demanda mediante
`.claude/rules/` cuando Claude toca los archivos correspondientes.

## Diferencias respecto a Cortex Code
| En `AGENTS.md` se dice… | En Claude Code se hace así |
|---|---|
| Skill `agent-studio` | Skills `semantic-view-builder` y `cortex-agent-builder` (`.claude/skills/`) |
| Skill `streamlit-in-workspaces` | Skill `streamlit-dashboard` |
| Skill `medallion-builder` | Mismo nombre, en `.claude/skills/medallion-builder/` |
| `cortex analyst query` | `python scripts/sf.py "SELECT ... SEMANTIC_VIEW(...)"` |
| SQL ejecutado por el workspace de Snowsight | SQL ejecutado por `python scripts/sf.py` (Snowflake CLI) |

## Cómo ejecutar SQL en Snowflake (obligatorio)
- Usa **siempre** `python scripts/sf.py "<SQL>"` o `python scripts/sf.py -f <archivo.sql>`.
  El script fuerza `ROLE COFFEE_LAB_PARTICIPANT` y `WAREHOUSE COMPUTE_WH`, y usa la conexión de `SF_CONNECTION` (ver `.claude/settings.json`).
- **No** llames `snow sql` ni `snowsql` directamente: están denegados en `.claude/settings.json` y el hook `guard_sql.py` los bloquea.
- Los hooks de `.claude/hooks/` validan el SQL antes de ejecutarlo y revisan los `.sql` que escribas en `participants/`.

## Flujo de trabajo esperado
1. `/lab-start Nombre Apellido` → calcula `INI`, valida la conexión y guarda tu identidad en `CLAUDE.local.md`.
2. `/sources [rubro]` → explora las fuentes del stage y del catálogo.
3. Pide en lenguaje natural: *"Procesa la fuente VENTAS de bronze a gold y quiero un agente y un dashboard"* →
   Claude activa el skill `medallion-builder`.
4. `/validate <FUENTE>` → subagente `standards-auditor` + conteos por capa.
5. `/refresh <FUENTE>` → `CALL SP_REFRESH_<FUENTE>()` y compara conteos.

## Cómo trabajar (buenas prácticas de Claude Code)
- Presenta un **plan** corto y espera confirmación antes de crear objetos (modo plan: `Shift+Tab`).
- Verifica cada capa con consultas reales antes de pasar a la siguiente; reporta conteos.
- Guarda todo el SQL en `participants/<INI>_<FUENTE>/NN_*.sql` y ejecútalo desde esos archivos (`sf.py -f`).
- Si el hook bloquea una acción, explícale la regla al participante y propón la alternativa compatible.
- Responde en español.

> `CLAUDE.local.md` (personal, en `.gitignore`) se carga junto a este archivo y guarda tu nombre e `INI`.
