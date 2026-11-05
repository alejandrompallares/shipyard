"""Línea de comandos.

  motor-notas --boveda <carpeta>                 arranca el servidor MCP (stdio)
  motor-notas --boveda <carpeta> indexar         crea o actualiza el índice y dice qué cambió
  motor-notas --boveda <carpeta> buscar "texto"  prueba rápida desde la terminal
  motor-notas descargar                          descarga el modelo de embeddings
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time


def main(argv=None):
    ap = argparse.ArgumentParser(prog="motor-notas", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--boveda", default=os.environ.get("MOTOR_BOVEDA"), help="carpeta de notas (o MOTOR_BOVEDA)")
    ap.add_argument("--indice", help="ruta del índice SQLite (por defecto, en ~/.cache/motor-notas)")
    ap.add_argument("--sin-modelo", action="store_true", help="solo búsqueda por palabras")
    ap.add_argument("orden", nargs="?", default="servir", choices=["servir", "indexar", "buscar", "parecido", "descargar"])
    ap.add_argument("texto", nargs="?")
    a = ap.parse_args(argv)

    if a.sin_modelo:
        os.environ["MOTOR_SIN_MODELO"] = "1"
    if a.orden == "descargar":
        from .embeddings import descargar
        try:
            descargar(log=print)
        except Exception as e:
            print(f"motor-notas: {e}", file=sys.stderr)
            return 1
        return 0
    if not a.boveda:
        ap.error("falta --boveda (o la variable MOTOR_BOVEDA)")

    from .embeddings import Cargador
    from .indice import Indice

    cargador = Cargador(descargar_si_falta=True)
    indice = Indice(a.boveda, a.indice, cargador)
    if a.orden == "servir":
        from .servidor import crear_servidor
        indice.actualizar()
        crear_servidor(indice).run()
        return

    cargador.obtener(esperar=600)  # en la terminal sí esperamos al modelo
    t = time.time()
    stats = indice.actualizar()
    if a.orden == "indexar":
        print(json.dumps({**stats, "notas": len(indice.notas), "modelo": indice.estado_modelo(),
                          "segundos": round(time.time() - t, 2)}, ensure_ascii=False, indent=2))
    elif a.orden == "buscar":
        print(json.dumps(indice.buscar(a.texto or ""), ensure_ascii=False, indent=2))
    elif a.orden == "parecido":
        print(json.dumps(indice.buscar_parecido(a.texto or ""), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    sys.exit(main())
