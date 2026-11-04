"""Índice en disco de una bóveda. Solo relee las notas cuya fecha de modificación o tamaño cambió.

El índice es un SQLite en la caché del usuario (no dentro de la bóveda), con:
- notas: lo parseado de cada nota y sus tokens para BM25;
- vectores: el embedding de cada nota y con qué modelo se hizo.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
import threading
from pathlib import Path

import numpy as np

from .bm25 import BM25, normalizar, tokens
from .embeddings import Cargador, cache_dir
from .notas import CARPETAS, Nota, archivos_md, clave, leer_archivo, validar_titulo

UMBRAL_MODELO = 0.85   # coseno entre embeddings
UMBRAL_PALABRAS = 0.25  # coseno TF-IDF sin modelo (en la bóveda de ejemplo: duplicados 0,31-0,74; distintas ≤ 0,12)


def ruta_indice_por_defecto(boveda: Path) -> Path:
    h = hashlib.sha1(str(boveda.resolve()).encode()).hexdigest()[:12]
    return cache_dir() / "indices" / f"{boveda.name}-{h}.sqlite"


class Indice:
    def __init__(self, boveda: str | Path, ruta_indice: str | Path | None = None, cargador: Cargador | None = None):
        self.boveda = Path(boveda).expanduser().resolve()
        if not self.boveda.is_dir():
            raise FileNotFoundError(f"no existe la bóveda {self.boveda}")
        ruta = Path(ruta_indice) if ruta_indice else ruta_indice_por_defecto(self.boveda)
        ruta.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(ruta, check_same_thread=False)
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS notas (
                ruta TEXT PRIMARY KEY, mtime INTEGER, tamano INTEGER, titulo TEXT,
                campos TEXT, cuerpo TEXT, enlaces TEXT, tokens TEXT);
            CREATE TABLE IF NOT EXISTS vectores (
                ruta TEXT PRIMARY KEY, modelo TEXT, mtime INTEGER, vector BLOB);
        """)
        self.cargador = cargador
        self.lock = threading.RLock()
        self.notas: dict[str, Nota] = {}
        self._tokens: dict[str, list[str]] = {}
        self._bm25: BM25 | None = None
        self._matriz: tuple[str, list[str], np.ndarray] | None = None  # (modelo, rutas, vectores)
        self.leidas = 0  # notas parseadas desde disco (para tests y estadísticas)
        self._cargar_de_db()

    # ---------- carga y actualización ----------

    def _cargar_de_db(self):
        for ruta, titulo, campos, cuerpo, enlaces, toks in self.db.execute(
                "SELECT ruta, titulo, campos, cuerpo, enlaces, tokens FROM notas"):
            self.notas[ruta] = Nota(titulo, ruta, json.loads(campos), cuerpo, json.loads(enlaces))
            self._tokens[ruta] = json.loads(toks)

    def actualizar(self) -> dict:
        """Relee lo cambiado y calcula los vectores que falten. Devuelve qué ha cambiado."""
        with self.lock:
            stats = {"nuevas": 0, "cambiadas": 0, "borradas": 0, "vectorizadas": 0}
            en_db = {r: (m, t) for r, m, t in self.db.execute("SELECT ruta, mtime, tamano FROM notas")}
            vistas = set()
            for archivo in archivos_md(self.boveda):
                st = archivo.stat()
                rel = archivo.relative_to(self.boveda).as_posix()
                vistas.add(rel)
                if en_db.get(rel) == (st.st_mtime_ns, st.st_size):
                    continue
                stats["cambiadas" if rel in en_db else "nuevas"] += 1
                nota = leer_archivo(self.boveda, archivo)
                self.leidas += 1
                toks = tokens(nota.titulo) * 2 + tokens(nota.texto_busqueda())  # el título pesa doble
                self.db.execute("INSERT OR REPLACE INTO notas VALUES (?,?,?,?,?,?,?,?)", (
                    rel, st.st_mtime_ns, st.st_size, nota.titulo, json.dumps(nota.campos, ensure_ascii=False),
                    nota.cuerpo, json.dumps(nota.enlaces, ensure_ascii=False), json.dumps(toks)))
                self.db.execute("DELETE FROM vectores WHERE ruta = ?", (rel,))
                self.notas[rel], self._tokens[rel] = nota, toks
            for rel in set(en_db) - vistas:
                stats["borradas"] += 1
                self.db.execute("DELETE FROM notas WHERE ruta = ?", (rel,))
                self.db.execute("DELETE FROM vectores WHERE ruta = ?", (rel,))
                self.notas.pop(rel, None)
                self._tokens.pop(rel, None)
            if stats["nuevas"] or stats["cambiadas"] or stats["borradas"] or self._bm25 is None:
                self._bm25 = BM25(self._tokens)
                self._por_clave = {clave(n.titulo): r for r, n in self.notas.items()}
                self._matriz = None
            stats["vectorizadas"] = self._vectorizar()
            self.db.commit()
            return stats

    def _modelo(self):
        return self.cargador.obtener() if self.cargador else None

    def _vectorizar(self) -> int:
        modelo = self._modelo()
        if modelo is None:
            return 0
        hechas = {r for (r,) in self.db.execute("SELECT ruta FROM vectores WHERE modelo = ?", (modelo.nombre,))}
        faltan = [r for r in self.notas if r not in hechas]
        if faltan:
            vecs = modelo.codificar([self.notas[r].texto_busqueda() for r in faltan])
            self.db.executemany("INSERT OR REPLACE INTO vectores VALUES (?,?,?,?)",
                                [(r, modelo.nombre, 0, v.astype(np.float32).tobytes()) for r, v in zip(faltan, vecs)])
            self._matriz = None
        if self._matriz is None or self._matriz[0] != modelo.nombre:
            filas = self.db.execute("SELECT ruta, vector FROM vectores WHERE modelo = ?", (modelo.nombre,)).fetchall()
            filas = [(r, v) for r, v in filas if r in self.notas]
            rutas = [r for r, _ in filas]
            matriz = np.vstack([np.frombuffer(v, dtype=np.float32) for _, v in filas]) if filas else np.zeros((0, 1))
            self._matriz = (modelo.nombre, rutas, matriz)
        return len(faltan)

    # ---------- utilidades ----------

    def resolver(self, titulo: str) -> Nota | None:
        self.actualizar()
        destino = titulo.strip().removeprefix("[[").removesuffix("]]").rsplit("/", 1)[-1]
        destino = destino.removesuffix(".md")
        r = self._por_clave.get(clave(destino))
        return self.notas.get(r) if r else None

    def _ficha(self, ruta: str, puntuacion: float | None = None, consulta: str = "") -> dict:
        n = self.notas[ruta]
        ficha = {"titulo": n.titulo, "carpeta": n.carpeta}
        if n.campos.get("tipo"):
            ficha["tipo"] = n.campos["tipo"]
        if puntuacion is not None:
            ficha["puntuacion"] = round(float(puntuacion), 3)
        ficha["fragmento"] = fragmento(n, consulta)
        return ficha

    # ---------- herramientas ----------

    def buscar(self, consulta: str, n: int = 8) -> list[dict]:
        self.actualizar()
        return [self._ficha(r, s, consulta) for r, s in self._bm25.buscar(consulta, n)]

    def similares_por_modelo(self, texto: str) -> list[tuple[str, float]] | None:
        modelo = self._modelo()
        if modelo is None:
            return None
        self.actualizar()
        _, rutas, matriz = self._matriz
        if not rutas:
            return []
        q = modelo.codificar([texto])[0]
        sims = matriz @ q
        orden = np.argsort(-sims)
        return [(rutas[i], float(sims[i])) for i in orden]

    def buscar_parecido(self, consulta: str, n: int = 8) -> dict:
        sims = self.similares_por_modelo(consulta)
        if sims is None:
            return {"modo": "palabras (BM25): " + self.estado_modelo(), "resultados": self.buscar(consulta, n)}
        return {"modo": "significado", "resultados": [self._ficha(r, s, consulta) for r, s in sims[:n]]}

    def posible_duplicado(self, texto: str, umbral: float | None = None, n: int = 5) -> dict:
        sims = self.similares_por_modelo(texto)
        if sims is None:
            self.actualizar()
            umbral = UMBRAL_PALABRAS if umbral is None else umbral
            sims, modo = self._bm25.similitud(texto), "palabras (TF-IDF): " + self.estado_modelo()
        else:
            umbral = UMBRAL_MODELO if umbral is None else umbral
            modo = "significado"
        res = [self._ficha(r, s) for r, s in sims if s >= umbral][:n]
        return {"modo": modo, "umbral": umbral, "duplicados": res}

    def relacionadas(self, titulo: str) -> dict:
        nota = self.resolver(titulo)
        if not nota:
            return {"error": f"no encuentro la nota «{titulo}»"}
        vecinos: dict[str, set[str]] = {r: set() for r in self.notas}
        salientes, rotos = [], []
        for r, n in self.notas.items():
            for e in n.enlaces:
                destino = self._por_clave.get(clave(e))
                if destino and destino != r:
                    vecinos[r].add(destino)
                    vecinos[destino].add(r)
                if r == nota.ruta:
                    (salientes if destino else rotos).append(destino or e)
        entrantes = [r for r, n in self.notas.items()
                     if r != nota.ruta and any(self._por_clave.get(clave(e)) == nota.ruta for e in n.enlaces)]
        # notas a dos saltos (en cualquier dirección) que no están enlazadas directamente
        directas = vecinos[nota.ruta]
        dos = {}
        for v in directas:
            for w in vecinos[v]:
                if w != nota.ruta and w not in directas:
                    dos.setdefault(w, []).append(self.notas[v].titulo)
        t = lambda rs: sorted({self.notas[r].titulo for r in rs})  # noqa: E731
        return {
            "nota": nota.titulo,
            "enlaza_a": t(salientes),
            "enlazada_desde": t(entrantes),
            "a_dos_saltos": [{"titulo": self.notas[w].titulo, "via": sorted(set(vias))}
                             for w, vias in sorted(dos.items(), key=lambda x: (-len(x[1]), self.notas[x[0]].titulo))],
            "enlaces_rotos": sorted(set(rotos)),
        }

    def leer(self, titulo: str) -> dict:
        nota = self.resolver(titulo)
        if not nota:
            return {"error": f"no encuentro la nota «{titulo}»"}
        texto = (self.boveda / nota.ruta).read_text(encoding="utf-8", errors="replace")
        return {"titulo": nota.titulo, "ruta": nota.ruta, "campos": nota.campos,
                "enlaces": nota.enlaces, "contenido": texto}

    def crear(self, titulo: str, carpeta: str, contenido: str, campos: dict[str, str] | None = None) -> dict:
        titulo = titulo.strip()
        motivo = validar_titulo(titulo)
        if motivo:
            return {"error": motivo}
        if carpeta not in CARPETAS:
            return {"error": f"carpeta no válida: usa una de {', '.join(CARPETAS)}"}
        if self.resolver(titulo):
            return {"error": f"ya existe una nota «{titulo}»: léela y amplíala en vez de crear otra"}
        lineas = [f"{k}:: {v}" for k, v in (campos or {}).items()]
        texto = ("\n".join(lineas) + "\n\n" if lineas else "") + contenido.strip() + "\n"
        aviso = self.posible_duplicado(f"{titulo}\n{contenido}")
        destino = self.boveda / carpeta / f"{titulo}.md"
        destino.parent.mkdir(parents=True, exist_ok=True)
        with open(destino, "x", encoding="utf-8") as f:  # «x»: nunca sobrescribe
            f.write(texto)
        self.actualizar()
        res = {"creada": f"{carpeta}/{titulo}.md"}
        if aviso["duplicados"]:
            res["aviso"] = "se parece a notas que ya existen; valora fusionarlas"
            res["parecidas"] = [d["titulo"] for d in aviso["duplicados"]]
        return res

    def estado_modelo(self) -> str:
        return self.cargador.estado if self.cargador else "sin modelo"


def fragmento(nota: Nota, consulta: str = "", largo: int = 160) -> str:
    texto = " ".join(nota.cuerpo.split())
    if consulta:
        plano = normalizar(texto)
        for w in tokens(consulta):
            i = plano.find(w)
            if i >= 0:
                ini = max(0, i - largo // 3)
                return ("…" if ini else "") + texto[ini:ini + largo] + ("…" if ini + largo < len(texto) else "")
    return texto[:largo] + ("…" if len(texto) > largo else "")

