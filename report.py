import csv
from collections import defaultdict
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
import json

from benchmark import FilaBenchmark
from config import MODELS, OUTPUT_DIR, TEMPERATURE, DIAS_DIR


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


def _medias_por_modelo(filas: list[FilaBenchmark]) -> dict[str, dict[str, float]]:
    ok = [f for f in filas if not f.error]
    lat: dict[str, list[int]] = defaultdict(list)
    out_tok: dict[str, list[int]] = defaultdict(list)

    for f in ok:
        lat[f.modelo].append(f.elapsed_ms)
        if f.output_tokens is not None:
            out_tok[f.modelo].append(f.output_tokens)

    resumen: dict[str, dict[str, float]] = {}
    for modelo in MODELS:
        resumen[modelo] = {
            "runs_ok": float(len(lat.get(modelo, []))),
            "elapsed_ms_media": mean(lat[modelo]) if lat.get(modelo) else 0.0,
            "output_tokens_media": mean(out_tok[modelo]) if out_tok.get(modelo) else 0.0,
        }
    return resumen


def generar_reporte_md(filas: list[FilaBenchmark], csv_path: Path) -> Path:
    OUTPUT_DIR.mkdir(exist_ok=True)
    path = OUTPUT_DIR / f"report_{_stamp()}.md"
    medias = _medias_por_modelo(filas)
    errores = [f for f in filas if f.error]

    lineas = [
        "# Informe de benchmark",
        "",
        f"- Generado: {datetime.now(timezone.utc).isoformat()}",
        f"- Temperatura: {TEMPERATURE}",
        f"- Modelos: {', '.join(MODELS)}",
        f"- CSV: `{csv_path.name}`",
        "",
        "## Latencia media (ms)",
        "",
        "| Modelo | Runs OK | ms media | out tokens media |",
        "|--------|---------|----------|------------------|",
    ]

    for modelo in MODELS:
        m = medias[modelo]
        lineas.append(
            f"| {modelo} | {int(m['runs_ok'])} | {m['elapsed_ms_media']:.0f} | "
            f"{m['output_tokens_media']:.1f} |"
        )

    lineas.extend(["", "## Errores", ""])
    if errores:
        for e in errores:
            lineas.append(f"- `{e.pregunta_id}` × `{e.modelo}`: {e.error}")
    else:
        lineas.append("Ninguno.")

    lineas.extend(
        [
            "",
            "## Siguiente paso",
            "",
            "Completa `entregables/matriz_decision.md` con calidad 1–5 por pregunta.",
            "Escribe tu recomendación en `entregables/recomendacion.md`.",
            "",
        ]
    )

    path.write_text("\n".join(lineas), encoding="utf-8")
    return path

def guardar_json(state: dict) -> None:
    path = DIAS_DIR / f"report_{_stamp()}.md"
    json_ = json.dumps(state)
    path.write_text("\n".join(json_), encoding="utf-8")
    return None