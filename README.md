# Snowflake Lab Coffee — Medallion + IA con Cortex Code

Laboratorio en el que cada participante elige una fuente de datos y, **con un solo prompt**, la procesa de Bronze a Gold y obtiene un producto final (agente o dashboard) usando la IA de Snowflake: Cortex Code, Cortex Analyst y Cortex Agents.

## Repositorio del laboratorio
Este laboratorio usa el repositorio: **https://github.com/itzdata/snowflake-lab-coffee-v2.git**
(público, sin credenciales). Es el que se conecta a Snowflake para crear el workspace de cada participante
(Projects » Workspaces » From Git repository).

## Estructura
```
AGENTS.md                         # Reglas globales que Cortex Code lee siempre
standards/                        # Estándares: nombres, bronze, silver, gold, política IA
.cortex/skills/medallion-builder/ # Skill que orquesta el flujo completo
templates/                        # SQL de referencia con marcadores {{INI}}, {{FUENTE}}
setup/00_admin_setup.sql          # Infraestructura (instructor, ACCOUNTADMIN)
participants/                     # Aquí se guarda el SQL que genera cada participante
```

## Guía del instructor
1. Ejecutar `setup/00_admin_setup.sql` (ya ejecutado en la cuenta del laboratorio).
2. Subir los datasets, **una carpeta por fuente**:
   `@COFFEE_BRONZE.LANDING.STG_DATASETS/ventas/`, `/inventario/`, `/resenas/`, …
   (Snowsight » Data » Add Data » Load files into a stage).
3. Asignar el rol: `GRANT ROLE COFFEE_LAB_PARTICIPANT TO USER <usuario>;`
4. Cada participante crea su workspace desde este repo
   (Projects » Workspaces » From Git repository, integration `GITHUB_ITZDATA`, repo `https://github.com/itzdata/snowflake-lab-coffee-v2.git`).

## Guía del participante
1. Abre tu workspace del repo y Cortex Code, con el rol `COFFEE_LAB_PARTICIPANT`.
2. Mira las fuentes: `LIST @COFFEE_BRONZE.LANDING.STG_DATASETS;`
3. Escribe un prompt como:

> Soy **Gustavo Gamboa**. Usa el skill medallion-builder para procesar la fuente **VENTAS** de bronze a gold.
> Quiero ver ventas por tienda, producto y día.
> Crea un **agente** y un **dashboard**.

Resultado esperado (INI = `GG`):
| Capa | Objetos |
|---|---|
| `COFFEE_BRONZE.GG_VENTAS` | `RAW_*` |
| `COFFEE_SILVER.GG_VENTAS` | `STG_*`, `DIM_*`, `FCT_*` |
| `COFFEE_GOLD.GG_VENTAS` | `AGG_*`, `KPI_*`, `SV_VENTAS`, `AGT_VENTAS`, `APP_VENTAS_DASHBOARD` |

## IA de Snowflake que se muestra
- **Cortex Code**: genera todo el pipeline a partir de un prompt y de las reglas del repo.
- **Cortex Analyst** (semantic views) y **Cortex Agents**: preguntas en lenguaje natural sobre Gold.
- Fuera de alcance (por consumo de tokens): funciones AISQL de enriquecimiento (AI_SENTIMENT, AI_EXTRACT, …).
