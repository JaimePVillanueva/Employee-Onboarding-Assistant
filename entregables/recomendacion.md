# Recomendación de modelo

## Modelo recomendado: `gemini-flash-lite-latest`

Tras comparar los dos modelos con datos reales (10 casos, temperatura 0.2, mismo proveedor), recomendamos **`gemini-flash-lite-latest`** como modelo principal del Employee Onboarding Assistant.

## Justificación

**1. Velocidad.** Con una latencia media de 822 ms frente a los 3906 ms del modelo estándar, el flash-lite es **4.8 veces más rápido**. En un asistente conversacional, la rapidez de respuesta es clave para la experiencia del empleado nuevo.

**2. Coste.** El flash-lite consume de media 221 tokens por consulta frente a los 732 del estándar: **3.3 veces menos**. A escala, el ahorro es muy significativo.

**3. Calidad suficiente.** Las preguntas de onboarding son concretas y están respaldadas por la documentación interna que se le pasa en el prompt. No requieren la máxima capacidad de razonamiento, por lo que la calidad del flash-lite es adecuada para el caso de uso.

**4. Cobertura del benchmark.** El flash-lite completó los 10 casos sin incidencias. El flash-latest solo completó 6, al agotarse la cuota del plan gratuito: un modelo que consume más tokens también agota antes los límites disponibles.

## ¿Qué pasaría si duplicáramos el tráfico?

El consumo de tokens escala de forma directa con el volumen (tokens × volumen). Partiendo de las medias medidas:

- Con **flash-latest**: 732 tokens/consulta. Al duplicar el tráfico, el consumo por cada par de consultas pasa a ~1464 tokens, y la latencia acumulada crece en la misma proporción.
- Con **flash-lite-latest**: 221 tokens/consulta → ~442 tokens al duplicar. El sistema absorbe mucho mejor el aumento.

En términos absolutos, la diferencia entre ambos modelos crece con el volumen: cada 1000 consultas adicionales suponen unos **511.000 tokens más** con el modelo estándar que con el ligero.

Esto refuerza la elección: el flash-lite **escala mejor**. Además, durante el propio benchmark ya vimos el efecto práctico de este consumo: el modelo estándar agotó la cuota disponible antes de completar todos los casos, mientras que el ligero los completó todos.

## Reserva

Para consultas excepcionalmente complejas o ambiguas se podría escalar puntualmente al modelo estándar, manteniendo el flash-lite como opción por defecto. Esto daría velocidad y coste bajo en la mayoría de casos, y capacidad extra cuando realmente se necesite.
