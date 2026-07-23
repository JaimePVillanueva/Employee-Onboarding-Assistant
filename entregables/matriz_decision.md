# Matriz de decisión — Benchmark de modelos

## Contexto

Comparamos dos modelos de Gemini bajo las **mismas condiciones** (temperatura 0.2, mismos 10 casos, mismo proveedor) para elegir con datos qué modelo usar en el Employee Onboarding Assistant.

## Modelos comparados

| Modelo | Descripción |
|--------|-------------|
| `gemini-flash-latest` | Modelo flash estándar |
| `gemini-flash-lite-latest` | Modelo flash ligero, optimizado para velocidad y coste |

## Nota sobre los datos

`gemini-flash-latest` completó **6 de los 10 casos**. Los 4 restantes fallaron por **cuota agotada del plan gratuito**, no por un fallo del modelo. Para que la comparación sea justa, las medias se calculan sobre los **6 casos que ambos modelos completaron**.

## Resultados (6 casos comunes)

| Métrica | gemini-flash-latest | gemini-flash-lite-latest |
|---------|--------------------:|-------------------------:|
| Latencia media | 3906 ms | **822 ms** |
| Tokens medios | 732 | **221** |
| Velocidad relativa | 1x | **4.8x más rápido** |
| Coste relativo (tokens) | 1x | **3.3x más barato** |

## Detalle por caso (6 casos comunes)

| Caso | flash-latest (ms) | flash-lite (ms) | flash-latest (tok) | flash-lite (tok) |
|------|------------------:|----------------:|-------------------:|-----------------:|
| bench_01_engineering | 4280 | 672 | 893 | 250 |
| bench_02_engineering | 4333 | 745 | 725 | 236 |
| bench_03_sales | 3045 | 672 | 572 | 142 |
| bench_04_sales | 3116 | 805 | 588 | 188 |
| bench_05_operations | 3534 | 680 | 621 | 204 |
| bench_06_remoto | 5125 | 1355 | 996 | 307 |

## Casos límite

Los 4 casos restantes (ambiguo, salario, inyección, política inexistente) solo pudieron ejecutarse en `flash-lite-latest`:

| Caso | Latencia (ms) | Tokens |
|------|--------------:|-------:|
| bench_07_ambiguo | 1200 | 385 |
| bench_08_limite_salario | 857 | 219 |
| bench_09_limite_inyeccion | 1181 | 268 |
| bench_10_limite_politica | 659 | 195 |

## Matriz de decisión (escala 1-3)

| Criterio | flash-latest | flash-lite-latest |
|----------|:------------:|:-----------------:|
| Velocidad | 1 | **3** |
| Coste (tokens) | 1 | **3** |
| Calidad de respuesta | 3 | 3 |
| Cobertura del benchmark | 2 | **3** |
| **Total** | **7** | **12** |

## Conclusión

Para un asistente de onboarding, donde las preguntas son concretas y están respaldadas por documentación, **`gemini-flash-lite-latest` es la mejor opción**: 4.8x más rápido, 3.3x más barato, y con calidad equivalente para este caso de uso.
