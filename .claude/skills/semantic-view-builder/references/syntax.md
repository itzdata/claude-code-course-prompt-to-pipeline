# Referencia rápida: CREATE SEMANTIC VIEW

```sql
CREATE OR REPLACE SEMANTIC VIEW BASE.ESQUEMA.SV_X
  TABLES (
    ALIAS AS BASE.ESQUEMA.TABLA PRIMARY KEY (COL) [WITH SYNONYMS = ('a','b')] [COMMENT = '...']
  )
  RELATIONSHIPS ( NOMBRE AS HECHO (COL_FK) REFERENCES DIMENSION )
  FACTS ( ALIAS.NOMBRE AS EXPRESION )                      -- opcional
  DIMENSIONS ( ALIAS.NOMBRE AS COLUMNA [WITH SYNONYMS ...] [COMMENT ...] )
  METRICS ( ALIAS.NOMBRE AS SUM(COL) [WITH SYNONYMS ...] [COMMENT ...] )
  COMMENT = '...';
```

Errores comunes
- Orden de cláusulas: `TABLES` → `RELATIONSHIPS` → `FACTS` → `DIMENSIONS` → `METRICS` → `COMMENT`.
- Una dimensión/métrica se califica con el **alias** de la tabla, no con el nombre completo.
- `PRIMARY KEY` debe ser único; si el grano es compuesto, lista todas las columnas.
- Las métricas usan agregaciones (`SUM`, `COUNT(DISTINCT ...)`); no referencian otras métricas sin `FACTS`.
- Prueba: `SELECT * FROM SEMANTIC_VIEW(BASE.ESQUEMA.SV_X DIMENSIONS ALIAS.DIM METRICS ALIAS.METRICA);`
