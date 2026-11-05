"""Búsqueda por palabras: BM25 y similitud TF-IDF (para duplicados sin modelo)."""
from __future__ import annotations

import math
import re
import unicodedata
from collections import Counter

# Palabras vacías del español (y unas pocas del inglés que aparecen en notas técnicas).
VACIAS = set("""
a al algo algun alguna algunas alguno algunos ante antes aqui asi aun bajo bien cada casi como con contra cual
cuales cuando de del desde donde dos e el ella ellas ello ellos en entre era eran es esa esas ese eso esos esta
estaba estan estar este esto estos fue fueron ha habia han hasta hay la las le les lo los mas me mi mis mucho muy
muchos nada ni no nos nosotros o os otra otras otro otros para pero poco por porque que quien se sea segun ser si
sin sobre solo son su sus tambien tan tanto te tiene tienen todo todos tu tus un una unas uno unos usar y ya yo
the of and to in is for on with
""".split())

TOKEN_RE = re.compile(r"\w+", re.UNICODE)


def normalizar(texto: str) -> str:
    t = unicodedata.normalize("NFKD", texto.lower())
    return "".join(c for c in t if not unicodedata.combining(c))


def raiz(palabra: str) -> str:
    """Raíz muy ligera: quita plurales para que «copias» y «copia» coincidan."""
    if len(palabra) > 4 and palabra.endswith("es") and palabra[-3] not in "aeiou":
        return palabra[:-2]
    if len(palabra) > 3 and palabra.endswith("s"):
        return palabra[:-1]
    return palabra


def tokens(texto: str) -> list[str]:
    return [raiz(w) for w in TOKEN_RE.findall(normalizar(texto)) if w not in VACIAS and len(w) > 1]


class BM25:
    def __init__(self, docs: dict[str, list[str]], k1: float = 1.5, b: float = 0.75):
        self.k1, self.b = k1, b
        self.tf = {d: Counter(t) for d, t in docs.items()}
        self.largo = {d: len(t) for d, t in docs.items()}
        n = len(docs) or 1
        self.media = sum(self.largo.values()) / n or 1.0
        df: Counter = Counter()
        for c in self.tf.values():
            df.update(c.keys())
        self.idf = {w: math.log(1 + (n - f + 0.5) / (f + 0.5)) for w, f in df.items()}

    def buscar(self, consulta: str, n: int = 10) -> list[tuple[str, float]]:
        q = tokens(consulta)
        puntos = {}
        for d, tf in self.tf.items():
            s = 0.0
            for w in q:
                f = tf.get(w)
                if not f:
                    continue
                s += self.idf[w] * f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * self.largo[d] / self.media))
            if s > 0:
                puntos[d] = s
        return sorted(puntos.items(), key=lambda x: -x[1])[:n]

    def vector_tfidf(self, toks: list[str]) -> dict[str, float]:
        c = Counter(toks)
        v = {w: (1 + math.log(f)) * self.idf.get(w, math.log(1 + len(self.tf))) for w, f in c.items()}
        norma = math.sqrt(sum(x * x for x in v.values())) or 1.0
        return {w: x / norma for w, x in v.items()}

    def similitud(self, texto: str) -> list[tuple[str, float]]:
        """Coseno TF-IDF entre el texto y cada nota (0 a 1)."""
        q = self.vector_tfidf(tokens(texto))
        res = []
        for d, tf in self.tf.items():
            v = self.vector_tfidf(list(tf.elements()))
            res.append((d, sum(x * v.get(w, 0.0) for w, x in q.items())))
        return sorted(res, key=lambda x: -x[1])
