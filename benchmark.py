import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone

from config import MODELS, PREGUNTAS_PATH, TEMPERATURE
from gemini_client import llamar_gemini


@dataclass
class FilaBenchmark: ## Clase FilaBenchmark
    timestamp: str
    pregunta_id: str
    modelo: str
    elapsed_ms: int
    prompt_tokens: int | None
    output_tokens: int | None
    total_tokens: int | None
    respuesta: str
    error: str | None = None


def cargar_preguntas() -> list[dict]:
    with PREGUNTAS_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def ejecutar_benchmark() -> list[FilaBenchmark]:
    preguntas = cargar_preguntas()
    filas: list[FilaBenchmark] = []

    for p in preguntas:
        pid = p["id"]
        prompt = p["prompt"]
        for modelo in MODELS:
            ts = datetime.now(timezone.utc).isoformat()
            try:
                texto, m = llamar_gemini(prompt, model=modelo, temperature=TEMPERATURE)
                filas.append(
                    FilaBenchmark(
                        timestamp=ts,
                        pregunta_id=pid,
                        modelo=modelo,
                        elapsed_ms=m.elapsed_ms,
                        prompt_tokens=m.prompt_tokens,
                        output_tokens=m.output_tokens,
                        total_tokens=m.total_tokens,
                        respuesta=texto,
                    )
                )
                print(f"OK  {pid} × {modelo} ({m.elapsed_ms} ms)")
            except Exception as exc:  # noqa: BLE001 — demo didáctica
                filas.append(
                    FilaBenchmark(
                        timestamp=ts,
                        pregunta_id=pid,
                        modelo=modelo,
                        elapsed_ms=0,
                        prompt_tokens=None,
                        output_tokens=None,
                        total_tokens=None,
                        respuesta="",
                        error=str(exc),
                    )
                )
                print(f"ERR {pid} × {modelo}: {exc}")

    return filas


def filas_a_dicts(filas: list[FilaBenchmark]) -> list[dict]:
    return [asdict(f) for f in filas]
