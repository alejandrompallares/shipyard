"""Servidor MCP (stdio) con las herramientas de búsqueda sobre la bóveda."""
from __future__ import annotations

from mcp.server.mcpserver import MCPServer

from .indice import Indice
from .notas import CARPETAS

INSTRUCCIONES = f"""Bóveda de notas Markdown (compatible con Jylos y Obsidian).
- buscar: por palabras exactas (BM25). buscar_parecido: por significado, encuentra sinónimos y paráfrasis.
- Antes de crear una nota, usa posible_duplicado; si ya hay una del tema, amplíala en vez de crear otra.
- Títulos sin paréntesis, comas ni dos puntos. Carpetas: {", ".join(CARPETAS)}."""


def crear_servidor(indice: Indice) -> MCPServer:
    mcp = MCPServer("notas", instructions=INSTRUCCIONES)

    @mcp.tool()
    def buscar(consulta: str, n: int = 8) -> list[dict]:
        """Busca notas por palabras (BM25). Rápido y exacto; no entiende sinónimos."""
        return indice.buscar(consulta, n)

    @mcp.tool()
    def buscar_parecido(consulta: str, n: int = 8) -> dict:
        """Busca notas por significado (embeddings), aunque no compartan palabras con la consulta.
        Si el modelo no está disponible, busca por palabras y lo indica en «modo»."""
        return indice.buscar_parecido(consulta, n)

    @mcp.tool()
    def relacionadas(titulo: str) -> dict:
        """Notas enlazadas desde esta, las que la enlazan (backlinks) y las que quedan a dos saltos."""
        return indice.relacionadas(titulo)

    @mcp.tool()
    def posible_duplicado(texto: str, umbral: float | None = None) -> dict:
        """Dado el texto de una nota nueva, devuelve las notas existentes con similitud >= umbral
        (por defecto 0.85 con el modelo y 0.25 por palabras)."""
        return indice.posible_duplicado(texto, umbral)

    @mcp.tool()
    def leer_nota(titulo: str) -> dict:
        """Devuelve el contenido completo de una nota, con sus campos y enlaces."""
        return indice.leer(titulo)

    @mcp.tool()
    def crear_nota(titulo: str, carpeta: str, contenido: str, campos: dict[str, str] | None = None) -> dict:
        """Crea una nota nueva (nunca sobrescribe). Título sin paréntesis, comas ni dos puntos.
        carpeta: 00 Inbox, 10 Proyectos, 20 Intereses, 30 Conocimiento, 40 Sesiones o 90 Mapas.
        campos: se escriben al principio como «clave:: valor» (tipo, estado, sirve-para…)."""
        return indice.crear(titulo, carpeta, contenido, campos)

    return mcp
