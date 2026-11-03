---
paths:
  - "**/*.sql"
  - "**/app/**/*.py"
---

# Política de IA (se carga al tocar cualquier SQL o app)

- Prohibido en el pipeline: `AI_SENTIMENT`, `AI_CLASSIFY`, `AI_EXTRACT`, `AI_COMPLETE`, `AI_SUMMARIZE_AGG`, `SNOWFLAKE.CORTEX.*` y tablas `ENR_`.
- Permitido: semantic view `SV_` + Cortex Analyst, y Cortex Agent `AGT_` (consume tokens solo cuando alguien pregunta).
- Si el participante pide enriquecimiento con IA: explica que está fuera de alcance y ofrece la alternativa con `CASE` / `ILIKE`.
- Detalle completo: `standards/ai_functions.md`. Los hooks `guard_sql.py` y `lint_sql.py` lo hacen cumplir.
