"""Embeddings con ibm-granite/granite-embedding-107m-multilingual en ONNX.

- Pooling CLS (el vector del primer token) y normalizado L2, como indica la ficha del modelo.
- Se descarga la primera vez a la caché (unos cientos de MB) y después funciona sin conexión.
- Si no hay modelo (sin red, sin espacio o MOTOR_SIN_MODELO=1), quien llama cae a BM25.

Variables de entorno:
  MOTOR_MODELO_DIR    carpeta con model.onnx y tokenizer.json ya preparados (no descarga nada)
  MOTOR_MODELO_REPO   repo de Hugging Face (por defecto ibm-granite/granite-embedding-107m-multilingual)
  MOTOR_MODELO_ONNX   ruta del .onnx dentro del repo (por defecto prueba onnx/model.onnx y model.onnx)
  MOTOR_SIN_MODELO=1  no usar modelo: todo por palabras
"""
from __future__ import annotations

import os
import shutil
import sys
import threading
from pathlib import Path

import numpy as np

REPO = "ibm-granite/granite-embedding-107m-multilingual"
ONNX_CANDIDATOS = ("onnx/model.onnx", "model.onnx")
MAX_TOKENS = 512


def cache_dir() -> Path:
    base = os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache"
    return Path(base) / "motor-notas"


class Modelo:
    """Envuelve una sesión ONNX y su tokenizer. Sirve para cualquier encoder tipo BERT/XLM-R."""

    def __init__(self, carpeta: Path):
        import onnxruntime as ort
        from tokenizers import Tokenizer

        carpeta = Path(carpeta)
        opciones = ort.SessionOptions()
        opciones.log_severity_level = 3
        self.sesion = ort.InferenceSession(str(carpeta / "model.onnx"), opciones, providers=["CPUExecutionProvider"])
        self.entradas = {i.name for i in self.sesion.get_inputs()}
        self.tok = Tokenizer.from_file(str(carpeta / "tokenizer.json"))
        self.tok.enable_truncation(MAX_TOKENS)
        pad_id = self.tok.token_to_id("<pad>")
        if pad_id is None:
            pad_id = self.tok.token_to_id("[PAD]") or 0
        self.tok.enable_padding(pad_id=pad_id)
        self.nombre = (carpeta / "NOMBRE").read_text().strip() if (carpeta / "NOMBRE").exists() else carpeta.name

    def codificar(self, textos: list[str], lote: int = 16) -> np.ndarray:
        salida = []
        for i in range(0, len(textos), lote):
            enc = self.tok.encode_batch(textos[i:i + lote])
            ids = np.array([e.ids for e in enc], dtype=np.int64)
            mask = np.array([e.attention_mask for e in enc], dtype=np.int64)
            feed = {"input_ids": ids, "attention_mask": mask}
            if "token_type_ids" in self.entradas:
                feed["token_type_ids"] = np.zeros_like(ids)
            feed = {k: v for k, v in feed.items() if k in self.entradas}
            ocultos = self.sesion.run(None, feed)[0]  # (lote, tokens, dim)
            cls = ocultos[:, 0, :] if ocultos.ndim == 3 else ocultos
            normas = np.linalg.norm(cls, axis=1, keepdims=True)
            salida.append(cls / np.maximum(normas, 1e-12))
        if not salida:
            return np.zeros((0, 0), dtype=np.float32)
        return np.vstack(salida).astype(np.float32)


def carpeta_modelo() -> Path:
    if os.environ.get("MOTOR_MODELO_DIR"):
        return Path(os.environ["MOTOR_MODELO_DIR"])
    repo = os.environ.get("MOTOR_MODELO_REPO", REPO)
    return cache_dir() / "modelos" / repo.replace("/", "--")


def descargar(log=lambda m: print(m, file=sys.stderr)) -> Path:
    """Descarga model.onnx y tokenizer.json a la caché. Devuelve la carpeta."""
    from huggingface_hub import hf_hub_download

    destino = carpeta_modelo()
    if (destino / "model.onnx").exists() and (destino / "tokenizer.json").exists():
        return destino
    if os.environ.get("MOTOR_MODELO_DIR"):
        raise FileNotFoundError(f"{destino} no tiene model.onnx y tokenizer.json")
    repo = os.environ.get("MOTOR_MODELO_REPO", REPO)
    candidatos = [os.environ["MOTOR_MODELO_ONNX"]] if os.environ.get("MOTOR_MODELO_ONNX") else ONNX_CANDIDATOS
    destino.mkdir(parents=True, exist_ok=True)
    bajada = destino / "descarga"
    log(f"Descargando {repo} (solo la primera vez)…")
    ultimo_error = None
    for nombre in candidatos:
        try:
            onnx = Path(hf_hub_download(repo, nombre, local_dir=bajada))
            break
        except Exception as e:  # probamos el siguiente
            ultimo_error = e
    else:
        raise RuntimeError(f"no se pudo descargar el ONNX de {repo} (probé {', '.join(candidatos)}): {ultimo_error}")
    try:  # algunos ONNX guardan los pesos aparte (model.onnx_data)
        datos = Path(hf_hub_download(repo, nombre + "_data", local_dir=bajada))
        shutil.move(datos, destino / "model.onnx_data")
    except Exception:
        pass
    shutil.move(Path(hf_hub_download(repo, "tokenizer.json", local_dir=bajada)), destino / "tokenizer.json")
    shutil.move(onnx, destino / "model.onnx")
    shutil.rmtree(bajada, ignore_errors=True)
    (destino / "NOMBRE").write_text(repo)
    tam = sum(p.stat().st_size for p in destino.iterdir()) / 1e6
    log(f"Modelo listo en {destino} ({tam:.0f} MB).")
    return destino


class Cargador:
    """Carga el modelo en segundo plano para que el servidor arranque al momento."""

    def __init__(self, descargar_si_falta: bool = True):
        self.modelo: Modelo | None = None
        self.error: str | None = None
        self._listo = threading.Event()
        if os.environ.get("MOTOR_SIN_MODELO") == "1":
            self.error = "desactivado con MOTOR_SIN_MODELO=1"
            self._listo.set()
            return
        self._hilo = threading.Thread(target=self._cargar, args=(descargar_si_falta,), daemon=True)
        self._hilo.start()

    def _cargar(self, descargar_si_falta: bool):
        try:
            carpeta = carpeta_modelo()
            if not (carpeta / "model.onnx").exists():
                if not descargar_si_falta:
                    raise FileNotFoundError("modelo no descargado (motor-notas descargar)")
                carpeta = descargar()
            self.modelo = Modelo(carpeta)
        except Exception as e:
            self.error = f"{type(e).__name__}: {e}"
            print(f"motor-notas: sin modelo de embeddings, uso BM25 ({self.error})", file=sys.stderr)
        finally:
            self._listo.set()

    def obtener(self, esperar: float = 0.0) -> Modelo | None:
        self._listo.wait(esperar)
        return self.modelo

    @property
    def estado(self) -> str:
        if self.modelo:
            return f"modelo {self.modelo.nombre}"
        if not self._listo.is_set():
            return "cargando el modelo (mientras, por palabras)"
        return f"sin modelo: {self.error}"
