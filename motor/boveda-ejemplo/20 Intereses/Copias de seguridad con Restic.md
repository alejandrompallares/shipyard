tipo:: herramienta
estado:: activo
creado:: 2026-09-20
autor:: Ana Prueba
sirve-para:: copias de seguridad cifradas, versiones antiguas de documentos, recuperar un disco
lo-use-para:: guardar el portátil y las fotos en un disco externo y en la nube

Restic hace copias de seguridad cifradas e incrementales. Guarda instantáneas y deduplica bloques, así que cada copia nueva ocupa poco.

## Cómo se usa
- `restic init` para crear el repositorio.
- `restic backup ~/Documentos` para hacer una instantánea.
- `restic snapshots` para ver las instantáneas.

Sigue la [[Regla 3-2-1 de copias]]. Decidido en [[2026-09-20 Elegir sistema de copias]].
