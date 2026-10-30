# Notas iniciales de `90 Mapas`

## Inicio

```markdown
Portada del segundo cerebro. Se actualiza sola con Dataview (plugin de Jylos).

Índices: [[Catálogo de recursos]] · [[Mapa general]]

## Proyectos activos
```dataview
TABLE estado, creado FROM "10 Proyectos" WHERE estado = "activo" SORT file.mtime DESC
```

## Intereses recientes
```dataview
TABLE sirve-para FROM "20 Intereses" SORT file.mtime DESC LIMIT 20
```

## Últimas sesiones
```dataview
TABLE creado FROM "40 Sesiones" SORT file.name DESC LIMIT 15
```

## Por ordenar
```dataview
LIST FROM "00 Inbox"
```
```

## Catálogo de recursos

```markdown
Índice de todo lo que conozco, agrupado por para qué sirve. Claude lee este índice y después solo el área que necesite.

Cada área tiene secciones `## Capacidad` con líneas `- [[Nombre]]: qué hace en esa capacidad, en una frase`. Una herramienta aparece en todas las capacidades que cubre. Esquema por proyectos en [[Mapa general]].

**Regla de títulos:** sin paréntesis, comas ni dos puntos (Jylos los cambia por `_` y los enlaces se rompen).

<!-- Claude añade aquí una línea por área: ## [[Catálogo - <Área>]] y debajo sus capacidades separadas por · -->

## Sin clasificar
```

## Mapa general

```markdown
Esquema de todo lo que hay en la bóveda, agrupado por área o proyecto. Para buscar por "para qué sirve", ver [[Catálogo de recursos]]. Portada: [[Inicio]].

<!-- Claude añade aquí las áreas a medida que aparezcan: proyectos con sus sesiones, herramientas y conocimiento relacionados, y al final los hilos que cruzan áreas. -->
```
