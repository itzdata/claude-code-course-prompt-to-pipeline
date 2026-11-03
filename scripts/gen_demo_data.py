#!/usr/bin/env python
"""Genera un CSV sintético de ventas de cafeterías para demos y pruebas (datos ficticios, con suciedad intencional).

  python scripts/gen_demo_data.py            -> datasets/demo/ventas_demo.csv

Suciedad incluida a propósito para que Silver tenga algo que limpiar: duplicados exactos, espacios, mayúsculas/minúsculas
mezcladas, precios vacíos y fechas inválidas.
"""
import csv
import os
import random
from datetime import date, timedelta

random.seed(42)
STORES = [("S01", "Centro Histórico", "Guatemala"), ("S02", "Zona 10", "Guatemala"), ("S03", "Antigua Plaza", "Antigua"),
          ("S04", "Mixco Mall", "Mixco"), ("S05", "Xela Parque", "Quetzaltenango")]
PRODUCTS = [("P01", "Espresso", "Bebidas calientes", 2.2), ("P02", "Cappuccino", "Bebidas calientes", 3.1),
            ("P03", "Latte", "Bebidas calientes", 3.4), ("P04", "Cold Brew", "Bebidas frías", 3.8),
            ("P05", "Frappé Moka", "Bebidas frías", 4.5), ("P06", "Croissant", "Panadería", 2.4),
            ("P07", "Muffin Arándano", "Panadería", 2.6), ("P08", "Sandwich Pollo", "Comida", 5.9),
            ("P09", "Bolsa Café 250g", "Retail", 9.5), ("P10", "Taza Térmica", "Retail", 14.0)]
PAYMENTS = ["Tarjeta", "Efectivo", "Wallet"]

rows, oid, d0 = [], 10000, date(2026, 1, 1)
for day in range(180):
    d = d0 + timedelta(days=day)
    for sid, sname, city in STORES:
        for _ in range(random.randint(6, 14)):
            oid += 1
            for pid, pname, cat, price in random.sample(PRODUCTS, random.randint(1, 3)):
                rows.append([oid, d.isoformat(), sid, sname, city, pid, pname, cat, random.randint(1, 4),
                             round(price, 2), random.choice([0, 0, 0, 5, 10]), random.choice(PAYMENTS)])

# suciedad intencional
for i in random.sample(range(len(rows)), 25):
    rows.append(list(rows[i]))                                  # duplicados exactos
for i in random.sample(range(len(rows)), 40):
    rows[i][3] = "  " + rows[i][3].upper() + " "                # espacios y mayúsculas
for i in random.sample(range(len(rows)), 10):
    rows[i][9] = ""                                             # precio vacío
for i in random.sample(range(len(rows)), 5):
    rows[i][1] = "2026-13-45"                                   # fecha inválida

out = os.path.join(os.path.dirname(__file__), "..", "datasets", "demo", "ventas_demo.csv")
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["ORDER_ID", "ORDER_DATE", "STORE_ID", "STORE_NAME", "CITY", "PRODUCT_ID", "PRODUCT_NAME", "CATEGORY",
                "QUANTITY", "UNIT_PRICE", "DISCOUNT_PCT", "PAYMENT_METHOD"])
    w.writerows(rows)
print(f"{len(rows)} filas -> {os.path.normpath(out)}")
