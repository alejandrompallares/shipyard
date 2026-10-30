#!/usr/bin/env bash
# Comprueba una web: enlaces rotos y notas de Lighthouse.
#   check-site.sh https://example.com
#   check-site.sh http://localhost:3000
# Necesita Node y Chrome/Chromium (Lighthouse lo usa en modo headless).
set -uo pipefail

URL="${1:?Uso: check-site <url>}"
OUT="${TMPDIR:-/tmp}/check-site-$(date +%s)"
mkdir -p "$OUT"
fail=0

echo "== Enlaces rotos en $URL"
if npx --yes linkinator@6 "$URL" --recurse --skip '^(?!'"$URL"')' --timeout 15000 --format CSV > "$OUT/links.csv" 2>/dev/null; then
  echo "   Sin enlaces rotos."
else
  echo "   Enlaces con problemas:"
  awk -F, 'NR>1 && $2!="200" && $3=="BROKEN" {print "   - " $1 " (" $2 ") desde " $4}' "$OUT/links.csv"
  fail=1
fi

for preset in mobile desktop; do
  echo "== Lighthouse ($preset)"
  flags=(--quiet --output=json --output-path="$OUT/lh-$preset.json"
         --only-categories=performance,accessibility,best-practices,seo
         --chrome-flags="--headless=new --no-sandbox")
  [ "$preset" = desktop ] && flags+=(--preset=desktop)
  if npx --yes lighthouse@12 "$URL" "${flags[@]}" >/dev/null 2>&1; then
    node -e '
      const r = require(process.argv[1]);
      const c = r.categories, a = r.audits;
      const s = k => Math.round((c[k]?.score ?? 0) * 100);
      console.log(`   Rendimiento ${s("performance")} · Accesibilidad ${s("accessibility")} · Buenas prácticas ${s("best-practices")} · SEO ${s("seo")}`);
      console.log(`   LCP ${a["largest-contentful-paint"].displayValue} · TBT ${a["total-blocking-time"].displayValue} · CLS ${a["cumulative-layout-shift"].displayValue}`);
    ' "$OUT/lh-$preset.json"
  else
    echo "   Lighthouse no pudo ejecutarse (¿falta Chrome/Chromium?)."
    fail=1
  fi
done

echo "Informes completos en $OUT"
exit $fail
