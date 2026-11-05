"""BM25: encuentra por palabras y NO encuentra por sinónimos (por eso hace falta el modelo)."""
import pytest

from consultas import SINONIMOS
from motor_notas.indice import Indice


@pytest.fixture
def indice(boveda, ruta_indice):
    return Indice(boveda, ruta_indice)


@pytest.mark.parametrize("consulta,esperado", [
    ("restic instantáneas", "Copias de seguridad con Restic"),
    ("riego goteros programador", "Riego por goteo"),
    ("masa madre harina", "Hacer pan de masa madre"),
    ("whisper reuniones", "Transcribir audio con Whisper"),
    ("chucrut", "Fermentar verduras"),
])
def test_bm25_encuentra_por_palabras(indice, consulta, esperado):
    titulos = [r["titulo"] for r in indice.buscar(consulta, 3)]
    assert esperado in titulos


@pytest.mark.parametrize("consulta,esperados", SINONIMOS)
def test_bm25_no_encuentra_sinonimos(indice, consulta, esperados):
    top3 = {r["titulo"] for r in indice.buscar(consulta, 3)}
    assert not (top3 & esperados), f"BM25 ya encuentra {top3 & esperados}: la consulta no sirve de prueba"


def test_sin_modelo_buscar_parecido_cae_a_bm25(indice):
    r = indice.buscar_parecido("restic", 3)
    assert r["modo"].startswith("palabras")
    assert r["resultados"][0]["titulo"] in {"Copias de seguridad con Restic", "Backups con Restic"}
