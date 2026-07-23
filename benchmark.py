# ============================================
# BENCHMARK (Parte 4)
#
# Ejecuta los 10 casos en 2 modelos y genera las FilaBenchmark.
# El CSV lo genera report.py (guardar_csv).
# La tabla de resultados la genera este mismo fichero.
# ============================================

import os
import json
import time
import getpass
from pathlib import Path
from dataclasses import dataclass
from statistics import mean

from dotenv import load_dotenv
from google import genai
from google.genai import types


# ============================================
# CONFIGURACIÓN DEL BENCHMARK
# Independiente: los modelos a comparar se definen aquí,
# para poder cambiarlos sin tocar el config compartido.
# ============================================

MODELOS_BENCHMARK = [
    "gemini-flash-latest",
    "gemini-flash-lite-latest",
]

TEMPERATURA_BENCHMARK = 0.2   # misma para los dos = condiciones iguales

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"


# ============================================
# ESTRUCTURA DE DATOS
# report.py importa esta clase: los campos deben coincidir.
# ============================================

@dataclass
class FilaBenchmark:
    pregunta_id: str
    modelo: str
    elapsed_ms: int
    prompt_tokens: int | None
    output_tokens: int | None
    total_tokens: int | None
    respuesta: str
    error: str | None


# ============================================
# CLIENTE DE GEMINI
# ============================================

_client = None

def configurar_api() -> None:
    """Carga la clave de Gemini desde .env, o la pide por terminal."""
    load_dotenv()
    if not os.getenv("GEMINI_API_KEY"):
        os.environ["GEMINI_API_KEY"] = getpass.getpass("Pega tu GEMINI_API_KEY: ")


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        configurar_api()
        _client = genai.Client()
    return _client


# ============================================
# LLAMAR A UN MODELO
# ============================================

def llamar_modelo(modelo: str, prompt: str, pregunta_id: str) -> FilaBenchmark:
    """Llama a un modelo con un prompt y devuelve una FilaBenchmark."""
    cliente = _get_client()
    inicio = time.time()

    try:
        respuesta = cliente.models.generate_content(
            model=modelo,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=TEMPERATURA_BENCHMARK),
        )
        elapsed_ms = int((time.time() - inicio) * 1000)
        um = respuesta.usage_metadata

        return FilaBenchmark(
            pregunta_id=pregunta_id,
            modelo=modelo,
            elapsed_ms=elapsed_ms,
            prompt_tokens=getattr(um, "prompt_token_count", None),
            output_tokens=getattr(um, "candidates_token_count", None),
            total_tokens=getattr(um, "total_token_count", None),
            respuesta=(respuesta.text or "").strip()[:300],
            error=None,
        )

    except Exception as e:
        return FilaBenchmark(
            pregunta_id=pregunta_id,
            modelo=modelo,
            elapsed_ms=0,
            prompt_tokens=None,
            output_tokens=None,
            total_tokens=None,
            respuesta="",
            error=str(e)[:200],
        )


# ============================================
# EJECUTAR EL BENCHMARK
# ============================================

def ejecutar_benchmark() -> list[FilaBenchmark]:
    """Ejecuta los casos del dataset en todos los modelos."""
    with open(DATA_DIR / "preguntas_benchmark.json", "r", encoding="utf-8") as f:
        casos = json.load(f)

    filas: list[FilaBenchmark] = []

    print("=" * 60)
    print(f"BENCHMARK — {len(casos)} casos x {len(MODELOS_BENCHMARK)} modelos")
    print(f"Temperatura: {TEMPERATURA_BENCHMARK}")
    print("=" * 60)

    for caso in casos:
        print(f"\n--- {caso['id']} ---")
        for modelo in MODELOS_BENCHMARK:
            fila = llamar_modelo(modelo, caso["prompt"], caso["id"])
            filas.append(fila)
            if fila.error:
                print(f"  [{modelo}] ERROR: {fila.error[:60]}")
            else:
                print(f"  [{modelo}] {fila.elapsed_ms} ms | {fila.total_tokens} tokens")

    return filas


# ============================================
# TABLA DE RESULTADOS (para los entregables .md)
# ============================================

def generar_tabla(filas: list[FilaBenchmark]) -> Path:
    """Genera una tabla markdown con las medias por modelo."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    path = OUTPUT_DIR / "tabla_benchmark.md"

    lineas = [
        "# Resultados del benchmark",
        "",
        f"- Temperatura: {TEMPERATURA_BENCHMARK}",
        f"- Modelos: {', '.join(MODELOS_BENCHMARK)}",
        "",
        "## Medias por modelo",
        "",
        "| Modelo | Casos OK | Latencia media (ms) | Tokens medios |",
        "|--------|:--------:|:-------------------:|:-------------:|",
    ]

    for modelo in MODELOS_BENCHMARK:
        ok = [f for f in filas if f.modelo == modelo and not f.error]
        if ok:
            lat = mean(f.elapsed_ms for f in ok)
            toks = [f.total_tokens for f in ok if f.total_tokens]
            tok = mean(toks) if toks else 0
            lineas.append(f"| {modelo} | {len(ok)} | {lat:.0f} | {tok:.0f} |")
        else:
            lineas.append(f"| {modelo} | 0 | - | - |")

    # Detalle caso por caso
    lineas.extend([
        "", "## Detalle por caso", "",
        "| Caso | Modelo | Latencia (ms) | Tokens |",
        "|------|--------|:-------------:|:------:|",
    ])
    for f in filas:
        if f.error:
            lineas.append(f"| {f.pregunta_id} | {f.modelo} | ERROR | - |")
        else:
            lineas.append(f"| {f.pregunta_id} | {f.modelo} | {f.elapsed_ms} | {f.total_tokens} |")

    path.write_text("\n".join(lineas), encoding="utf-8")
    return path


# ============================================
# PUNTO DE ENTRADA
# El import de report va aquí dentro para evitar
# la dependencia circular (report importa FilaBenchmark de aquí).
# ============================================

def main() -> None:
    filas = ejecutar_benchmark()

    # El CSV lo genera report.py (parte de Jaime)
    from report import guardar_csv
    csv_path = guardar_csv(filas)

    # La tabla de resultados la genera este fichero
    tabla_path = generar_tabla(filas)

    # Resumen en pantalla
    print("\n" + "=" * 60)
    print("RESUMEN")
    print("=" * 60)
    for modelo in MODELOS_BENCHMARK:
        ok = [f for f in filas if f.modelo == modelo and not f.error]
        if ok:
            lat = mean(f.elapsed_ms for f in ok)
            toks = [f.total_tokens for f in ok if f.total_tokens]
            tok = mean(toks) if toks else 0
            print(f"\n{modelo}:")
            print(f"  Casos OK: {len(ok)}/{len(filas)//len(MODELOS_BENCHMARK)}")
            print(f"  Latencia media: {lat:.0f} ms")
            print(f"  Tokens medios: {tok:.0f}")
        else:
            print(f"\n{modelo}: sin datos (todos los casos dieron error)")

    print(f"\nCSV:   {csv_path}")
    print(f"Tabla: {tabla_path}")


if __name__ == "__main__":
    main()