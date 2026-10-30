# Plantilla de CLAUDE.md de proyecto (menos de 40 líneas al crearlo)

```markdown
# <nombre>

<Qué es en una frase. Para quién. Si va a producción o es una prueba.>

## Stack and commands
<stack en una línea>
- `<dev>` → <url local>
- `<build>`, `<lint>`, `<test>`

## Structure
- `<carpeta o archivo clave>`: <para qué>
- …

## Do not touch
- <marca, textos, archivos generados, decisiones fijadas>

## How to verify
- `<build>` and `<test>` pass.
- (web) Screenshots with the Playwright MCP at 1440px and 390px, no horizontal overflow; every link points to real content; `scripts/check-site.sh <url>`.

## Deploy
<"Not deployed yet." o el comando/script, con `--dry-run` y cómo volver atrás. Never deploy without the user's OK.>

## Decisions
- <decisión>: <por qué, en una línea>
```

Reglas: comandos que funcionen de verdad (pruébalos), nada que el código ya diga por sí solo, y actualizarlo en cada `cierre`.
