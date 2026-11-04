# Modo diseño

Boris lo hace así: pasa la imagen del diseño, le da a Claude una forma de ver el resultado y le deja iterar.

1. **Referencia.** El usuario pasa una imagen: arrastrada, pegada, una ruta o una URL de la que hacer captura. Si no la hay, pídela. Describe en 3-5 líneas lo que ves (estructura, tipografía, colores, espaciados, interacciones que se intuyen) y pregunta lo que no se deduce: tamaño de referencia, qué es fijo de marca y qué es libre.
2. **Plan.** Componentes y orden de construcción, usando el stack y la marca del proyecto si existen. Espera el OK.
3. **Primera versión.** Constrúyela.
4. **Itera hasta 3 rondas.** En cada una:
   - haz capturas con Playwright al mismo ancho que la referencia y a 390px;
   - compáralas con la imagen y anota las diferencias concretas (posiciones, tamaños, colores, textos);
   - corrígelas.
5. **Para cuando** ya no haya diferencias visibles o queden solo dudas de criterio. Esas dudas, pregúntalas.
6. **Entrega:** la captura final junto a la referencia, lo que no se parece y por qué, y comprobación de accesibilidad básica (contraste, foco, `prefers-reduced-motion`).
7. **Respeta la marca.** Si la referencia es de una web ajena, úsala como inspiración: no copies textos, logos ni recursos.
