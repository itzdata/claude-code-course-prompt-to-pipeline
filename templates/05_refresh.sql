-- =====================================================================
-- 05_refresh.sql | Procedimiento ÚNICO de reproceso: SP_REFRESH_{{FUENTE}}
-- Con un CALL recarga Bronze, refresca Silver y Gold en orden de dependencias
-- y devuelve el conteo de filas por objeto. Idempotente: se puede ejecutar N veces.
-- Marcadores: {{INI}}, {{FUENTE}} (MAYUSCULAS), {{fuente}} (carpeta en el stage), {{ENTIDAD}}, {{archivo}} (CSV), {{OWNER}}
-- Antes de crearlo valida que el nombre no exista (SHOW PROCEDURES LIKE 'SP_REFRESH_{{FUENTE}}' IN SCHEMA ...).
-- =====================================================================
USE ROLE COFFEE_LAB_PARTICIPANT;
USE WAREHOUSE COMPUTE_WH;

CREATE OR REPLACE PROCEDURE COFFEE_GOLD.{{INI}}_{{FUENTE}}.SP_REFRESH_{{FUENTE}}()
  RETURNS VARCHAR
  LANGUAGE SQL
  COMMENT = 'Reproceso total Bronze->Silver->Gold | owner: {{OWNER}} | fuente: {{FUENTE}}'
  EXECUTE AS CALLER
AS
$$
DECLARE
  resumen VARCHAR DEFAULT '';
  n NUMBER;
BEGIN
  -- 1. Bronze: vaciar y recargar (FORCE = TRUE evita que COPY omita archivos ya cargados; TRUNCATE evita duplicados)
  TRUNCATE TABLE COFFEE_BRONZE.{{INI}}_{{FUENTE}}.RAW_{{ENTIDAD}};
  COPY INTO COFFEE_BRONZE.{{INI}}_{{FUENTE}}.RAW_{{ENTIDAD}}
    FROM @COFFEE_BRONZE.LANDING.STG_DATASETS/{{fuente}}/{{archivo}}
    FILE_FORMAT = (FORMAT_NAME = 'COFFEE_BRONZE.LANDING.FF_CSV')
    MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE
    INCLUDE_METADATA = (_FILE_NAME = METADATA$FILENAME, _FILE_ROW = METADATA$FILE_ROW_NUMBER, _LOADED_TS = METADATA$START_SCAN_TIME)
    FORCE = TRUE;
  -- (usa el mismo COPY INTO que 01_bronze.sql; repite el bloque por cada RAW_)

  -- 2. Silver y Gold: refrescar en orden de dependencias (STG -> DIM -> FCT -> AGG)
  ALTER DYNAMIC TABLE COFFEE_SILVER.{{INI}}_{{FUENTE}}.STG_{{ENTIDAD}} REFRESH;
  -- ALTER DYNAMIC TABLE COFFEE_SILVER.{{INI}}_{{FUENTE}}.DIM_<...> REFRESH;
  -- ALTER DYNAMIC TABLE COFFEE_SILVER.{{INI}}_{{FUENTE}}.FCT_<...> REFRESH;
  -- ALTER DYNAMIC TABLE COFFEE_GOLD.{{INI}}_{{FUENTE}}.AGG_<...> REFRESH;
  -- Si algún objeto es una tabla CTAS en lugar de dynamic table, usa CREATE OR REPLACE TABLE ... aquí.

  -- 3. Conteos por objeto
  SELECT COUNT(*) INTO :n FROM COFFEE_BRONZE.{{INI}}_{{FUENTE}}.RAW_{{ENTIDAD}};
  resumen := resumen || 'RAW_{{ENTIDAD}}: ' || n || CHR(10);
  SELECT COUNT(*) INTO :n FROM COFFEE_SILVER.{{INI}}_{{FUENTE}}.STG_{{ENTIDAD}};
  resumen := resumen || 'STG_{{ENTIDAD}}: ' || n || CHR(10);
  -- repite por cada DIM_, FCT_ y AGG_

  RETURN resumen;
END;
$$;

-- Uso: CALL COFFEE_GOLD.{{INI}}_{{FUENTE}}.SP_REFRESH_{{FUENTE}}();
