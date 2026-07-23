import json
import os
from pathlib import Path
from config import DATA_DIR

ESTADOS_DIR = DATA_DIR.parent / "dias"


def inicializar_estado(*, user_profile: dict | None = None) -> dict:
    """Inicializa el estado con el perfil de usuario y pone los mensajes y turnos a cero"""
    return {
        "user_profile": user_profile or {},
        "messages": [],
        "turnos": 0,
    }


def append_user(state: dict, texto: str) -> None:
    """Añade el mensaje del usuario al historial"""
    state["messages"].append({"role": "user", "text": texto.strip()})


def append_assistant(state: dict, texto: str) -> None:
    """Añade respuesta del asistente al historial e incrementa turnos +1"""
    state["messages"].append({"role": "assistant", "text": texto.strip()})
    state["turnos"] = state.get("turnos", 0) + 1


def ultimos_n(state: dict, n: int) -> list[dict]:
    """Devuelve lista de los últimos mensajes"""
    msgs = state.get("messages", [])
    return msgs[-n:] if n > 0 else []

def _ruta_estado(empleado_id: str) -> Path:
    return ESTADOS_DIR / f"{empleado_id}_estado.json"


def guardar_estado(empleado_id: str, state: dict) -> None:
    os.makedirs(ESTADOS_DIR, exist_ok=True)
    ruta = _ruta_estado(empleado_id)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    print(f"Estado guardado en {ruta}")


def cargar_estado(empleado_id: str) -> dict | None:
    ruta = _ruta_estado(empleado_id)
    if ruta.exists():
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def tareas_pendientes_dias_anteriores(state: dict, dia: int) -> list[dict]:
    """Tareas de días anteriores al actual que siguen sin completar."""
    return [
        t for t in state.get("tareas", [])
        if t.get("dia", 1) < dia and not t.get("completada", False)
    ]
