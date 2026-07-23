import csv
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path


from config import OUTPUT_DIR

class FilaBenchmark: ## Clase FilaBenchmark
    timestamp: str
    modelo: str
    elapsed_ms: int
    prompt_tokens: int | None
    output_tokens: int | None
    total_tokens: int | None
    respuesta: str
    error: str | None = None

def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

def guardar_csv(filas: list[FilaBenchmark]) -> Path:
    OUTPUT_DIR.mkdir(exist_ok=True)
    path = OUTPUT_DIR / f"benchmark_{_stamp()}.csv"
    if not filas:
        path.write_text("", encoding="utf-8")
        return path

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(filas[0]).keys()))
        writer.writeheader()
        for fila in filas:
            writer.writerow(asdict(fila))
    return path