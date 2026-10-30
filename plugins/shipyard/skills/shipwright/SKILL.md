---
name: shipwright
description: Úsala para cualquier trabajo sobre proyectos de código. Sirve para empezar uno nuevo, entender o retomar uno que no conozco, mejorar uno existente, construir una interfaz a partir de una imagen o mock, probar varias versiones de un diseño, cerrar una sesión, resumir lo hecho en la semana o pedir atajos de Claude Code. Monta o audita git, CLAUDE.md, comprobaciones, permisos, automatizaciones y la nota en Jylos. Modos nuevo, entender, mejorar, diseño, variantes, cierre, semana y atajos.
---

# Shipwright

Aplica a los proyectos de cada persona del equipo lo que recomienda Boris Cherny, creador de Claude Code:
- preguntar al código antes de tocarlo;
- planificar antes de construir;
- dar a Claude una forma de comprobar su trabajo;
- contexto corto y compartido en CLAUDE.md;
- git desde el principio;
- trabajo en paralelo con worktrees;
- nada de producción sin permiso.

Elige el modo por lo que pida el usuario. Si no está claro, pregunta con una línea:

- **nuevo**: empezar un proyecto desde cero.
- **entender**: conocer a fondo un código que no conozco o que hace tiempo que no toco, solo con preguntas y sin editar nada.
- **mejorar**: auditar y poner al día un proyecto que ya existe (la carpeta actual u otra que diga).
- **diseño**: construir una pantalla o una web a partir de una imagen, captura o mock, iterando con capturas hasta que se parezca.
- **variantes**: probar varias versiones de un diseño o enfoque a la vez.
- **cierre**: terminar una sesión dejando el proyecto y la memoria mejor que antes.
- **semana**: resumen de lo hecho en un periodo, cruzando git y Jylos.
- **atajos**: enseñar los atajos y trucos de Claude Code (`references/atajos.md`).

Habla en español; código, commits y comentarios de código en inglés salvo que el proyecto diga otra cosa. Respuestas cortas, sin hacer la pelota y sin inventar datos (ni clientes, logos, métricas o precios en webs).

## Primera vez: perfil de la persona

Los datos de cada persona viven en su `~/.claude/CLAUDE.md`, entre `<!-- shipwright:perfil -->` y `<!-- /shipwright:perfil -->`. Claude Code carga ese archivo siempre, así que el perfil está disponible en cualquier proyecto.

Si el bloque no existe, antes del primer modo pregunta en un solo mensaje:

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

1. Añade al final de `~/.claude/CLAUDE.md` (créalo si no existe, sin borrar nada) el perfil entre esas dos marcas.
2. Añade debajo el bloque de `references/reglas-globales.md`, si no está ya (marca `<!-- shipwright -->`).
3. Si `claude mcp list` no muestra `playwright`, propón `claude mcp add --scope user playwright -- npx -y @playwright/mcp@latest` y `npx playwright install chromium`.

Si la persona cambia algo («ahora uso GitHub»), actualiza el perfil.

## Reglas comunes

- **Jylos, solo si el perfil dice que lo usa.** Sigue las convenciones de la skill `logbook`:
  - carpetas `10 Proyectos`, `20 Intereses`, `30 Conocimiento` y `40 Sesiones`;
  - títulos sin paréntesis, comas ni dos puntos;
  - campo `autor::` en cada nota.
  Si no lo usa, sáltate todos los pasos de Jylos.
- **Qué va en cada sitio.** Lo operativo de un repo va en su CLAUDE.md. En Jylos va el porqué, las decisiones, el estado, lo pendiente y el registro.
- **Repos nuevos, privados.** Si no hay forma de crearlos automáticamente, pide a la persona que lo cree y espera.
- **Datos personales o de clientes.** Si la persona tiene IA local, propón procesarlos ahí en vez de mandarlos a la nube.

## Modo nuevo

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

## Modo entender

Es el primer consejo de Boris: antes de editar, preguntar al código. No edites nada en este modo.

1. **Visión general.** Lee el CLAUDE.md, el README, los manifiestos (package.json o equivalente), la estructura de carpetas y `git log --oneline -30`. Si usa Jylos, busca la nota del proyecto.
2. **Informe de 15-25 líneas:**
   - qué hace y para quién;
   - el stack;
   - cómo se arranca, se compila y se prueba (comprueba que los comandos funcionan);
   - el mapa de carpetas, con lo importante de cada una;
   - el flujo principal de punta a punta (por ejemplo, del clic al servidor y al dato);
   - dónde está lo delicado: secretos, despliegue, código generado, partes frágiles.
3. **Preguntas.** Ofrece responder lo que el usuario quiera. Al responder:
   - busca usos y ejemplos reales en el código, no solo coincidencias de texto;
   - si pregunta por qué algo es así, mira el historial (`git log -S`, `git log -L`, `git blame`) y cuenta cuándo y por qué entró.
4. **Cierre del modo.** Si no hay CLAUDE.md, o le falta algo de lo descubierto, propón crearlo o completarlo con lo aprendido.

## Modo mejorar

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

## Modo diseño

Boris lo hace así: pasa la imagen del diseño, le da a Claude una forma de ver el resultado y le deja iterar.

1. **Referencia.** El usuario pasa una imagen: arrastrada, pegada, una ruta o una URL de la que hacer captura. Si no la hay, pídela. Describe en 3-5 líneas lo que ves (estructura, tipografía, colores, espaciados, interacciones que se intuyen) y pregunta lo que no se deduce: tamaño de referencia, qué es fijo de marca y qué es libre.
2. **Plan.** Componentes y orden de construcción, usando el stack y la marca del proyecto si existen. Espera el OK.
3. **Primera versión.** Constrúyela.
4. **Itera hasta 3 rondas.** En cada una:
   - haz capturas con Playwright al mismo ancho que la referencia y a 390px;
   - compáralas con la imagen y anota las diferencias concretas (posiciones, tamaños, colores, textos);
   - corrígelas.
5. **Para cuando** ya no haya diferencias visibles o queden solo dudas de criterio. Esas dudas, pregúntalas.
6. **Entrega:** la captura final junto a la referencia, lo que no se parece y por qué, y comprobación de accesibilidad básica (contraste, foco, `prefers-reduced-motion`).
7. **Respeta la marca.** Si la referencia es de una web ajena, úsala como inspiración: no copies textos, logos ni recursos.

## Modo variantes

1. Propón las variantes antes de construir (3 por defecto). Para cada una, 3-4 líneas sobre qué cambia, con su referencia si la hay. Espera el OK o los ajustes.
2. Con el árbol limpio, crea un worktree por variante: `git worktree add ../<repo>-v<n> -b variante/<n>-<nombre-corto>`.
3. Construye cada variante en su carpeta. Si el usuario quiere trabajar en paralelo, dile cómo abrir un Claude Code en cada carpeta (por ejemplo, en pestañas de Warp).
4. Comprueba cada variante: build y capturas a 1440 y 390. Si el proyecto usa Vercel, saca una vista previa por variante.
5. Entrega una tabla con variante, qué tiene de bueno, qué falla, enlace y captura.
6. Cuando elija, fusiona la rama ganadora en main. Con su OK, borra los demás worktrees y sus ramas. Si algo descartado merece la pena y usa Jylos, apúntalo.

## Modo cierre

1. Revisa `git status` y propón commits agrupados con sentido. Hazlos con el OK.
2. Busca en la sesión lo que debería haber estado en el CLAUDE.md desde el principio: comandos, trampas, decisiones, correcciones del usuario. Propón añadirlo como diff corto, al CLAUDE.md del proyecto o, si vale para todo, a `~/.claude/CLAUDE.md`. Si pasa de ~150 líneas, propón qué quitar.
3. Si usa Jylos, actualízalo:
   - el registro y lo pendiente de la nota del proyecto;
   - si hubo decisiones o resultados importantes, una nota en `40 Sesiones` titulada `AAAA-MM-DD Tema`;
   - si salió algo reutilizable, su nota y su línea en el área del catálogo que toque.
4. Resume en 3 líneas: qué queda hecho, qué queda pendiente y por dónde seguir la próxima vez.

## Modo semana

Es el truco de Boris de cada lunes («¿qué entregué esta semana?»), cruzado con Jylos si se usa.

1. **Periodo.** El que diga el usuario; por defecto, los últimos 7 días.
2. **Git.** Recorre los repos de la carpeta de proyectos del perfil que tengan `.git`. En cada uno: `git log --since=<inicio> --author=<email del perfil> --oneline --stat`. Traduce los commits a lo que significan para alguien que no programa.
3. **Jylos** (si lo usa). Las notas de `40 Sesiones` del periodo y las líneas de `## Registro` con esas fechas en `10 Proyectos`.
4. **Resumen:**
   - **Hecho:** por proyecto, 2-4 viñetas.
   - **Decidido:** cada decisión con su porqué, en una línea.
   - **Pendiente:** lo más urgente primero.
5. **Sin inventar.** Nada que no salga en git o en Jylos. Los proyectos sin actividad no se mencionan.
6. **Guardar.** Si usa Jylos, ofrece guardarlo como `AAAA-MM-DD Resumen semanal`.

## Modo atajos

Muestra `references/atajos.md`. Si el usuario está con algo concreto, señala primero los 2-3 atajos que más le ayudarían en eso.

## Siempre

- Antes de un cambio grande (rediseño, sección nueva, refactor, más de ~200 líneas), haz un plan corto y espera el OK.
- No digas que algo está hecho sin haberlo comprobado.
- Nunca despliegues ni ejecutes `ssh`, `rsync`, `scp` o `docker` contra un servidor sin el OK explícito en la sesión.
- Nunca subas a git ni muestres `.env`, claves o certificados.
