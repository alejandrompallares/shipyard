# Modo variantes

1. Propón las variantes antes de construir (3 por defecto). Para cada una, 3-4 líneas sobre qué cambia, con su referencia si la hay. Espera el OK o los ajustes.
2. Con el árbol limpio, crea un worktree por variante: `git worktree add ../<repo>-v<n> -b variante/<n>-<nombre-corto>`.
3. Construye cada variante en su carpeta. Si el usuario quiere trabajar en paralelo, dile cómo abrir un Claude Code en cada carpeta (por ejemplo, en pestañas de Warp).
4. Comprueba cada variante: build y capturas a 1440 y 390. Si el proyecto usa Vercel, saca una vista previa por variante.
5. Entrega una tabla con variante, qué tiene de bueno, qué falla, enlace y captura.
6. Cuando elija, fusiona la rama ganadora en main. Con su OK, borra los demás worktrees y sus ramas. Si algo descartado merece la pena y usa Jylos, apúntalo.
