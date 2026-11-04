#!/usr/bin/env bash
# Prepara una versión nueva del plugin.
#   scripts/release.sh 1.3.0
# 1. Cambia la versión en .claude-plugin/marketplace.json y plugins/shipyard/.claude-plugin/plugin.json.
# 2. Regenera logbook-skill-para-app-claude.zip desde plugins/shipyard/skills/logbook (raíz: logbook/).
# 3. Pasa scripts/check.py y, si está instalado, `claude plugin validate .`.
# 4. Hace el commit "Release X.Y.Z". No hace push.
set -euo pipefail

VERSION="${1:-}"
if [[ ! "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "Uso: scripts/release.sh X.Y.Z" >&2
  exit 2
fi

cd "$(git rev-parse --show-toplevel)"

if [ -n "$(git status --porcelain)" ]; then
  echo "El árbol de trabajo no está limpio. Haz commit o guarda los cambios antes." >&2
  exit 1
fi
if [ "$(git rev-parse --abbrev-ref HEAD)" = "main" ]; then
  echo "Estás en main. Crea una rama para la versión (git switch -c release-$VERSION)." >&2
  exit 1
fi

echo "== Versión $VERSION en los manifiestos"
python3 - "$VERSION" <<'PY'
import json, sys
v = sys.argv[1]
def edit(path, fn):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    fn(data)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
def mk(d):
    d.setdefault("metadata", {})["version"] = v
    for p in d["plugins"]:
        if p["name"] == "shipyard":
            p["version"] = v
def pl(d):
    d["version"] = v
edit(".claude-plugin/marketplace.json", mk)
edit("plugins/shipyard/.claude-plugin/plugin.json", pl)
PY

echo "== Zip de logbook"
python3 - <<'PY'
# Zip reproducible: orden fijo y fecha fija, para que solo cambie si cambia el contenido.
import zipfile
from pathlib import Path
src = Path("plugins/shipyard/skills/logbook")
out = Path("logbook-skill-para-app-claude.zip")
stamp = (2026, 1, 1, 0, 0, 0)
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    entries = [src] + sorted(p for p in src.rglob("*"))
    for p in entries:
        rel = p.relative_to(src).as_posix()
        name = "logbook" if rel == "." else "logbook/" + rel
        if p.is_dir():
            info = zipfile.ZipInfo(name + "/", stamp)
            info.external_attr = 0o40755 << 16
            z.writestr(info, b"")
        else:
            info = zipfile.ZipInfo(name, stamp)
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, p.read_bytes())
print(f"   {out} regenerado")
PY

echo "== Comprobaciones"
python3 scripts/check.py
if command -v claude >/dev/null 2>&1; then
  claude plugin validate .
else
  echo "   claude no está instalado: me salto 'claude plugin validate .'"
fi

git add .claude-plugin/marketplace.json plugins/shipyard/.claude-plugin/plugin.json logbook-skill-para-app-claude.zip
git commit -q -m "Release $VERSION"
echo "== Hecho: commit 'Release $VERSION'. Revisa con 'git show --stat' y haz push cuando quieras."
