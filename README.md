# Shipyard

Plugin para [Claude Code](https://claude.com/claude-code) que unifica la forma de trabajar del equipo: proyectos montados con buenas prácticas desde el primer día y un segundo cerebro en [Jylos](https://jylos.es) que conserva el conocimiento entre sesiones.

Incluye dos skills:

| Skill | Función |
|---|---|
| **shipwright** | Crea, analiza y mejora proyectos de código siguiendo las recomendaciones de Boris Cherny, creador de Claude Code: git desde el inicio, `CLAUDE.md` breve, verificación automática del trabajo, trabajo en paralelo con worktrees y ningún despliegue sin autorización. |
| **logbook** | Conecta Claude con tu bóveda de Jylos. Consulta lo que ya sabes antes de responder, registra decisiones y aprendizajes sin que tengas que pedirlo y crea la estructura de la bóveda la primera vez. |

## Requisitos

> [!IMPORTANT]
> **Jylos es obligatorio.** Shipyard guarda y consulta toda la memoria en Jylos: `logbook` depende de él por completo y `shipwright` lo usa para la nota de cada proyecto. Instálalo antes que el plugin y mantenlo abierto mientras trabajas.
>
> **Instalación de Jylos: https://jylos.es** · Código fuente: https://github.com/RGiskard7/jylos

- [Claude Code](https://claude.com/claude-code)
- [Jylos](https://jylos.es) con el plugin **MCP Server** activado
- Git

## Instalación

**1. Instala Jylos** desde https://jylos.es y activa el plugin **MCP Server**, que expone la bóveda en `http://127.0.0.1:8843/mcp`.

**2. Conecta Jylos con Claude Code:**

```bash
claude mcp add --scope user --transport http jylos http://127.0.0.1:8843/mcp
claude mcp list   # jylos debe aparecer como conectado
```

**3. Añade el marketplace e instala el plugin** desde Claude Code:

```
/plugin marketplace add alejandrompallares/shipyard
/plugin install shipyard@shipyard
```

**4. Empieza a trabajar.** Abre Claude Code en cualquier proyecto y pide, por ejemplo, «mejora este proyecto». La primera vez, `shipwright` te hará seis preguntas para crear tu perfil y `logbook` te ofrecerá preparar la bóveda.

La guía [`conectar-jylos.md`](plugins/shipyard/skills/logbook/references/conectar-jylos.md) cubre la compilación de los plugins de Jylos y la conexión con la app de escritorio de Claude.

### App de escritorio de Claude

`logbook` también funciona en la app de escritorio. Sube [`logbook-skill-para-app-claude.zip`](logbook-skill-para-app-claude.zip) en **Ajustes → Capacidades → Skills** y conecta Jylos como se indica en la guía anterior.

## Actualización

```
/plugin marketplace update shipyard
```

También puedes activar la actualización automática desde `/plugin`.

## Uso

Las skills se activan solas según lo que pidas. También puedes invocarlas directamente con `/shipyard:shipwright` y `/shipyard:logbook`.

| Petición | Resultado |
|---|---|
| «Empieza un proyecto de…» | Estructura inicial completa: git, `CLAUDE.md`, permisos, Playwright si es web, repositorio remoto y nota en Jylos. |
| «Explícame este proyecto» | Informe del código y respuestas a tus preguntas, sin modificar nada. |
| «Mejora este proyecto» | Diagnóstico en una tabla. Solo se aplican los cambios que apruebes, con un commit por cambio. |
| «Hazme esto» + imagen | Construye la interfaz y la ajusta comparando capturas con la referencia. |
| «Hazme 3 versiones de…» | Una rama por versión, cada una con su captura y vista previa. Eliges una y se limpian las demás. |
| «Cerramos» | Commits pendientes, aprendizajes incorporados a `CLAUDE.md` y bóveda actualizada. |
| «¿Qué hice esta semana?» | Resumen que cruza el historial de git con Jylos. |
| «Atajos» | Referencia rápida de Claude Code. |

## Archivos que crea o modifica

**Configuración global**
- `~/.claude/CLAUDE.md`: tu perfil (nombre, identidad de git, carpeta de proyectos, servicio de repositorios…) y las reglas de trabajo comunes, delimitados por marcas `<!-- shipwright… -->`. Puedes editarlo a mano.

**En cada proyecto**
- `CLAUDE.md` con el contexto del proyecto.
- `.claude/settings.json` con permisos que piden confirmación antes de usar ssh o docker, hacer push o desplegar en producción.
- `.mcp.json` con Playwright, solo en proyectos web.
- `scripts/check-site.sh` para verificar el sitio automáticamente.

**En tu bóveda de Jylos**
- Las notas de proyectos, sesiones y recursos. Cada nota incluye el campo `autor::` para poder combinar bóvedas en un futuro espacio de equipo.

## Estructura del repositorio

```
.claude-plugin/marketplace.json     Definición del marketplace
plugins/shipyard/
├── .claude-plugin/plugin.json      Manifiesto del plugin
└── skills/
    ├── shipwright/                 Skill de proyectos
    └── logbook/                    Skill del segundo cerebro
logbook-skill-para-app-claude.zip   logbook empaquetada para la app de escritorio
```
