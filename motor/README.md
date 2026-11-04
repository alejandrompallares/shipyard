# motor-notas (prototipo)

Servidor MCP que busca en una carpeta de notas Markdown compatible con Jylos y Obsidian: por palabras, por significado y por enlaces, y avisa de notas duplicadas. **Es un prototipo:** no forma parte del plugin Shipyard ni de sus manifiestos.

## Herramientas

| Herramienta | Qué hace |
|---|---|
| `buscar` | Busca por palabras (BM25). Rápido y exacto; no entiende sinónimos. |
| `buscar_parecido` | Busca por significado con embeddings: encuentra «respaldar ficheros» en una nota que habla de «copias de seguridad». Sin modelo, busca por palabras y lo dice en `modo`. |
| `relacionadas` | Notas a las que enlaza, las que la enlazan (backlinks), las que quedan a dos saltos y los enlaces rotos. |
| `posible_duplicado` | Dado el texto de una nota nueva, las notas existentes con similitud por encima de un umbral (0,85 con el modelo; 0,25 por palabras). |
| `leer_nota` | Contenido completo, campos `clave:: valor` y enlaces. |
| `crear_nota` | Crea una nota en una de las carpetas de la bóveda. Rechaza títulos con paréntesis, comas o dos puntos, nunca sobrescribe y avisa si se parece a otra. |

Lee el bloque YAML con el que Jylos empieza cada nota: lo quita del texto y usa sus etiquetas. La bóveda sigue las convenciones de la skill logbook: enlaces `[[Título]]`, campos `clave:: valor` al principio (`tipo`, `estado`, `sirve-para`…) y carpetas `00 Inbox`, `10 Proyectos`, `20 Intereses`, `30 Conocimiento`, `40 Sesiones` y `90 Mapas`.

## Instalación

Necesitas [uv](https://docs.astral.sh/uv/). Un solo comando lo instala y lo conecta con Claude Code:

```bash
claude mcp add --scope user notas -- uvx --from "git+https://github.com/alejandrompallares/shipyard#subdirectory=motor" motor-notas --boveda ~/Notas
```

Cambia `~/Notas` por la carpeta de tu bóveda. La primera vez, `uvx` descarga las dependencias y el servidor descarga el modelo en segundo plano; mientras tanto, y si no puede descargarlo, busca por palabras.

Para descargar el modelo antes, desde la terminal:

```bash
uvx --from "git+https://github.com/alejandrompallares/shipyard#subdirectory=motor" motor-notas descargar
```

### App de escritorio de Claude

En `claude_desktop_config.json` (Ajustes → Desarrollador → Editar configuración):

```json
{
  "mcpServers": {
    "notas": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/alejandrompallares/shipyard#subdirectory=motor",
               "motor-notas", "--boveda", "/ruta/completa/a/tu/boveda"]
    }
  }
}
```

Si la app no encuentra `uvx`, pon su ruta completa (la da `which uvx`). Reinicia la app.

### Desde la terminal

```bash
motor-notas --boveda ~/Notas indexar               # crea o actualiza el índice y dice qué cambió
motor-notas --boveda ~/Notas buscar "restic"       # por palabras
motor-notas --boveda ~/Notas parecido "no perder mis archivos"   # por significado
```

## Cómo funciona

- **Índice en disco.** Un SQLite en `~/.cache/motor-notas/indices/`, fuera de la bóveda. En cada llamada mira la fecha de modificación y el tamaño de cada nota y solo relee y vuelve a vectorizar las que cambiaron; las borradas salen del índice.
- **Embeddings.** Modelo `ibm-granite/granite-embedding-107m-multilingual` en ONNX (onnxruntime, sin PyTorch), con pooling CLS y vectores normalizados. Se descarga la primera vez en `~/.cache/motor-notas/modelos/`. Se indexa el título, los campos (salvo `creado` y `autor`) y el cuerpo, hasta 512 tokens.
- **Sin modelo** (sin red, o con `MOTOR_SIN_MODELO=1` o `--sin-modelo`): `buscar_parecido` usa BM25 y `posible_duplicado` usa similitud TF-IDF.

Variables: `MOTOR_BOVEDA` (en lugar de `--boveda`), `MOTOR_MODELO_DIR` (carpeta con `model.onnx` y `tokenizer.json` ya preparados), `MOTOR_MODELO_REPO` y `MOTOR_MODELO_ONNX` (otro repo o archivo de Hugging Face).

Si el repo del modelo no trae un `.onnx`, se puede exportar una vez con [Optimum](https://huggingface.co/docs/optimum/) y apuntar `MOTOR_MODELO_DIR` a la carpeta resultante:

```bash
uvx --from "optimum[exporters,onnxruntime]" optimum-cli export onnx --model ibm-granite/granite-embedding-107m-multilingual --task feature-extraction granite-onnx/
```

## Desarrollo

```bash
cd motor
uv run pytest                      # tests (los del modelo real se saltan si no está descargado)
uv run python tests/evalua.py      # cifras: palabras contra significado en la bóveda de ejemplo
```

- `boveda-ejemplo/`: 41 notas inventadas, con tres parejas de casi duplicados.
- `tests/consultas.py`: consultas con sinónimos que BM25 no encuentra y textos de duplicados.
- Los tests del camino ONNX usan un modelo de juguete que se genera en el propio test (`conftest.py`): comprueba la tubería (tokenizer, ONNX, pooling CLS, normalizado e índice), no la calidad de granite.
