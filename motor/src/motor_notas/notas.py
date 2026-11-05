"""Lectura de notas Markdown al estilo Jylos/Obsidian.

- El título es el nombre del archivo sin `.md`.
- Jylos empieza cada nota con un bloque YAML (`---` … `---`): no es texto de la nota; de él solo se usan las etiquetas.
- Los campos `clave:: valor` van al principio de la nota (antes del primer texto normal).
- Los enlaces son `[[Título]]`, `[[Título|alias]]` o `[[Título#sección]]`.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

CARPETAS = ("00 Inbox", "10 Proyectos", "20 Intereses", "30 Conocimiento", "40 Sesiones", "90 Mapas")

CAMPO_RE = re.compile(r"^([\w][\w-]*)::[ \t]*(.*)$")
ENLACE_RE = re.compile(r"\[\[([^\]\|#\n]+)(?:#[^\]\|\n]*)?(?:\|[^\]\n]*)?\]\]")
# El bloque solo cuenta si su primera línea es «clave:»; así un «---» suelto al principio sigue siendo una línea horizontal.
YAML_RE = re.compile(r"\A\ufeff?---[ \t]*\r?\n(?=[\w-]+:)(.*?)^---[ \t]*(?:\r?\n|\Z)", re.S | re.M)
ETIQUETA_RE = re.compile(r"^[ \t]*-[ \t]+(.+?)[ \t]*$", re.M)
# Prohibidos por la regla de títulos (Jylos los cambia por _) y por el sistema de archivos.
TITULO_PROHIBIDO = re.compile(r"[(),:/\\\[\]#|^?*\"<>]")


@dataclass
class Nota:
    titulo: str
    ruta: str  # relativa a la bóveda, con /
    campos: dict[str, str] = field(default_factory=dict)
    cuerpo: str = ""
    enlaces: list[str] = field(default_factory=list)

    @property
    def carpeta(self) -> str:
        return self.ruta.rsplit("/", 1)[0] if "/" in self.ruta else ""

    def texto_busqueda(self) -> str:
        """Lo que se indexa: título, campos útiles y cuerpo."""
        campos = " ".join(v for k, v in self.campos.items() if k not in {"creado", "autor"})
        return f"{self.titulo}\n{campos}\n{self.cuerpo}"


def separar_yaml(texto: str) -> tuple[str, list[str]]:
    """Devuelve el texto sin el bloque YAML inicial y las etiquetas que traía."""
    m = YAML_RE.match(texto)
    if not m:
        return texto, []
    bloque = re.search(r"^tags:[ \t]*\r?\n((?:[ \t]*-[ \t]+.*(?:\r?\n|\Z))+)", m.group(1), re.M)
    return texto[m.end():], ETIQUETA_RE.findall(bloque.group(1)) if bloque else []


def parsear(texto: str, titulo: str, ruta: str) -> Nota:
    texto, etiquetas = separar_yaml(texto)
    lineas = texto.splitlines()
    campos: dict[str, str] = {}
    i = 0
    while i < len(lineas):
        linea = lineas[i].strip()
        if not linea:
            i += 1
            continue
        m = CAMPO_RE.match(linea)
        if not m:
            break
        campos[m.group(1).lower()] = m.group(2).strip()
        i += 1
    if etiquetas:
        campos["etiquetas"] = " ".join(etiquetas)
    cuerpo = "\n".join(lineas[i:]).strip()
    enlaces = []
    for m in ENLACE_RE.finditer(texto):
        destino = m.group(1).strip().rsplit("/", 1)[-1]
        if destino and destino not in enlaces:
            enlaces.append(destino)
    return Nota(titulo=titulo, ruta=ruta, campos=campos, cuerpo=cuerpo, enlaces=enlaces)


def leer_archivo(boveda: Path, archivo: Path) -> Nota:
    rel = archivo.relative_to(boveda).as_posix()
    return parsear(archivo.read_text(encoding="utf-8", errors="replace"), archivo.stem, rel)


def archivos_md(boveda: Path):
    """Todas las notas .md, sin carpetas ocultas (.obsidian, .trash, .motor…)."""
    for p in sorted(boveda.rglob("*.md")):
        partes = p.relative_to(boveda).parts
        if any(x.startswith(".") for x in partes):
            continue
        yield p


def clave(titulo: str) -> str:
    """Clave para resolver enlaces: sin mayúsculas ni acentos."""
    t = unicodedata.normalize("NFKD", titulo.strip().lower())
    return "".join(c for c in t if not unicodedata.combining(c))


def validar_titulo(titulo: str) -> str | None:
    """Devuelve el motivo si el título no vale, o None si vale."""
    t = titulo.strip()
    if not t:
        return "el título está vacío"
    if t.startswith("."):
        return "el título no puede empezar por punto"
    malos = sorted(set(TITULO_PROHIBIDO.findall(t)))
    if malos:
        return ("el título no puede llevar " + " ".join(malos)
                + " (sin paréntesis, comas ni dos puntos: Jylos los cambia por _ y los enlaces se rompen)")
    if len(t) > 150:
        return "el título es demasiado largo (máximo 150 caracteres)"
    return None
