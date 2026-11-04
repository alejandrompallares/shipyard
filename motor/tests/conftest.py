import shutil
import sys
from pathlib import Path

import pytest

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
BOVEDA = AQUI.parent / "boveda-ejemplo"


@pytest.fixture
def boveda(tmp_path):
    """Copia de la bóveda de ejemplo, para poder modificarla."""
    destino = tmp_path / "boveda"
    shutil.copytree(BOVEDA, destino)
    return destino


@pytest.fixture
def ruta_indice(tmp_path):
    return tmp_path / "indice.sqlite"


# ---------- modelo ONNX de juguete ----------
# Un «encoder» mínimo con la misma interfaz que granite (input_ids, attention_mask → last_hidden_state).
# En la posición 0 (la del CLS) pone la suma de los vectores de las palabras, así que con pooling CLS
# y normalizado se comporta como una bolsa de palabras en la que los sinónimos comparten vector.
# Sirve para probar todo el camino ONNX → pooling → normalizado → índice, NO la calidad de granite.

GRUPOS = [
    ["copia", "copias", "backup", "backups", "respaldar", "respaldo", "ficheros", "archivos", "perderlos", "seguridad"],
    ["compost", "compostaje", "compostera", "abonar", "abono", "restos", "peladuras"],
    ["pomodoro", "pomodoros", "concentrarme", "bloques", "temporizador", "reloj", "distraerme", "minutos"],
    ["sueño", "dormir", "insomnio", "descanso", "noches", "acostarse"],
    ["gazpacho", "pepino"],
]


def construir_modelo_juguete(carpeta: Path) -> Path:
    import numpy as np
    import onnx
    from onnx import TensorProto, helper, numpy_helper
    from tokenizers import Tokenizer, normalizers, pre_tokenizers, processors
    from tokenizers.models import WordLevel

    vocab = {"[PAD]": 0, "[UNK]": 1, "[CLS]": 2}
    for g in GRUPOS:
        for w in g:
            vocab.setdefault(w, len(vocab))
    dim = len(GRUPOS) + 1
    tabla = np.zeros((len(vocab), dim), dtype=np.float32)
    for i, g in enumerate(GRUPOS):
        for w in g:
            tabla[vocab[w], i] = 1.0
    tabla[vocab["[CLS]"], -1] = 0.05  # evita vectores nulos

    tok = Tokenizer(WordLevel(vocab, unk_token="[UNK]"))
    tok.normalizer = normalizers.Lowercase()
    tok.pre_tokenizer = pre_tokenizers.Whitespace()
    tok.post_processor = processors.TemplateProcessing(single="[CLS] $A", special_tokens=[("[CLS]", 2)])
    carpeta.mkdir(parents=True, exist_ok=True)
    tok.save(str(carpeta / "tokenizer.json"))

    nodos = [
        helper.make_node("Gather", ["E", "input_ids"], ["emb"]),
        helper.make_node("Cast", ["attention_mask"], ["maskf"], to=TensorProto.FLOAT),
        helper.make_node("Unsqueeze", ["maskf", "ax2"], ["mask3"]),
        helper.make_node("Mul", ["emb", "mask3"], ["embm"]),
        helper.make_node("ReduceSum", ["embm", "ax1"], ["suma"], keepdims=1),
        helper.make_node("Concat", ["suma", "embm"], ["last_hidden_state"], axis=1),
    ]
    grafo = helper.make_graph(
        nodos, "juguete",
        [helper.make_tensor_value_info("input_ids", TensorProto.INT64, ["b", "t"]),
         helper.make_tensor_value_info("attention_mask", TensorProto.INT64, ["b", "t"])],
        [helper.make_tensor_value_info("last_hidden_state", TensorProto.FLOAT, ["b", "t1", dim])],
        initializer=[numpy_helper.from_array(tabla, "E"),
                     numpy_helper.from_array(np.array([1], dtype=np.int64), "ax1"),
                     numpy_helper.from_array(np.array([2], dtype=np.int64), "ax2")],
    )
    modelo = helper.make_model(grafo, opset_imports=[helper.make_opsetid("", 17)])
    modelo.ir_version = 8
    onnx.save(modelo, str(carpeta / "model.onnx"))
    (carpeta / "NOMBRE").write_text("juguete")
    return carpeta


class CargadorFijo:
    """Sustituye a embeddings.Cargador con un modelo ya cargado."""

    def __init__(self, modelo):
        self.modelo = modelo
        self.estado = f"modelo {modelo.nombre}"

    def obtener(self, esperar=0.0):
        return self.modelo


@pytest.fixture(scope="session")
def modelo_juguete(tmp_path_factory):
    from motor_notas.embeddings import Modelo
    return Modelo(construir_modelo_juguete(tmp_path_factory.mktemp("juguete")))
