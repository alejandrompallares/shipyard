"""El índice en disco solo relee lo que cambia."""
import os
import time

from conftest import CargadorFijo
from motor_notas.indice import Indice


def test_actualiza_solo_lo_cambiado(boveda, ruta_indice):
    idx = Indice(boveda, ruta_indice)
    s = idx.actualizar()
    assert s["nuevas"] == 41 and idx.leidas == 41
    assert idx.actualizar() == {"nuevas": 0, "cambiadas": 0, "borradas": 0, "vectorizadas": 0}

    nota = boveda / "20 Intereses" / "Syncthing.md"
    nota.write_text(nota.read_text(encoding="utf-8") + "\nAñadido: funciona en Android.\n", encoding="utf-8")
    (boveda / "30 Conocimiento" / "BM25.md").unlink()
    s = idx.actualizar()
    assert (s["cambiadas"], s["borradas"], idx.leidas) == (1, 1, 42)
    assert "Android" in idx.buscar("android")[0]["fragmento"]


def test_el_indice_persiste_entre_arranques(boveda, ruta_indice):
    Indice(boveda, ruta_indice).actualizar()
    otro = Indice(boveda, ruta_indice)
    s = otro.actualizar()
    assert s["nuevas"] == 0 and otro.leidas == 0
    assert otro.buscar("restic")


def test_misma_fecha_distinto_tamano_tambien_cuenta(boveda, ruta_indice):
    idx = Indice(boveda, ruta_indice)
    idx.actualizar()
    nota = boveda / "30 Conocimiento" / "BM25.md"
    st = nota.stat()
    nota.write_text(nota.read_text(encoding="utf-8") + "x", encoding="utf-8")
    os.utime(nota, ns=(st.st_atime_ns, st.st_mtime_ns))
    assert idx.actualizar()["cambiadas"] == 1


def test_vectores_solo_de_lo_cambiado(boveda, ruta_indice, modelo_juguete):
    idx = Indice(boveda, ruta_indice, CargadorFijo(modelo_juguete))
    assert idx.actualizar()["vectorizadas"] == 41
    assert idx.actualizar()["vectorizadas"] == 0
    time.sleep(0.01)
    (boveda / "00 Inbox" / "Nueva.md").write_text("respaldo de archivos\n", encoding="utf-8")
    assert idx.actualizar()["vectorizadas"] == 1
    # al reabrir, los vectores siguen en disco
    assert Indice(boveda, ruta_indice, CargadorFijo(modelo_juguete)).actualizar()["vectorizadas"] == 0
