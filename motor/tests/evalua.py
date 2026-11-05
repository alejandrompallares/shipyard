"""Cifras del motor sobre la bóveda de ejemplo: palabras contra significado.

    uv run python tests/evalua.py            (usa el modelo si está descargado)
    uv run python tests/evalua.py --sin-modelo
"""
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from consultas import DUPLICADOS, DUPLICADOS_PARAFRASIS, NO_DUPLICADOS, SINONIMOS  # noqa: E402

if "--sin-modelo" in sys.argv:
    os.environ["MOTOR_SIN_MODELO"] = "1"

from motor_notas.embeddings import Cargador, carpeta_modelo  # noqa: E402
from motor_notas.indice import Indice  # noqa: E402

BOVEDA = Path(__file__).resolve().parent.parent / "boveda-ejemplo"


def main():
    tmp = Path(tempfile.mkdtemp())
    shutil.copytree(BOVEDA, tmp / "b")
    cargador = Cargador(descargar_si_falta=False)
    t = time.time()
    modelo = cargador.obtener(esperar=120)
    carga = time.time() - t
    idx = Indice(tmp / "b", tmp / "i.sqlite", cargador)
    t = time.time()
    s = idx.actualizar()
    primera = time.time() - t
    (tmp / "b" / "20 Intereses" / "Syncthing.md").write_text("cambio\n", encoding="utf-8")
    t = time.time()
    s2 = idx.actualizar()
    segunda = time.time() - t

    print(f"Notas: {len(idx.notas)} · modelo: {idx.estado_modelo()}")
    if modelo:
        tam = sum(p.stat().st_size for p in carpeta_modelo().iterdir()) / 1e6
        print(f"Modelo en disco: {tam:.0f} MB · carga {carga:.1f} s")
    print(f"Índice: primera vez {primera * 1000:.0f} ms ({s['nuevas']} notas, {s['vectorizadas']} vectores) · "
          f"tras cambiar 1 nota {segunda * 1000:.0f} ms ({s2['cambiadas']} releída, {s2['vectorizadas']} vector)")

    print("\nConsultas con sinónimos (¿aparece una nota correcta en el top 3?)")
    ok_bm25 = ok_sem = 0
    for consulta, esperados in SINONIMOS:
        b = {r["titulo"] for r in idx.buscar(consulta, 3)} & esperados
        ok_bm25 += bool(b)
        linea = f"  palabras {'sí' if b else 'no'}"
        if modelo:
            r = idx.buscar_parecido(consulta, 3)["resultados"]
            hit = {x["titulo"] for x in r} & esperados
            ok_sem += bool(hit)
            linea += f" · significado {'sí' if hit else 'no'} ({r[0]['titulo']} {r[0]['puntuacion']})"
        print(f"{linea} · «{consulta}»")
    print(f"  Total: palabras {ok_bm25}/{len(SINONIMOS)}" + (f" · significado {ok_sem}/{len(SINONIMOS)}" if modelo else ""))

    print(f"\nPosibles duplicados ({'significado' if modelo else 'palabras'}, umbral por defecto)")
    for nombre, casos in [("casi iguales", DUPLICADOS), ("paráfrasis", DUPLICADOS_PARAFRASIS)]:
        hits = sum(bool({d["titulo"] for d in idx.posible_duplicado(t)["duplicados"]} & e) for t, e in casos)
        print(f"  {nombre}: {hits}/{len(casos)} detectados")
    falsos = sum(bool(idx.posible_duplicado(t)["duplicados"]) for t in NO_DUPLICADOS)
    print(f"  textos sin relación marcados como duplicado: {falsos}/{len(NO_DUPLICADOS)}")
    shutil.rmtree(tmp)


if __name__ == "__main__":
    main()
