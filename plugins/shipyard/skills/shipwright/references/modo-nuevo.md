# Modo nuevo

1. Pregunta lo que falte en un solo mensaje:
   - nombre de la carpeta;
   - qué es, en una frase;
   - tipo (web, app, bot, script…);
   - si va a producción o es una prueba;
   - stack. Si no lo sabe, recomienda uno con una línea de por qué.
2. Si usa Jylos, busca si ya hay algo relacionado (proyecto, idea o herramienta del catálogo) y dilo en 2-3 líneas.
3. Crea la carpeta en la carpeta de proyectos del perfil, con el iniciador oficial del stack, y ejecuta `git init -b main` con el autor del perfil.
4. Monta el `.gitignore` del stack y añade `.env`, `.env.*` (salvo `.env.example`), `*.key`, `*.pem`, `.claude/settings.local.json` y `CLAUDE.local.md`.
5. Escribe un `CLAUDE.md` de menos de 40 líneas con la plantilla de `references/plantilla-claude-md.md`.
6. Crea `.claude/settings.json` con los permisos de `references/permisos.json`.
7. Si es web:
   - crea `.mcp.json` con Playwright (`{"mcpServers":{"playwright":{"command":"npx","args":["-y","@playwright/mcp@latest"]}}}`);
   - copia `scripts/check-site.sh` de esta skill a `scripts/check-site.sh` del proyecto (enlaces rotos y Lighthouse);
   - pon en el CLAUDE.md cómo se comprueba: capturas a 1440 y 390 y `scripts/check-site.sh <url>`.
8. Comprueba que arranca y compila. Haz el primer commit `Initial commit`. Crea el repo privado donde diga el perfil, añade el remoto `origin` y haz push.
9. Si usa Jylos, crea la nota del proyecto en `10 Proyectos`: `tipo:: proyecto`, `estado:: activo`, `autor::`, objetivo, ruta, repo y `## Registro` con la línea de hoy.
10. Termina con lo creado y el primer paso que propones. Antes de ese primer paso, si es grande, haz un plan corto y espera el OK.
