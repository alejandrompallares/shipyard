---
name: logbook
description: Segundo cerebro en Jylos. Úsala en cualquier conversación con sustancia (investigar, aprender, decidir, idear, planificar o trabajar en algo) o cuando algo que la persona ya sabe pueda servir. Antes de responder, busca en su bóveda lo que ya conoce; después, guarda lo importante sin que lo pida. La primera vez monta la estructura de la bóveda.
---

# Logbook: el segundo cerebro en Jylos

Cada persona tiene una bóveda en Jylos conectada por MCP. Las herramientas se llaman `jylos` y pueden llevar un prefijo según desde dónde se conecte: `mcp__jylos__`, `mcp__remote-devices__jylos__`, `mcp__claude-device__lcl-jylos-`… La bóveda es su memoria externa: lo que sabe, lo que le ha interesado, las herramientas y recursos que ha visto, sus ideas, decisiones y proyectos.

Tu trabajo es doble:
- mantenerla al día sin que te lo pida;
- usarla para recordarle cosas que ya no recuerda, cuando le puedan servir.

Gasta el mínimo contexto posible.

Vale para cualquier tema con sustancia: aprender algo, comparar opciones, decidir, planear, idear o resolver un problema. La charla y las preguntas de un momento no se guardan.

**Si no hay herramientas `jylos`:**
- Puede que acaben de conectarse: dilo una sola vez y pide que envíe otro mensaje.
- Si siguen sin aparecer (Jylos o la app cerrados, o chat desde el móvil o la web), explica una vez cómo conectarlas (`references/conectar-jylos.md`) y sigue con la tarea.
- Si la persona pide «guardar», dale las notas en bloques Markdown listos para pegar, con sus líneas para el catálogo.

**Si pide guardar «toda la conversación»** al retomar un chat antiguo, recórrela entera, no solo lo último.

## Primera vez: montar la bóveda

Usa `list_folders`. Si faltan las carpetas de abajo o la nota `Catálogo de recursos`, ofrece montar la estructura una sola vez. Con un «sí»:

1. Crea las carpetas que falten.
2. Crea en `90 Mapas` las notas de `references/plantillas-mapas.md`: `Inicio`, `Catálogo de recursos` y `Mapa general`.
3. Pregunta el nombre de la persona para el campo `autor::`, salvo que ya esté en su `~/.claude/CLAUDE.md` (bloque `shipwright:perfil`).
4. Si ya tenía notas sueltas, no las muevas sin preguntar. Propón ordenarlas por carpetas y añadirlas al catálogo.

## Carpetas (no inventes otras)

- `00 Inbox`: lo que no sabes dónde va.
- `10 Proyectos`: una nota por proyecto o cosa que se está haciendo con un objetivo.
- `20 Intereses`: temas, herramientas, recursos e ideas.
- `30 Conocimiento`: conceptos, técnicas y aprendizajes reutilizables.
- `40 Sesiones`: una nota por sesión con decisiones o resultados, titulada `AAAA-MM-DD Tema`.
- `90 Mapas`:
  - `Inicio`;
  - `Mapa general`;
  - `Catálogo de recursos`, que es el índice;
  - las áreas del catálogo, `Catálogo - <Área>`.

## Recordar (lo barato primero)

1. **Busca primero.** Al empezar algo con sustancia, usa `search_notes` con el tema, por capacidad y con sinónimos, no solo por nombre. Lee solo las notas que salgan y sean relevantes.
2. **Catálogo, solo si hace falta.** Si la búsqueda no basta, o necesitas ver qué herramientas tiene para una necesidad:
   - lee `Catálogo de recursos`, que es un índice corto;
   - después lee SOLO el área o áreas que encajen;
   - no leas todas las áreas por si acaso.
3. **Parte de lo que ya sabe y no se lo repitas.** Si algo que vio antes encaja, propónselo así: «Ya miraste X, que sirve para Y. Podría encajar aquí porque Z». Si no encaja de verdad, no lo fuerces.

## Guardar (sin que lo pida, cuando algo quede claro)

**Antes de crear, busca.** Si ya existe nota del tema, léela con `read_note` y amplíala con `update_note` reescribiendo el contenido completo, conservando todo lo anterior. Si no existe, créala con `create_note` y muévela con `move_note`.

**Títulos sin paréntesis, comas ni dos puntos.** Jylos los cambia por `_` en el archivo y los enlaces `[[...]]` se rompen. Si una nota existente ya tiene `_` en el título, enlázala tal cual (por ejemplo `[[REA _Reverse Engineer Anything_]]`).

**Herramientas, recursos, temas e ideas** van a `20 Intereses` con este formato:

```
tipo:: interes | herramienta | recurso | idea | concepto
estado:: activo | idea | pausado | terminado
creado:: AAAA-MM-DD
autor:: <nombre>
sirve-para:: TODOS sus usos posibles, en lenguaje llano
lo-use-para:: lo que yo quería hacer con ello

Qué es y cómo funciona en lo esencial.

## Usos posibles
- Cada uso, en una o dos líneas.

## Cómo se usa
Enlaces, comandos, pasos.

## Limitaciones y preguntas abiertas

Relacionado: [[Otra nota]]
```

- **`sirve-para`** recoge TODOS los usos, también los que no se eligieron ese día. Escríbelos como alguien describiría la necesidad («clasificar textos», «simular cómo reaccionaría un público»). Si salen usos nuevos, añádelos.
- **Catálogo.** Las herramientas, recursos e ideas reutilizables se apuntan en la nota de área del catálogo que toque, en la sección `## <Capacidad>` de CADA uno de sus usos: `- [[Nombre]]: qué hace en esa capacidad, en una frase`.
  - Si la capacidad es nueva, créala en su área.
  - Si el área no existe, crea `Catálogo - <Área>`, añádela al índice `Catálogo de recursos` y escribe en el índice el nombre de sus capacidades.
- **Proyectos:** nota en `10 Proyectos` con `tipo:: proyecto`, `estado::`, `autor::`, el objetivo y `## Registro`, con una línea por avance.
  - Si el proyecto tiene repositorio de código, lo operativo (comandos, despliegue, qué no tocar) va en el `CLAUDE.md` del repo.
  - En Jylos van el porqué, las decisiones, el estado, lo pendiente y el registro, con un enlace a la ruta del repo. No dupliques.
- **Sesiones con decisiones o resultados:** nota en `40 Sesiones` con qué se habló, qué se decidió y por qué, y qué queda pendiente, enlazada a su proyecto o tema.
- **Conceptos o técnicas reutilizables:** `30 Conocimiento`.
- **Etiquetas:** en minúsculas y en español. Mira `list_tags` antes de inventar una nueva. Enlaces siempre con `[[Título exacto]]`.
- **Lo esencial, no la conversación.** Nada de datos sensibles: contraseñas, claves ni datos personales de terceros. No borres notas.

Cuando guardes algo, dilo en una sola línea al final de la respuesta.

## Si un día hay bóveda compartida de equipo

Esta skill ya deja cada nota con `autor::`, así que se podrá juntar con las de otros sin perder quién escribió qué. Cuando la persona diga que hay una bóveda compartida:

- **Qué va a cada bóveda:**
  - a la compartida, lo del equipo: proyectos comunes, conocimiento y herramientas útiles para todos, decisiones de equipo;
  - a la personal, lo suyo.
  - Si dudas, pregunta.
- **Notas de otros:** en la compartida no reescribas notas de otra persona. Añade al final una línea en `## Registro`, o una sección `## Aportación de <nombre> (AAAA-MM-DD)`.
- **Al buscar,** mira en las dos bóvedas y di de cuál sale cada cosa.
