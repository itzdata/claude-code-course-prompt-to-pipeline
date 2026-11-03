#!/usr/bin/env python
"""Hook UserPromptSubmit — se ejecuta con cada mensaje del participante, antes de que Claude lo vea.

Si el prompt pide enriquecimiento con IA fila por fila (AISQL), inyecta un recordatorio de política como
contexto adicional. Lo que se imprime en stdout se agrega al contexto del turno.
"""
import json
import re
import sys

try:
    prompt = json.load(sys.stdin).get("prompt", "")
except json.JSONDecodeError:
    sys.exit(0)

if re.search(r"sentimiento|sentiment|AI_[A-Z]+|clasific\w+ con IA|resumir cada|enriquec\w+ con (IA|AI)", prompt, re.I):
    print("[política del laboratorio] Las funciones AISQL de enriquecimiento (AI_SENTIMENT, AI_EXTRACT, AI_CLASSIFY, AI_COMPLETE…) "
          "están fuera de alcance por consumo de tokens. Explícalo brevemente y ofrece la alternativa con SQL (CASE / ILIKE) "
          "(standards/ai_functions.md).")
