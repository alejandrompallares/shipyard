#!/usr/bin/env python3
"""Mantiene las conversaciones cortas sin perder el hilo. Solo usa la biblioteca estándar.

  contexto.py aviso    Hook Stop: si la conversación ha crecido mucho, pide a Claude que guarde
                       el estado en la nota «Retomar <proyecto>» y avise de que se puede hacer /clear
                       o abrir una conversación nueva (algunos clientes no tienen /clear).
  contexto.py inicio   Hook SessionStart: recuerda leer esa nota al empezar.

SHIPYARD_AVISO_TOKENS cambia el umbral (150000 por defecto); 0 lo desactiva.
Un fallo aquí nunca debe molestar: ante cualquier error, sale sin decir nada.
"""
import json
import os
import sys
import tempfile

UMBRAL = 150_000
PASO = 100_000  # si sigue creciendo, vuelve a avisar cada tanto
COLA = 1_000_000  # bytes finales de la transcripción que se leen


def umbral():
    try:
        return int(os.environ.get("SHIPYARD_AVISO_TOKENS", UMBRAL))
    except ValueError:
        return UMBRAL


def tokens_de_contexto(ruta):
    """Tamaño de la conversación según el último turno del hilo principal."""
    with open(ruta, "rb") as f:
        f.seek(0, os.SEEK_END)
        f.seek(max(0, f.tell() - COLA))
        lineas = f.read().splitlines()
    for linea in reversed(lineas):
        try:
            e = json.loads(linea)
        except ValueError:
            continue
        if e.get("type") != "assistant" or e.get("isSidechain"):
            continue
        u = (e.get("message") or {}).get("usage") or {}
        total = sum(u.get(k) or 0 for k in ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens"))
        if total:
            return total
    return 0


def titulo_nota(cwd):
    """Sin paréntesis, comas ni dos puntos, que rompen los enlaces en Jylos."""
    nombre = os.path.basename(os.path.normpath(cwd or os.getcwd()))
    return "Retomar " + "".join(c for c in nombre if c not in "(),:").strip()


def ruta_estado(sesion):
    limpio = "".join(c for c in str(sesion) if c.isalnum() or c in "-_") or "x"
    return os.path.join(tempfile.gettempdir(), f"shipyard-contexto-{limpio}")


def aviso(datos):
    limite = umbral()
    if limite <= 0 or datos.get("stop_hook_active"):
        return
    n = tokens_de_contexto(datos["transcript_path"])
    estado = ruta_estado(datos.get("session_id"))
    if n < limite:  # p. ej. tras compactar
        if os.path.exists(estado):
            os.remove(estado)
        return
    try:
        with open(estado) as f:
            ultimo = int(f.read().strip() or 0)
    except (OSError, ValueError):
        ultimo = 0
    if ultimo and n < ultimo + PASO:
        return
    with open(estado, "w") as f:
        f.write(str(n))
    titulo = titulo_nota(datos.get("cwd"))
    print(json.dumps({"decision": "block", "reason": (
        f"Shipyard: esta conversación va por unos {n // 1000}.000 tokens y cada turno la reenvía entera. "
        "Sin preguntar y sin hacer nada más:\n"
        f"1. Guarda en Jylos la nota «{titulo}» en 10 Proyectos; si ya existe, sustituye su contenido. "
        "Máximo 15 líneas: objetivo, qué está hecho, decisiones, qué falta, siguiente paso exacto y archivos clave. "
        "Si no hay herramientas de Jylos, escribe ese resumen aquí en Markdown.\n"
        "2. Di en una línea que está guardado y que, al acabar lo que esté en marcha, escriba /clear "
        "o abra una conversación nueva: la sesión nueva sigue sola desde esa nota."
    )}, ensure_ascii=False))


def inicio(datos):
    if umbral() <= 0:
        return
    titulo = titulo_nota(datos.get("cwd"))
    print(f"Shipyard: si te piden trabajar en este proyecto y tienes Jylos, lee primero la nota «{titulo}». "
          "Si no existe, sigue sin mencionarlo. Es un resumen: no releas lo que ya explica.")


def main():
    try:
        datos = json.load(sys.stdin)
        {"aviso": aviso, "inicio": inicio}[sys.argv[1]](datos)
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
