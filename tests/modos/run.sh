#!/usr/bin/env bash
# Prueba cada modo de shipwright (y logbook sin Jylos) con `claude -p`.
#
#   tests/modos/run.sh                        todos los casos contra el plugin actual
#   tests/modos/run.sh entender cierre        solo esos casos
#   tests/modos/run.sh --comparar v1.1.0      además, contra el plugin de esa ref de git (tabla A/B)
#   tests/modos/run.sh --modelo sonnet -j 4   modelo concreto y 4 casos a la vez
#
# Cada caso corre en una copia temporal de su fixture, con solo herramientas de lectura
# permitidas: cualquier intento de escribir queda denegado y registrado.
# Los resultados quedan en tests/modos/resultados/<fecha>/ y al final se ejecuta analiza.py.
set -euo pipefail

AQUI="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$AQUI/../.." && pwd)"
REF=""; MODELO=""; JOBS=1; CASOS=()

while [ $# -gt 0 ]; do
  case "$1" in
    --comparar) REF="${2:?falta la ref}"; shift 2 ;;
    --modelo)   MODELO="${2:?falta el modelo}"; shift 2 ;;
    -j)         JOBS="${2:?falta el número}"; shift 2 ;;
    -h|--help)  sed -n '2,12p' "$0"; exit 0 ;;
    -*)         echo "Opción desconocida: $1" >&2; exit 2 ;;
    *)          CASOS+=("$1"); shift ;;
  esac
done

command -v claude >/dev/null || { echo "Necesitas Claude Code (claude) en el PATH." >&2; exit 1; }

SALIDA="$AQUI/resultados/$(date +%Y%m%d-%H%M%S)"
TMP="$(mktemp -d "${TMPDIR:-/tmp}/shipyard-modos.XXXXXX")"
trap 'rm -rf "$TMP"' EXIT

# Herramientas permitidas sin preguntar: solo lectura. El resto (Write, Edit, git commit…) se deniega.
PERMITIDAS="Read,Glob,Grep,Skill,Bash(git log:*),Bash(git status:*),Bash(git diff:*),Bash(git show:*),Bash(git blame:*),Bash(git ls-files:*),Bash(git branch:*),Bash(git rev-parse:*),Bash(git worktree list:*),Bash(ls:*),Bash(cat:*),Bash(head:*),Bash(grep:*),Bash(wc:*)"

# Lista de casos: id, fixture, cwd, jylos, número de turnos (de casos.json).
mapfile -t TODOS < <(python3 -c '
import json, sys
for c in json.load(open(sys.argv[1])):
    print(c["id"], c["fixture"] or "-", c["cwd"], int(c.get("jylos", False)), len(c["turnos"]))
' "$AQUI/casos.json")

prompt_de() { # prompt_de <caso> <turno 0..n>
  python3 -c '
import json, sys
c = next(c for c in json.load(open(sys.argv[1])) if c["id"] == sys.argv[2])
print(c["turnos"][int(sys.argv[3])]["prompt"])' "$AQUI/casos.json" "$1" "$2"
}

perfil() { # perfil <carpeta raíz> <usa jylos 0|1>
  local jylos="no"; [ "$2" = 1 ] && jylos="sí"
  cat <<PERFIL
# Perfil de pruebas
Este archivo hace las veces de ~/.claude/CLAUDE.md en una prueba automática.

<!-- shipwright:perfil -->
- Nombre: Ana Prueba. Commits: Ana Prueba <ana@example.com>.
- Carpeta de proyectos: $1
- Repositorios: ninguno, solo git local.
- Usa Jylos: $jylos.
- Publica en: nada todavía.
- IA local: no.
<!-- /shipwright:perfil -->
PERFIL
}

ejecuta_caso() { # ejecuta_caso <etiqueta> <plugin-dir> <id> <fixture> <cwd> <jylos> <turnos>
  local etq="$1" plugin="$2" id="$3" fixture="$4" cwd="$5" jylos="$6" turnos="$7"
  local raiz="$TMP/$etq/$id" dir out sesion="" t
  mkdir -p "$raiz" "$SALIDA/$etq"
  perfil "$raiz" "$jylos" > "$raiz/CLAUDE.md"
  dir="$raiz"
  if [ "$fixture" != "-" ]; then
    "$AQUI/fixtures/prepara.sh" "$fixture" "$raiz/pedidos-api" >/dev/null
    [ "$cwd" = proyecto ] && dir="$raiz/pedidos-api"
  fi
  for ((t = 1; t <= turnos; t++)); do
    out="$SALIDA/$etq/$id.t$t.jsonl"
    local args=(-p "$(prompt_de "$id" $((t - 1)))"
      --output-format stream-json --verbose
      --plugin-dir "$plugin" --strict-mcp-config
      --permission-mode default --allowedTools "$PERMITIDAS"
      --max-turns 40)
    [ -n "$MODELO" ] && args+=(--model "$MODELO")
    [ -n "$sesion" ] && args+=(--resume "$sesion")
    (cd "$dir" && timeout 900 claude "${args[@]}" > "$out" 2> "${out%.jsonl}.err") || true
    sesion="$(python3 -c '
import json, sys
for l in open(sys.argv[1]):
    try: e = json.loads(l)
    except ValueError: continue
    if e.get("session_id"): print(e["session_id"]); break' "$out")"
  done
  echo "   [$etq] $id listo"
}

ejecuta_todo() { # ejecuta_todo <etiqueta> <plugin-dir>
  echo "== $1: $2"
  local linea id
  for linea in "${TODOS[@]}"; do
    read -r id fixture cwd jylos turnos <<< "$linea"
    if [ ${#CASOS[@]} -gt 0 ] && [[ ! " ${CASOS[*]} " =~ " $id " ]]; then continue; fi
    while [ "$(jobs -rp | wc -l)" -ge "$JOBS" ]; do wait -n || true; done
    ejecuta_caso "$1" "$2" "$id" "$fixture" "$cwd" "$jylos" "$turnos" &
  done
  wait
}

mkdir -p "$SALIDA"
if [ -n "$REF" ]; then
  ANTES="$TMP/plugin-$REF"
  mkdir -p "$ANTES"
  git -C "$REPO" archive "$REF" plugins/shipyard | tar -x -C "$ANTES"
  ejecuta_todo A "$ANTES/plugins/shipyard"
  ejecuta_todo B "$REPO/plugins/shipyard"
  python3 "$AQUI/analiza.py" "$SALIDA/A" "$SALIDA/B" --etiquetas "$REF" "actual" | tee "$SALIDA/resumen.md"
else
  ejecuta_todo actual "$REPO/plugins/shipyard"
  python3 "$AQUI/analiza.py" "$SALIDA/actual" | tee "$SALIDA/resumen.md"
fi
