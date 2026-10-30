# Atajos y trucos de Claude Code

Sacados de la charla de Boris Cherny. Si algún atajo no funciona, consulta la ayuda de tu versión con `/help`.

## Mientras trabaja
- **Mayús+Tab:** cambia de modo. Uno acepta los cambios de archivos sin preguntar (los comandos siguen preguntando); otro es el modo plan, que piensa sin tocar nada. Útil cuando ya va bien encaminado o está iterando tests.
- **Esc:** lo para en seco sin romper nada. Ideal si una propuesta de 20 líneas tiene una mal: paras, le dices cuál y que la rehaga.
- **Esc dos veces:** vuelve atrás en la conversación.
- **Ctrl+R:** muestra todo lo que ve Claude (la salida completa).

## Para darle contexto
- **`@archivo` o `@carpeta`:** lo mete en la conversación.
- **`!comando`:** ejecuta un comando tuyo y Claude ve el resultado en el siguiente turno. Bueno para comandos largos o cuando ya sabes lo que hay que ejecutar.
- **`#` + texto:** que lo recuerde. Se guarda en el CLAUDE.md que elijas.
- **`/memory`:** ver y editar los CLAUDE.md que se están cargando.
- **Imágenes:** arrástralas, pégalas o da la ruta. Úsalo con el modo diseño de shipwright.

## Sesiones
- **`claude --continue`:** sigue la última conversación de esta carpeta.
- **`claude --resume`:** elige cuál retomar.

## Hablarle en vez de escribir
- **Dictar los prompts por voz:** Boris lo hace casi siempre, porque los prompts dictados salen más largos y concretos. Usa el dictado de tu sistema (en macOS: Ajustes → Teclado → Dictado; en Linux hay opciones locales con whisper.cpp).

## Como herramienta de terminal
- **`claude -p "prompt"`:** responde sin conversación; con `--output-format json` sale en JSON. Se le pueden pasar datos por tubería:
  - `git diff | claude -p "revisa este cambio"`
  - `tail -n 2000 app.log | claude -p "errores y causas"`
- **Con datos personales:** mejor en local, `| ollama run <modelo> "…"`.

## Varios a la vez
- **Un Claude por carpeta:** con `git worktree`, en pestañas de Warp. El modo variantes de shipwright lo prepara.
