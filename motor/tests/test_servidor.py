"""Herramientas MCP: en proceso y por stdio, como las usaría Claude."""
import asyncio
import json
import os
import sys

import pytest

from motor_notas.indice import Indice
from motor_notas.servidor import crear_servidor

HERRAMIENTAS = {"buscar", "buscar_parecido", "relacionadas", "posible_duplicado", "leer_nota", "crear_nota"}


def llamar(mcp, nombre, args):
    res = asyncio.run(mcp.call_tool(nombre, args))
    if res.structured_content and "result" in res.structured_content:  # herramientas que devuelven listas
        return res.structured_content["result"]
    return json.loads(res.content[0].text)


@pytest.fixture
def mcp(boveda, ruta_indice):
    return crear_servidor(Indice(boveda, ruta_indice))


def test_lista_de_herramientas(mcp):
    assert {t.name for t in asyncio.run(mcp.list_tools())} == HERRAMIENTAS


def test_leer_nota(mcp):
    r = llamar(mcp, "leer_nota", {"titulo": "Syncthing"})
    assert r["campos"]["tipo"] == "herramienta" and "igual a igual" in r["contenido"]


@pytest.mark.parametrize("titulo", ["Restic (copias)", "Restic, copias", "Restic: copias"])
def test_crear_nota_rechaza_titulos_malos(mcp, boveda, titulo):
    r = llamar(mcp, "crear_nota", {"titulo": titulo, "carpeta": "00 Inbox", "contenido": "x"})
    assert "error" in r
    assert not list(boveda.rglob("Restic*copias*.md"))


def test_crear_nota(mcp, boveda):
    r = llamar(mcp, "crear_nota", {"titulo": "Kéfir de agua", "carpeta": "20 Intereses",
                                    "contenido": "Fermentación con nódulos de kéfir.",
                                    "campos": {"tipo": "interes", "estado": "idea"}})
    assert r["creada"] == "20 Intereses/Kéfir de agua.md"
    texto = (boveda / "20 Intereses" / "Kéfir de agua.md").read_text(encoding="utf-8")
    assert texto.startswith("tipo:: interes\nestado:: idea\n\nFermentación")
    assert llamar(mcp, "buscar", {"consulta": "kéfir nódulos", "n": 1})[0]["titulo"] == "Kéfir de agua"
    # no sobrescribe ni duplica, tampoco con otras mayúsculas
    assert "error" in llamar(mcp, "crear_nota", {"titulo": "kéfir de agua", "carpeta": "00 Inbox", "contenido": "y"})
    assert "error" in llamar(mcp, "crear_nota", {"titulo": "Otra", "carpeta": "Inventada", "contenido": "y"})


def test_crear_nota_avisa_de_parecidas(mcp):
    r = llamar(mcp, "crear_nota", {"titulo": "Restic otra vez", "carpeta": "00 Inbox",
                                    "contenido": "Backups cifrados con Restic: instantáneas incrementales y deduplicación de bloques."})
    assert "creada" in r and "Backups con Restic" in r["parecidas"]


def test_servidor_por_stdio(boveda, tmp_path):
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    async def probar():
        params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "motor_notas.cli", "--boveda", str(boveda), "--indice", str(tmp_path / "i.sqlite")],
            env={**os.environ, "MOTOR_SIN_MODELO": "1"})
        async with stdio_client(params) as (r, w):
            async with ClientSession(r, w) as s:
                await s.initialize()
                nombres = {t.name for t in (await s.list_tools()).tools}
                res = await s.call_tool("relacionadas", {"titulo": "Syncthing"})
                return nombres, json.loads(res.content[0].text)

    nombres, rel = asyncio.run(probar())
    assert nombres == HERRAMIENTAS
    assert "Copias de seguridad con Restic" in rel["enlaza_a"]
