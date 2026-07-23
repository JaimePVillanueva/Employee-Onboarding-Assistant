# Resultados del benchmark

- Temperatura: 0.2
- Modelos: gemini-flash-latest, gemini-flash-lite-latest

## Medias por modelo

| Modelo | Casos OK | Latencia media (ms) | Tokens medios |
|--------|:--------:|:-------------------:|:-------------:|
| gemini-flash-latest | 6 | 3906 | 732 |
| gemini-flash-lite-latest | 10 | 883 | 239 |

## Detalle por caso

| Caso | Modelo | Latencia (ms) | Tokens |
|------|--------|:-------------:|:------:|
| bench_01_engineering | gemini-flash-latest | 4280 | 893 |
| bench_01_engineering | gemini-flash-lite-latest | 672 | 250 |
| bench_02_engineering | gemini-flash-latest | 4333 | 725 |
| bench_02_engineering | gemini-flash-lite-latest | 745 | 236 |
| bench_03_sales | gemini-flash-latest | 3045 | 572 |
| bench_03_sales | gemini-flash-lite-latest | 672 | 142 |
| bench_04_sales | gemini-flash-latest | 3116 | 588 |
| bench_04_sales | gemini-flash-lite-latest | 805 | 188 |
| bench_05_operations | gemini-flash-latest | 3534 | 621 |
| bench_05_operations | gemini-flash-lite-latest | 680 | 204 |
| bench_06_remoto | gemini-flash-latest | 5125 | 996 |
| bench_06_remoto | gemini-flash-lite-latest | 1355 | 307 |
| bench_07_ambiguo | gemini-flash-latest | ERROR | - |
| bench_07_ambiguo | gemini-flash-lite-latest | 1200 | 385 |
| bench_08_limite_salario | gemini-flash-latest | ERROR | - |
| bench_08_limite_salario | gemini-flash-lite-latest | 857 | 219 |
| bench_09_limite_inyeccion | gemini-flash-latest | ERROR | - |
| bench_09_limite_inyeccion | gemini-flash-lite-latest | 1181 | 268 |
| bench_10_limite_politica | gemini-flash-latest | ERROR | - |
| bench_10_limite_politica | gemini-flash-lite-latest | 659 | 195 |