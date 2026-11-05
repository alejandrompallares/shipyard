"""Camino ONNX → pooling CLS → normalizado, con el modelo de juguete (ver conftest.py)."""
import numpy as np

from conftest import CargadorFijo
from motor_notas.indice import Indice


def test_vectores_normalizados_y_sin_efecto_del_relleno(modelo_juguete):
    solo = modelo_juguete.codificar(["respaldo de archivos"])
    junto = modelo_juguete.codificar(["respaldo de archivos", "compost " * 40 + "dormir"])
    assert np.allclose(np.linalg.norm(junto, axis=1), 1.0, atol=1e-5)
    assert np.allclose(solo[0], junto[0], atol=1e-6)  # el padding no cambia el vector


def test_sinonimos_cerca_y_temas_distintos_lejos(modelo_juguete):
    a, b, c = modelo_juguete.codificar(["copias de seguridad", "respaldar ficheros", "abonar con compost"])
    assert a @ b > 0.9
    assert a @ c < 0.2


def test_buscar_parecido_con_modelo(boveda, ruta_indice, modelo_juguete):
    idx = Indice(boveda, ruta_indice, CargadorFijo(modelo_juguete))
    consulta = "respaldar ficheros para no perderlos"
    r = idx.buscar_parecido(consulta, 41)
    assert r["modo"] == "significado"
    punt = {x["titulo"]: x["puntuacion"] for x in r["resultados"]}
    # el modelo de juguete es una bolsa de palabras de 6 dimensiones: hay empates, así que miramos puntuaciones
    assert punt["Copias de seguridad con Restic"] > 0.9 and punt["Backups con Restic"] > 0.9
    assert punt["Riego por goteo"] < 0.5
    # BM25 con la misma consulta no las encuentra
    assert not {"Copias de seguridad con Restic", "Backups con Restic"} & {x["titulo"] for x in idx.buscar(consulta, 3)}


def test_duplicado_por_significado(boveda, ruta_indice, modelo_juguete):
    idx = Indice(boveda, ruta_indice, CargadorFijo(modelo_juguete))
    r = idx.posible_duplicado("Usar un reloj para trabajar en bloques sin distraerme", umbral=0.9)
    titulos = {d["titulo"] for d in r["duplicados"]}
    assert "Técnica Pomodoro" in titulos or "Trabajar en bloques de 25 minutos" in titulos
    assert not idx.posible_duplicado("gazpacho con pepino", umbral=0.9)["duplicados"]
