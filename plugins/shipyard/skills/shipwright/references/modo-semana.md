# Modo semana

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
