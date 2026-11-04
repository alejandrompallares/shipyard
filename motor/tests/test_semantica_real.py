"""Con el modelo granite de verdad. Se salta si no está descargado (motor-notas descargar)."""
import pytest

from consultas import DUPLICADOS, DUPLICADOS_PARAFRASIS, NO_DUPLICADOS, SINONIMOS
from motor_notas.embeddings import Cargador, carpeta_modelo
from motor_notas.indice import Indice

pytestmark = pytest.mark.skipif(not (carpeta_modelo() / "model.onnx").exists(),
                                reason="modelo granite no descargado: ejecuta `motor-notas descargar`")

# Casos que granite base no resuelve hoy. Se dejan a la vista, y si otro modelo los resuelve no fallan.
LIMITES = {
    "aprovechar restos de comida para abonar": "granite base no lo sitúa entre los 3 primeros",
    DUPLICADOS_PARAFRASIS[0][0]: "la paráfrasis queda por debajo del umbral de duplicados",
}


def con_limites(casos):
    return [pytest.param(*c, marks=pytest.mark.xfail(reason=LIMITES[c[0]], strict=False)) if c[0] in LIMITES else c
            for c in casos]


@pytest.fixture(scope="module")
def indice(tmp_path_factory):
    import shutil

    from conftest import BOVEDA
    destino = tmp_path_factory.mktemp("real") / "boveda"
    shutil.copytree(BOVEDA, destino)
    cargador = Cargador(descargar_si_falta=False)
    assert cargador.obtener(esperar=120), cargador.estado
    return Indice(destino, destino.parent / "i.sqlite", cargador)


@pytest.mark.parametrize("consulta,esperados", con_limites(SINONIMOS))
def test_encuentra_sinonimos_en_top3(indice, consulta, esperados):
    r = indice.buscar_parecido(consulta, 3)
    assert r["modo"] == "significado"
    assert {x["titulo"] for x in r["resultados"]} & esperados


@pytest.mark.parametrize("texto,esperados", con_limites(DUPLICADOS + DUPLICADOS_PARAFRASIS))
def test_duplicados(indice, texto, esperados):
    assert {d["titulo"] for d in indice.posible_duplicado(texto)["duplicados"]} & esperados


@pytest.mark.parametrize("texto", NO_DUPLICADOS)
def test_sin_falsos_duplicados(indice, texto):
    assert indice.posible_duplicado(texto)["duplicados"] == []
