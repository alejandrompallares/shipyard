#!/usr/bin/env python3
"""Comprobaciones del repo (las mismas que la CI).

1. Todos los .json del repo son válidos.
2. La versión de marketplace.json coincide con la de plugin.json.
3. logbook-skill-para-app-claude.zip contiene exactamente plugins/shipyard/skills/logbook.
4. Cada ruta references/… o scripts/… citada en un SKILL.md o references/*.md existe.

Uso: python3 scripts/check.py   (sale con código 1 si algo falla)
"""
import json
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "plugins/shipyard/skills"
MARKETPLACE = ROOT / ".claude-plugin/marketplace.json"
PLUGIN = ROOT / "plugins/shipyard/.claude-plugin/plugin.json"
ZIP = ROOT / "logbook-skill-para-app-claude.zip"
LOGBOOK = SKILLS / "logbook"
SKIP_DIRS = {".git", "node_modules", ".venv", "__pycache__"}

errors = []


def fail(msg):
    errors.append(msg)
    print(f"  ✗ {msg}")


def check_json():
    print("JSON válidos")
    for path in sorted(ROOT.rglob("*.json")):
        if SKIP_DIRS & set(path.relative_to(ROOT).parts):
            continue
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            fail(f"{path.relative_to(ROOT)}: {e}")


def check_versions():
    print("Versiones")
    try:
        mk = json.loads(MARKETPLACE.read_text(encoding="utf-8"))
        pl = json.loads(PLUGIN.read_text(encoding="utf-8"))
    except Exception as e:  # ya informado en check_json
        fail(f"no se pueden leer los manifiestos: {e}")
        return
    found = {
        "plugin.json version": pl.get("version"),
        "marketplace.json metadata.version": mk.get("metadata", {}).get("version"),
    }
    for p in mk.get("plugins", []):
        if p.get("name") == pl.get("name"):
            found[f"marketplace.json plugins[{p['name']}].version"] = p.get("version")
    if len(set(found.values())) != 1 or None in found.values():
        fail("las versiones no coinciden: " + ", ".join(f"{k}={v}" for k, v in found.items()))
    else:
        print(f"  ✓ {next(iter(found.values()))}")


def check_zip():
    print("Zip de logbook")
    before = len(errors)
    if not ZIP.exists():
        fail(f"falta {ZIP.name}")
        return
    expected = {
        "logbook/" + p.relative_to(LOGBOOK).as_posix(): p.read_bytes()
        for p in LOGBOOK.rglob("*") if p.is_file()
    }
    with zipfile.ZipFile(ZIP) as z:
        actual = {i.filename: z.read(i) for i in z.infolist() if not i.is_dir()}
    for name in sorted(expected.keys() - actual.keys()):
        fail(f"falta en el zip: {name}")
    for name in sorted(actual.keys() - expected.keys()):
        fail(f"sobra en el zip: {name}")
    for name in sorted(expected.keys() & actual.keys()):
        if expected[name] != actual[name]:
            fail(f"distinto en el zip: {name} (ejecuta scripts/release.sh o regenera el zip)")
    if len(errors) == before:
        print(f"  ✓ {len(expected)} archivos iguales")


# references/x.md o scripts/x.sh, sin ir precedido de / . o letra (así se ignora ./scripts/… o .claude/…)
PATH_RE = re.compile(r"(?<![\w./-])((?:references|scripts)/[\w./-]*[\w-])")


def check_paths():
    print("Rutas citadas")
    count = 0
    for skill in sorted(p for p in SKILLS.iterdir() if p.is_dir()):
        docs = [skill / "SKILL.md", *sorted((skill / "references").glob("*.md"))]
        for doc in docs:
            if not doc.exists():
                continue
            for n, line in enumerate(doc.read_text(encoding="utf-8").splitlines(), 1):
                for m in PATH_RE.finditer(line):
                    rel = m.group(1)
                    if "<" in line[m.end():m.end() + 1]:  # plantilla tipo references/modo-<x>.md
                        continue
                    count += 1
                    if not (skill / rel).exists():
                        fail(f"{doc.relative_to(ROOT)}:{n} cita {rel}, que no existe en {skill.name}/")
    print(f"  {count} citas revisadas")


def main():
    check_json()
    check_versions()
    check_zip()
    check_paths()
    if errors:
        print(f"\n{len(errors)} problema(s).")
        sys.exit(1)
    print("\nTodo correcto.")


if __name__ == "__main__":
    main()
