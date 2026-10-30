# Conectar Jylos con Claude

Jylos expone la bóveda por MCP con su plugin **MCP Server**, en `http://127.0.0.1:8843/mcp`. Solo funciona en local, y Jylos tiene que estar abierto.

## 1. Activar el plugin en Jylos

- Instala y abre Jylos (https://jylos.es, repo https://github.com/RGiskard7/jylos).
- Activa el plugin **MCP Server**. Si tu instalación no trae los plugins, compílalos:
  - `./scripts/build-plugins.sh` con Java 21 y Maven;
  - copia los `.jar` a la carpeta de plugins de Jylos (en Linux, `~/.config/Jylos/plugins/`);
  - con Java 26 falla; usa Java 21.

## 2. Claude Code (terminal)

```
claude mcp add --scope user --transport http jylos http://127.0.0.1:8843/mcp
```

Para comprobarlo: `claude mcp list` debe mostrar `jylos` como conectado.

## 3. App de escritorio de Claude

En la configuración de la app (`claude_desktop_config.json`), añade un servidor que use el puente `mcp-remote`:

```json
{
  "mcpServers": {
    "jylos": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "http://127.0.0.1:8843/mcp", "--allow-http"]
    }
  }
}
```

Si `npx` no se encuentra, usa la ruta completa a `npx` y añade `PATH` en `env`. Reinicia la app.

## Limitaciones

- Jylos tiene que estar abierto para que Claude lo vea.
- Si editas archivos de la bóveda desde fuera de Jylos, refresca Jylos.
