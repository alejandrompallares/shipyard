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

- **nuevo** → `references/modo-nuevo.md`: empezar un proyecto desde cero.
- **entender** → `references/modo-entender.md`: conocer a fondo un código que no conozco o que hace tiempo que no toco, solo con preguntas y sin editar nada.
- **mejorar** → `references/modo-mejorar.md`: auditar y poner al día un proyecto que ya existe (la carpeta actual u otra que diga).
- **diseño** → `references/modo-diseno.md`: construir una pantalla o una web a partir de una imagen, captura o mock, iterando con capturas hasta que se parezca.
- **variantes** → `references/modo-variantes.md`: probar varias versiones de un diseño o enfoque a la vez.
- **cierre** → `references/modo-cierre.md`: terminar una sesión dejando el proyecto y la memoria mejor que antes.
- **semana** → `references/modo-semana.md`: resumen de lo hecho en un periodo, cruzando git y Jylos.
- **atajos** → `references/atajos.md`: enseñar los atajos y trucos de Claude Code. Si el usuario está con algo concreto, señala primero los 2-3 atajos que más le ayudarían en eso.

**Cada modo tiene sus pasos en su archivo:**
- Elegido el modo, lee su archivo ANTES del primer paso y síguelo. No lo hagas de memoria.
- Si en la misma sesión pasas a otro modo, lee también el archivo del nuevo, aunque ya hayas leído otro.
- Las rutas (`references/…`, `scripts/…`) son relativas a la carpeta de esta skill.
- Si no puedes leer el archivo, dilo y no improvises el modo.

Habla en español; código, commits y comentarios de código en inglés salvo que el proyecto diga otra cosa. Respuestas cortas, sin hacer la pelota y sin inventar datos (ni clientes, logos, métricas o precios en webs).

## Perfil de la persona

Los datos de cada persona viven en su `~/.claude/CLAUDE.md`, entre `<!-- shipwright:perfil -->` y `<!-- /shipwright:perfil -->`. Claude Code carga ese archivo siempre, así que el perfil está disponible en cualquier proyecto.

- Si el bloque no existe, antes del primer modo lee `references/primera-vez.md` y síguelo.
- Si la persona cambia algo («ahora uso GitHub»), actualiza el perfil.

## Reglas comunes

- **Jylos, solo si el perfil dice que lo usa.** Sigue las convenciones de la skill `logbook`:
  - carpetas `10 Proyectos`, `20 Intereses`, `30 Conocimiento` y `40 Sesiones`;
  - títulos sin paréntesis, comas ni dos puntos;
  - campo `autor::` en cada nota.
  Si no lo usa, sáltate todos los pasos de Jylos.
- **Qué va en cada sitio.** Lo operativo de un repo va en su CLAUDE.md. En Jylos va el porqué, las decisiones, el estado, lo pendiente y el registro.
- **Repos nuevos, privados.** Si no hay forma de crearlos automáticamente, pide a la persona que lo cree y espera.
- **Datos personales o de clientes.** Si la persona tiene IA local, propón procesarlos ahí en vez de mandarlos a la nube.

## Siempre

- Antes de un cambio grande (rediseño, sección nueva, refactor, más de ~200 líneas), haz un plan corto y espera el OK.
- No digas que algo está hecho sin haberlo comprobado.
- Nunca despliegues ni ejecutes `ssh`, `rsync`, `scp` o `docker` contra un servidor sin el OK explícito en la sesión.
- Nunca subas a git ni muestres `.env`, claves o certificados.
