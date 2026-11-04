"""posible_duplicado por palabras (TF-IDF), sin modelo."""
import pytest

from consultas import DUPLICADOS, NO_DUPLICADOS
from motor_notas.indice import Indice


@pytest.fixture
def indice(boveda, ruta_indice):
    return Indice(boveda, ruta_indice)


@pytest.mark.parametrize("texto,esperados", DUPLICADOS)
def test_detecta_casi_duplicados(indice, texto, esperados):
    r = indice.posible_duplicado(texto)
    assert r["modo"].startswith("palabras")
    assert esperados <= {d["titulo"] for d in r["duplicados"]}


@pytest.mark.parametrize("texto", NO_DUPLICADOS)
def test_no_marca_textos_distintos(indice, texto):
    assert indice.posible_duplicado(texto)["duplicados"] == []
