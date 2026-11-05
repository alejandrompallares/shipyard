#!/usr/bin/env python3
"""Genera mock.png (390x300): maqueta de una lista de pedidos en móvil. Solo biblioteca estándar.

Uso: genera-mock.py <salida.png>
"""
import struct
import sys
import zlib

W, H = 390, 300
BG, BAR, CARD, LINE, ACCENT, PAID, PEND = (
    (245, 246, 248), (33, 60, 120), (255, 255, 255), (210, 214, 222),
    (240, 120, 40), (46, 160, 90), (230, 170, 30),
)

px = [[BG] * W for _ in range(H)]


def rect(x0, y0, x1, y1, color):
    for y in range(max(0, y0), min(H, y1)):
        row = px[y]
        for x in range(max(0, x0), min(W, x1)):
            row[x] = color


rect(0, 0, W, 56, BAR)                # barra superior
rect(16, 20, 140, 36, CARD)           # título
rect(334, 16, 374, 40, ACCENT)        # botón "nuevo"
for i, badge in enumerate([PAID, PEND, PAID]):
    top = 72 + i * 72
    rect(16, top, W - 16, top + 60, CARD)          # tarjeta de pedido
    rect(16, top + 59, W - 16, top + 60, LINE)
    rect(32, top + 14, 180, top + 26, LINE)        # cliente
    rect(32, top + 36, 120, top + 46, LINE)        # fecha
    rect(W - 120, top + 14, W - 32, top + 30, badge)  # estado
    rect(W - 100, top + 36, W - 32, top + 46, LINE)   # total

raw = b"".join(b"\x00" + bytes(c for p in row for c in p) for row in px)


def chunk(tag, data):
    return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)


png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)) \
    + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")
with open(sys.argv[1] if len(sys.argv) > 1 else "mock.png", "wb") as f:
    f.write(png)
