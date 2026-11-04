# Modo mejorar

Para proyectos que ya existen. Primero diagnostica sin tocar nada.

1. **Entiende el proyecto.** Lee el CLAUDE.md, el README, el package.json o equivalente, la estructura y `git log -20` si hay git. Si usa Jylos, busca su nota.
2. **Respeta lo decidido.** Si el CLAUDE.md o Jylos recogen una decisión que choca con una recomendación (por ejemplo, "no git"), no la cambies: menciónala y pregunta.
3. **Repasa esta lista** y marca cada punto ✅, ⚠️ o ❌, con una línea de motivo:
   - **Git:** tiene repo, tiene remoto, el árbol está limpio, `.gitignore` cubre secretos y artefactos. Ningún secreto está versionado: `git ls-files | grep -E '\.env$|\.key$|\.pem$'` y una búsqueda de `PRIVATE KEY` o `SECRET` en los archivos versionados.
   - **CLAUDE.md:** existe, es corto (menos de ~150 líneas), tiene comandos que funcionan, dice qué no tocar y cómo comprobar, y no está desactualizado respecto al código.
   - **Comprobación:** build, lint y tests existen y pasan. Si es web: Playwright disponible, capturas a 1440 y 390 sin scroll horizontal, enlaces sin romper y Lighthouse con `scripts/check-site.sh <url>` (si el proyecto no lo tiene, usa el de esta skill y propón copiarlo).
   - **Despliegue:** si va a producción, hay un camino documentado y repetible (script o comando con `--dry-run` y forma de volver atrás). Si son muchos pasos manuales, propón el script.
   - **Permisos:** existe `.claude/settings.json` con lo de `references/permisos.json`.
   - **Jylos** (si lo usa): la nota del proyecto existe y está al día (estado, pendiente, registro).
   - **Específico del stack:** dependencias muy desfasadas o con vulnerabilidades conocidas (`npm audit`, `pnpm audit`), y en webs rendimiento, accesibilidad y textos legales y cookies si recoge datos.
   - **Tareas que se repiten:** mira el historial, el README y la nota de Jylos para ver qué pasos se hacen una y otra vez (publicar, actualizar datos, preparar una versión, revisar algo). Para cada uno, propón un comando propio del proyecto en `.claude/commands/<nombre>.md`, que se lanza con `/<nombre>`.
   - **Automatizaciones con `claude -p`:** propón dónde ahorraría trabajo usar Claude como herramienta de terminal, sin conversación:
     - revisar logs (`<comando de logs> | claude -p "resume errores y causas"`);
     - comprobar la web tras cada despliegue;
     - revisar cambios antes de un commit;
     - informes periódicos con cron o en la CI del repo (GitHub Actions, Gitea Actions…).
     Si los datos son personales o de clientes y el perfil tiene IA local, propón hacerlo ahí (por ejemplo `| ollama run <modelo> "…"`) en vez de `claude -p`.
4. **Informe.** Tabla corta ordenada por impacto, con qué propones en cada punto y cuánto cuesta (rápido, medio o largo).
5. **Aplica.** Con el OK, aplica los puntos aceptados uno a uno, con un commit pequeño por punto y comprobando cada uno. Si el proyecto no tiene git y el usuario acepta ponerlo, el primer commit guarda el estado actual tal cual, antes de cambiar nada.
6. **Registra.** Si usa Jylos, añade al acabar una línea al registro de la nota del proyecto y actualiza lo pendiente.
