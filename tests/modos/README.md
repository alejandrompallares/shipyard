# Pruebas de modos de shipwright

Comprueban que, tras un cambio en las skills, Claude sigue eligiendo bien el modo, lee su archivo `references/…` antes de actuar y no intenta escribir sin permiso. Usan `claude -p` de verdad, así que **gastan tokens** (unos 3 $ la batería completa con el modelo por defecto; céntimos con `--modelo haiku`).

```bash
tests/modos/run.sh                          # los 10 casos contra el plugin del repo
tests/modos/run.sh entender cierre          # solo algunos
tests/modos/run.sh -j 5 --modelo sonnet     # 5 a la vez, con otro modelo
tests/modos/run.sh --comparar v1.1.0        # A/B: esa ref de git contra lo actual
python3 tests/modos/analiza.py tests/modos/resultados/<fecha>/actual   # volver a analizar
```

Necesita Claude Code (`claude`), git y Python 3. Los resultados (los `.jsonl` de cada caso y `resumen.md`) quedan en `tests/modos/resultados/`, que no se versiona.

## Qué hace

- **Fixtures** (`fixtures/`): una API Express de pedidos pequeña. `prepara.sh` la copia a una carpeta temporal con tres commits de los últimos días y aplica una variante: `base`, `env` (un `.env` versionado con valores falsos), `sucio` (cambios sin commitear) o `diseno` (un `mock.png` de 390x300 que dibuja `genera-mock.py`).
- **Perfil**: cada caso tiene un `CLAUDE.md` de prueba con el bloque `shipwright:perfil` (persona ficticia, sin Jylos salvo en el caso logbook), para que la skill no se pare en las preguntas de la primera vez.
- **Casos** (`casos.json`): nuevo, entender, mejorar, diseño, variantes, cierre, semana, atajos, cambio de modo (entender y, en la misma sesión con `--resume`, cierre) y logbook «guarda esto» sin Jylos.
- **Ejecución** (`run.sh`): `claude -p` con `--output-format stream-json --verbose`, `--plugin-dir` al plugin, `--strict-mcp-config` (ningún MCP, tampoco Jylos), `--permission-mode default` y solo herramientas de lectura permitidas (`Read`, `Glob`, `Grep`, `Skill` y comandos de solo lectura como `git log` o `ls`). Todo lo demás se deniega y queda registrado.
- **Análisis** (`analiza.py`): por caso, si cargó la skill, si leyó el archivo del modo, si lo leyó antes de tocar el proyecto, cuántas escrituras intentó, cuántas llamadas se denegaron y el coste.

## Cómo leer el resultado

- ✅ correcto · ⚠️ leyó el archivo del modo, pero después de empezar a mirar el proyecto · ❌ fallo.
- Es **fallo** no leer el archivo del modo, intentar escribir (Write, Edit, `git commit`, `mkdir`, `npm install`…), no cargar la skill o que `claude` no termine.
- Solo cuenta una lectura que devolvió contenido; leer un `CLAUDE.md` (el perfil) no cuenta como actuar.
- En el caso logbook no hay archivo de modo: se comprueba que no escriba y se informa si leyó `references/conectar-jylos.md`.
- El resultado de un modelo cambia entre ejecuciones: ante un fallo suelto, repite el caso antes de sacar conclusiones.

## Límites

- Si tienes un perfil real en `~/.claude/CLAUDE.md` o skills personales con el mismo nombre, también se cargan y pueden influir.
- Las rutas de la carpeta temporal aparecen en los `.jsonl`; no subas los resultados al repo.
