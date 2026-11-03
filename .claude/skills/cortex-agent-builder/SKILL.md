---
name: cortex-agent-builder
description: Crea un Cortex Agent AGT_<FUENTE> de Snowflake con la tool Cortex Analyst apuntando a la semantic view SV_<FUENTE>, y lo prueba con una pregunta. Úsalo cuando el participante pida un agente, chat o preguntas en lenguaje natural sobre sus datos.
allowed-tools: Bash(python scripts/sf.py:*), Read, Edit(participants/**)
---

# Cortex Agent builder

Requisitos: existe `COFFEE_GOLD.<INI>_<FUENTE>.SV_<FUENTE>` y responde preguntas (skill `semantic-view-builder`).

1. Verifica que el nombre no existe: `SHOW AGENTS LIKE 'AGT_<FUENTE>' IN SCHEMA COFFEE_GOLD.<INI>_<FUENTE>`.
2. Escribe en `participants/<INI>_<FUENTE>/04_product.sql`:

```sql
CREATE OR REPLACE AGENT COFFEE_GOLD.<INI>_<FUENTE>.AGT_<FUENTE>
  COMMENT = 'Agente de <FUENTE> | owner: <Nombre Apellido> | fuente: <FUENTE>'
  FROM SPECIFICATION
  $$
  models:
    orchestration: auto
  instructions:
    response: "Responde en español, breve y con cifras. Indica siempre el periodo analizado."
    orchestration: "Para cualquier pregunta de datos usa la herramienta analista_<fuente>."
  tools:
    - tool_spec:
        type: cortex_analyst_text_to_sql
        name: analista_<fuente>
        description: "Responde preguntas de negocio sobre <FUENTE> usando la semantic view."
  tool_resources:
    analista_<fuente>:
      semantic_view: "COFFEE_GOLD.<INI>_<FUENTE>.SV_<FUENTE>"
      execution_environment:
        type: warehouse
        warehouse: COMPUTE_WH
  $$;
```

3. Ejecuta con `python scripts/sf.py -f ...` y confirma con `DESCRIBE AGENT COFFEE_GOLD.<INI>_<FUENTE>.AGT_<FUENTE>`.
4. Prueba con 1 pregunta (probado) y reporta la respuesta:
   `python scripts/sf.py --json "SELECT SNOWFLAKE.CORTEX.DATA_AGENT_RUN('COFFEE_GOLD.<INI>_<FUENTE>.AGT_<FUENTE>', '{\"messages\":[{\"role\":\"user\",\"content\":[{\"type\":\"text\",\"text\":\"<pregunta>\"}]}],\"stream\":false}')"`
   La respuesta trae bloques `text`, `table` y `suggested_queries`; muestra el `text`. (Sin tildes en la pregunta si la consola de Windows altera el texto.)
5. Si el `CREATE AGENT` falla por sintaxis, consulta la documentación vigente de Snowflake (`CREATE AGENT`) antes de reintentar:
   la especificación evoluciona con las versiones.

Consumo de tokens: el agente solo gasta cuando alguien le pregunta (permitido por `standards/ai_functions.md`).
