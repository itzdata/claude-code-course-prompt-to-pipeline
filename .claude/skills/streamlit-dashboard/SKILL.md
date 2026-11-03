---
name: streamlit-dashboard
description: Crea el dashboard Streamlit APP_<FUENTE>_DASHBOARD que lee solo de la capa Gold (AGG_/KPI_) y lo despliega en Snowflake. Úsalo cuando el participante pida un dashboard, visualización o app de su fuente.
allowed-tools: Bash(python scripts/sf.py:*), Read, Edit(participants/**)
---

# Streamlit dashboard

1. Define con el participante 3-5 visuales (KPIs arriba, serie temporal, ranking por dimensión).
2. Crea `participants/<INI>_<FUENTE>/app/streamlit_app.py`:
   - Conexión con `st.connection("snowflake")` o `get_active_session()` (en Snowflake).
   - Lee **solo** de `COFFEE_GOLD.<INI>_<FUENTE>.AGG_*` / `KPI_*` (nunca de Bronze ni de otros esquemas).
   - `st.metric` para KPIs, `st.line_chart` / `st.bar_chart` para series y rankings, filtros en `st.sidebar`.
3. Crea `participants/<INI>_<FUENTE>/app/environment.yml` con `streamlit` y los paquetes usados (canal `snowflake`).
4. Despliegue (probado) con `scripts/sf.py`, sin Snowflake CLI directo:
   - `CREATE STAGE IF NOT EXISTS COFFEE_GOLD.<INI>_<FUENTE>.STG_APP COMMENT = '...'`
   - `PUT 'file://<ruta absoluta con />/app/streamlit_app.py' @COFFEE_GOLD.<INI>_<FUENTE>.STG_APP AUTO_COMPRESS=FALSE OVERWRITE=TRUE` (y `environment.yml`;
     la ruta va entre comillas simples porque puede tener espacios)
   - `CREATE OR REPLACE STREAMLIT COFFEE_GOLD.<INI>_<FUENTE>.APP_<FUENTE>_DASHBOARD FROM '@COFFEE_GOLD.<INI>_<FUENTE>.STG_APP' MAIN_FILE = 'streamlit_app.py' QUERY_WAREHOUSE = COMPUTE_WH COMMENT = '... | owner: ... | fuente: ...'`
   - Guarda estas sentencias en `04_product.sql` (los `PUT` como comentario).
5. Verifica localmente que las consultas del app devuelven filas (`python scripts/sf.py "<consulta del app>"`) antes de desplegar.
6. Entrega al participante la ruta para abrirlo (Snowsight → Projects → Streamlit).
