# Modo entender

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
