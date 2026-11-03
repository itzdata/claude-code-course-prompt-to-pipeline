#!/usr/bin/env python
"""Línea de estado (statusLine): Claude Code envía JSON por stdin y muestra la primera línea impresa."""
import json
import os
import re
import sys

try:
    data = json.load(sys.stdin)
except json.JSONDecodeError:
    data = {}
root = (data.get("workspace") or {}).get("project_dir") or os.getcwd()
who = "sin identificar (/lab-start)"
try:
    with open(os.path.join(root, "CLAUDE.local.md"), encoding="utf-8") as fh:
        m = re.search(r"INI:\s*`?(\w+)`?", fh.read())
        who = f"INI {m.group(1)}" if m else who
except OSError:
    pass
model = (data.get("model") or {}).get("display_name", "Claude")
print(f"[coffee-lab] {who} | rol {os.environ.get('SF_ROLE', 'COFFEE_LAB_PARTICIPANT')} | {model}")
