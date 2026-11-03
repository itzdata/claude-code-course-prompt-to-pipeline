---
description: Lista las fuentes disponibles en el stage y las filtra por rubro o palabra clave del catálogo
argument-hint: [rubro o tema, ej. ventas, banca, energia]
allowed-tools: Bash(python scripts/sf.py:*), Read, Grep
---

## Contexto en vivo (se ejecuta antes de que Claude responda)
Archivos en el stage ahora mismo:

!`python scripts/sf.py "SELECT RELATIVE_PATH, SIZE, LAST_MODIFIED FROM DIRECTORY(@COFFEE_BRONZE.LANDING.STG_DATASETS) ORDER BY 1 LIMIT 100"`

## Tarea
Filtro pedido: **$ARGUMENTS** (si está vacío, resume los rubros del catálogo).

1. Busca en `datasets/CATALOGO.md` las fuentes que coinciden con el filtro (usa Grep, no leas las 867 líneas).
2. Muestra una tabla corta: fuente (carpeta), qué contiene, filas.
3. Marca cuáles ya están cargadas en el stage (según la lista de arriba) y cuáles no.
4. Si no hay datos en el stage para la fuente, dilo claramente: el instructor debe subirlos antes de continuar.
5. Sugiere el prompt listo de la fuente elegida (sección de detalle del catálogo).
