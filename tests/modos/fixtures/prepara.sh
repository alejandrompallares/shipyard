#!/usr/bin/env bash
# Crea una copia de trabajo de pedidos-api con historial de git.
#   prepara.sh <variante> <destino>
# Variantes:
#   base    repo limpio con 3 commits de los últimos días
#   env     base + un .env versionado (con valores falsos)
#   sucio   base + cambios sin commitear y un archivo sin seguimiento
#   diseno  base + mock.png de 390x300 (generado con genera-mock.py)
set -euo pipefail

VARIANTE="${1:?Uso: prepara.sh <base|env|sucio|diseno> <destino>}"
DEST="${2:?Uso: prepara.sh <variante> <destino>}"
AQUI="$(cd "$(dirname "$0")" && pwd)"

mkdir -p "$DEST"
cp -R "$AQUI/pedidos-api/." "$DEST/"
cd "$DEST"

export GIT_AUTHOR_NAME="Ana Prueba" GIT_AUTHOR_EMAIL="ana@example.com"
export GIT_COMMITTER_NAME="Ana Prueba" GIT_COMMITTER_EMAIL="ana@example.com"
hace() { date -u -d "-$1 days" +%Y-%m-%dT10:00:00Z 2>/dev/null || date -u -v-"$1"d +%Y-%m-%dT10:00:00Z; }
commit() { # commit <días atrás> <mensaje>
  GIT_AUTHOR_DATE="$(hace "$1")" GIT_COMMITTER_DATE="$(hace "$1")" git commit -q -m "$2"
}

git init -q -b main
git add package.json README.md .gitignore src/server.js src/app.js src/store.js
commit 6 "Initial orders API with in-memory store"
git add src/routes/orders.js
commit 3 "Add orders routes with status changes"
git add test/
commit 1 "Add store tests"

case "$VARIANTE" in
  base) ;;
  env)
    cat > .env <<'ENV'
PORT=3000
DB_PASSWORD=contrasena-falsa-de-prueba
PAYMENTS_SECRET=sk_test_FALSO_solo_para_pruebas
ENV
    git add .env
    commit 0 "Add env config"
    ;;
  sucio)
    cat >> src/routes/orders.js <<'JS'

// WIP: cancel endpoint
router.delete('/:id', (req, res) => {
  const order = store.setStatus(req.params.id, 'cancelled');
  if (!order) return res.status(404).json({ error: 'not found' });
  res.json(order);
});
JS
    printf 'Pendiente: paginar GET /orders y validar qty > 0.\n' > NOTAS.md
    ;;
  diseno)
    python3 "$AQUI/genera-mock.py" mock.png
    git add mock.png
    commit 0 "Add orders list mock"
    ;;
  *) echo "Variante desconocida: $VARIANTE" >&2; exit 2 ;;
esac
