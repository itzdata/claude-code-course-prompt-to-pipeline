-- Producto final de VENTAS_DEMO | INI = CC | agente (skill cortex-agent-builder) y dashboard (skill streamlit-dashboard)
USE ROLE COFFEE_LAB_PARTICIPANT;
USE WAREHOUSE COMPUTE_WH;

CREATE OR REPLACE AGENT COFFEE_GOLD.CC_VENTAS_DEMO.AGT_VENTAS_DEMO
  COMMENT = 'Agente de ventas por tienda y producto | owner: Claude Code | fuente: VENTAS_DEMO'
  FROM SPECIFICATION
  $$
  models:
    orchestration: auto
  instructions:
    response: "Responde en español, breve y con cifras en USD. Indica siempre el periodo analizado."
    orchestration: "Para cualquier pregunta de datos usa la herramienta analista_ventas."
  tools:
    - tool_spec:
        type: cortex_analyst_text_to_sql
        name: analista_ventas
        description: "Responde preguntas de negocio sobre ventas por tienda, producto, categoría, ciudad y fecha."
  tool_resources:
    analista_ventas:
      semantic_view: "COFFEE_GOLD.CC_VENTAS_DEMO.SV_VENTAS_DEMO"
      execution_environment:
        type: warehouse
        warehouse: COMPUTE_WH
  $$;

DESCRIBE AGENT COFFEE_GOLD.CC_VENTAS_DEMO.AGT_VENTAS_DEMO;

-- Dashboard Streamlit (skill streamlit-dashboard). Archivos en participants/CC_VENTAS_DEMO/app/
CREATE STAGE IF NOT EXISTS COFFEE_GOLD.CC_VENTAS_DEMO.STG_APP
  COMMENT = 'Código del dashboard | owner: Claude Code | fuente: VENTAS_DEMO';
-- PUT 'file://<ruta>/app/streamlit_app.py' @COFFEE_GOLD.CC_VENTAS_DEMO.STG_APP AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
-- PUT 'file://<ruta>/app/environment.yml' @COFFEE_GOLD.CC_VENTAS_DEMO.STG_APP AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
CREATE OR REPLACE STREAMLIT COFFEE_GOLD.CC_VENTAS_DEMO.APP_VENTAS_DEMO_DASHBOARD
  FROM '@COFFEE_GOLD.CC_VENTAS_DEMO.STG_APP'
  MAIN_FILE = 'streamlit_app.py'
  QUERY_WAREHOUSE = COMPUTE_WH
  COMMENT = 'Dashboard de ventas por tienda y producto | owner: Claude Code | fuente: VENTAS_DEMO';
