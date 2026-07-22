# ============================================
# BENCHMARK (Parte 4): comparar 2 modelos
# ============================================

import json
import csv
import time
from pathlib import Path

from google import genai
from google.genai import types

from config import DATA_DIR, TEMPERATURE
from asistente import configurar_api, construir_prompt
from datos import buscar_empleado, seleccionar_faqs, seleccionar_docs
from robustez import analizar_amenaza, respuesta_segura


# --- Los 2 modelos que comparamos (misma temperatura) ---
MODELOS = ["gemini-flash-latest", "gemini-flash-lite-latest"]
TEMPERATURA_BENCHMARK = 0.2   # la misma para los dos (condiciones iguales)

# --- Carpeta de salida ---
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)   # crea la carpeta si no existe


def llamar_modelo(modelo, prompt):
    """Llama a un modelo concreto y devuelve (respuesta, tiempo_ms, tokens)."""
    cliente = genai.Client()
    inicio = time.time()

    respuesta = cliente.models.generate_content(
        model=modelo,
        contents=prompt,
        config=types.GenerateContentConfig(temperature=TEMPERATURA_BENCHMARK),
    )

    tiempo_ms = int((time.time() - inicio) * 1000)
    uso = respuesta.usage_metadata
    tokens_total = getattr(uso, "total_token_count", 0)

    return (respuesta.text or "").strip(), tiempo_ms, tokens_total


def ejecutar_benchmark():
    """Ejecuta los 10 casos en los 2 modelos y guarda los resultados en CSV."""
    configurar_api()

    # Cargamos los casos de benchmark
    with open(DATA_DIR / "preguntas_benchmark.json", "r", encoding="utf-8") as f:
        casos = json.load(f)

    resultados = []

    print("=" * 70)
    print("BENCHMARK: comparando modelos")
    print("=" * 70)

    for caso in casos:
        empleado = buscar_empleado(caso["empleado"])
        pregunta = caso["pregunta"]

        print(f"\n--- {caso['id']} ({caso['tipo']}) ---")
        print(f"Pregunta: {pregunta}")

        # Comprobamos si es una amenaza (fail-closed)
        amenaza = analizar_amenaza(pregunta)

        for modelo in MODELOS:
            if amenaza:
                # No llamamos al modelo, respuesta segura
                respuesta = respuesta_segura(amenaza)
                tiempo_ms = 0
                tokens = 0
                print(f"  [{modelo}] BLOQUEADO (fail-closed): {amenaza}")
            else:
                # Construimos el prompt y llamamos al modelo
                faqs = seleccionar_faqs(pregunta)
                docs = seleccionar_docs(pregunta, faqs)
                prompt = construir_prompt(empleado, pregunta, faqs, docs)
                try:
                    respuesta, tiempo_ms, tokens = llamar_modelo(modelo, prompt)
                    print(f"  [{modelo}] {tiempo_ms} ms, {tokens} tokens")
                except Exception as e:
                    respuesta = f"ERROR: {e}"
                    tiempo_ms = 0
                    tokens = 0
                    print(f"  [{modelo}] ERROR")

            # Guardamos el resultado
            resultados.append({
                "id_caso": caso["id"],
                "tipo": caso["tipo"],
                "modelo": modelo,
                "latencia_ms": tiempo_ms,
                "tokens": tokens,
                "respuesta": respuesta[:200],   # primeros 200 caracteres
            })

    # --- Guardamos todo en un CSV ---
    ruta_csv = OUTPUT_DIR / "resultados_benchmark.csv"
    with open(ruta_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id_caso", "tipo", "modelo", "latencia_ms", "tokens", "respuesta"])
        writer.writeheader()
        writer.writerows(resultados)

    print(f"\n\n✅ Resultados guardados en: {ruta_csv}")

    # --- Resumen por modelo ---
    print("\n" + "=" * 70)
    print("RESUMEN POR MODELO")
    print("=" * 70)
    for modelo in MODELOS:
        datos_modelo = [r for r in resultados if r["modelo"] == modelo and r["latencia_ms"] > 0]
        if datos_modelo:
            latencia_media = sum(r["latencia_ms"] for r in datos_modelo) / len(datos_modelo)
            tokens_media = sum(r["tokens"] for r in datos_modelo) / len(datos_modelo)
            print(f"\n{modelo}:")
            print(f"  Latencia media: {latencia_media:.0f} ms")
            print(f"  Tokens media: {tokens_media:.0f}")


if __name__ == "__main__":
    ejecutar_benchmark()