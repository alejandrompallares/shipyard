# Primera vez: perfil de la persona

Pregunta en un solo mensaje:

1. Nombre, y nombre y email para los commits.
2. Carpeta donde guarda los proyectos (por defecto `~/Projects`).
3. Dónde guarda el código y cómo se crean los repos:
   - **Gitea:** URL y usuario u organización. Si hay `GITEA_TOKEN`, por API (`POST /api/v1/user/repos`).
   - **GitHub:** usuario u organización, con `gh repo create --private`.
   - **GitLab:** igual, con `glab`.
   - **Ninguno:** solo git local.
4. Si usa Jylos como segundo cerebro (skill `logbook`).
5. Dónde publica normalmente: Vercel, Netlify, VPS propio, nada…
6. Si tiene IA local (Ollama u otra) para los datos personales o de clientes.

Con las respuestas:

1. Añade al final de `~/.claude/CLAUDE.md` (créalo si no existe, sin borrar nada) el perfil entre `<!-- shipwright:perfil -->` y `<!-- /shipwright:perfil -->`.
2. Añade debajo el bloque de `references/reglas-globales.md`, si no está ya (marca `<!-- shipwright -->`).
3. Si `claude mcp list` no muestra `playwright`, propón `claude mcp add --scope user playwright -- npx -y @playwright/mcp@latest` y `npx playwright install chromium`.
