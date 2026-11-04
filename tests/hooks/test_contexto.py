"""python3 -m unittest discover tests/hooks"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
import uuid
from pathlib import Path

HOOK = Path(__file__).resolve().parents[2] / "plugins/shipyard/hooks/contexto.py"


def turno(tokens, **extra):
    return json.dumps({"type": "assistant", "message": {"usage": {
        "input_tokens": 1, "cache_read_input_tokens": tokens - 1, "cache_creation_input_tokens": 0}}, **extra})


class Contexto(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        self.ruta = Path(self.dir.name) / "t.jsonl"
        self.sesion = uuid.uuid4().hex
        self.addCleanup(lambda: Path(tempfile.gettempdir(), f"shipyard-contexto-{self.sesion}").unlink(missing_ok=True))

    def llamar(self, orden="aviso", env=None, entrada=None, **datos):
        base = {"session_id": self.sesion, "transcript_path": str(self.ruta), "cwd": "/x/mi-proyecto", **datos}
        r = subprocess.run([sys.executable, str(HOOK), orden], input=entrada if entrada is not None else json.dumps(base),
                           capture_output=True, text=True, env={**os.environ, **(env or {})})
        self.assertEqual(r.returncode, 0)
        return r.stdout

    def escribir(self, *lineas):
        self.ruta.write_text("\n".join(lineas) + "\n")

    def test_por_debajo_no_dice_nada(self):
        self.escribir(turno(149_999))
        self.assertEqual(self.llamar(), "")

    def test_por_encima_pide_guardar(self):
        self.escribir(turno(10), turno(150_000))
        r = json.loads(self.llamar())
        self.assertEqual(r["decision"], "block")
        self.assertIn("Retomar mi-proyecto", r["reason"])
        self.assertIn("/clear", r["reason"])

    def test_no_repite_hasta_crecer_mucho(self):
        self.escribir(turno(150_000))
        self.assertTrue(self.llamar())
        self.escribir(turno(200_000))
        self.assertEqual(self.llamar(), "")
        self.escribir(turno(250_000))
        self.assertTrue(self.llamar())

    def test_tras_compactar_vuelve_a_avisar(self):
        self.escribir(turno(150_000))
        self.assertTrue(self.llamar())
        self.escribir(turno(20_000))
        self.assertEqual(self.llamar(), "")
        self.escribir(turno(150_000))
        self.assertTrue(self.llamar())

    def test_no_crea_un_bucle(self):
        self.escribir(turno(500_000))
        self.assertEqual(self.llamar(stop_hook_active=True), "")

    def test_ignora_subagentes_y_lineas_rotas(self):
        self.escribir(turno(10), turno(500_000, isSidechain=True), "{roto")
        self.assertEqual(self.llamar(), "")

    def test_umbral_configurable_y_desactivable(self):
        self.escribir(turno(1_000))
        self.assertEqual(self.llamar(env={"SHIPYARD_AVISO_TOKENS": "0"}), "")
        self.assertTrue(self.llamar(env={"SHIPYARD_AVISO_TOKENS": "500"}))

    def test_fallos_en_silencio(self):
        self.assertEqual(self.llamar(entrada="no es json"), "")
        self.assertEqual(self.llamar(transcript_path="/no/existe"), "")

    def test_inicio_limpia_el_titulo(self):
        self.assertIn("«Retomar web v2»", self.llamar("inicio", cwd="/x/web (v2)"))


if __name__ == "__main__":
    unittest.main()
