# Shipyard

Plugin de Claude Code con dos skills: **shipwright** (proyectos de código: nuevo, entender, mejorar, diseño, variantes, cierre, semana, atajos) y **logbook** (segundo cerebro en Jylos). Se distribuye como marketplace de GitHub.

## Reglas
- Repo PÚBLICO: nada de datos personales, rutas de una máquina concreta, IPs ni nombres de clientes.
- Commits pequeños y en inglés, sin `Co-Authored-By` ni atribución a Claude (tampoco en los PR).
- Documentación y textos en español.
- No cambies el comportamiento de las skills (`SKILL.md` y `references/`) salvo que se pida expresamente.
- Trabaja en una rama y abre un PR; nunca toques `main` directamente.

## Estructura
- `.claude-plugin/marketplace.json`: marketplace (versión en `metadata.version` y `plugins[0].version`).
- `plugins/shipyard/.claude-plugin/plugin.json`: manifiesto del plugin (`version`).
- `plugins/shipyard/skills/shipwright/`: `SKILL.md`, un `references/modo-*.md` por modo y `scripts/check-site.sh`.
- `plugins/shipyard/skills/logbook/`: `SKILL.md` y `references/`.
- `logbook-skill-para-app-claude.zip`: logbook empaquetada para la app de escritorio (generada, no editar a mano).
- `scripts/`: herramientas del repo (`release.sh`, `check.py`).
- `tests/modos/`: pruebas de comportamiento de shipwright con `claude -p`.
- `motor/`: prototipo de servidor MCP de búsqueda; NO forma parte del plugin.

## Cómo comprobar
- `python3 scripts/check.py`: JSON válidos, versiones iguales, zip al día y rutas citadas existentes (lo mismo que la CI).
- `claude plugin validate .` si tienes Claude Code.
- Tras tocar una skill: `tests/modos/run.sh` (gasta tokens; ver `tests/modos/README.md`).

## Publicar una versión
1. Con el árbol limpio y en una rama: `scripts/release.sh X.Y.Z`.
   Cambia las tres versiones, regenera el zip, valida y hace el commit `Release X.Y.Z` (sin push).
2. Abre el PR; cuando se fusione, los usuarios actualizan con `/plugin marketplace update shipyard`.
