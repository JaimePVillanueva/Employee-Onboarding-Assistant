# Resultados del benchmark

- Temperatura: 0.2
- Modelos: gemini-flash-latest, gemini-flash-lite-latest

## Medias por modelo

| Modelo | Casos OK | Latencia media (ms) | Tokens medios |
|--------|:--------:|:-------------------:|:-------------:|
| gemini-flash-latest | 6 | 3848 | 754 |
| gemini-flash-lite-latest | 10 | 868 | 243 |

## Detalle por caso

| Caso | Modelo | Latencia (ms) | Tokens |
|------|--------|:-------------:|:------:|
| bench_01_engineering | gemini-flash-latest | 4598 | 876 |
| bench_01_engineering | gemini-flash-lite-latest | 842 | 273 |
| bench_02_engineering | gemini-flash-latest | 3731 | 736 |
| bench_02_engineering | gemini-flash-lite-latest | 702 | 227 |
| bench_03_sales | gemini-flash-latest | 2807 | 545 |
| bench_03_sales | gemini-flash-lite-latest | 670 | 156 |
| bench_04_sales | gemini-flash-latest | 3332 | 641 |
| bench_04_sales | gemini-flash-lite-latest | 779 | 190 |
| bench_05_operations | gemini-flash-latest | 3342 | 681 |
| bench_05_operations | gemini-flash-lite-latest | 703 | 189 |
| bench_06_remoto | gemini-flash-latest | 5276 | 1046 |
| bench_06_remoto | gemini-flash-lite-latest | 1164 | 340 |
| bench_07_ambiguo | gemini-flash-latest | ERROR | - |
| bench_07_ambiguo | gemini-flash-lite-latest | 1447 | 424 |
| bench_08_limite_salario | gemini-flash-latest | ERROR | - |
| bench_08_limite_salario | gemini-flash-lite-latest | 749 | 190 |
| bench_09_limite_inyeccion | gemini-flash-latest | ERROR | - |
| bench_09_limite_inyeccion | gemini-flash-lite-latest | 806 | 226 |
| bench_10_limite_politica | gemini-flash-latest | ERROR | - |
| bench_10_limite_politica | gemini-flash-lite-latest | 823 | 212 |