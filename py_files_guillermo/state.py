
def inicializar_estado(*,user_profile: dict | None = None) -> dict:
    return {
        "user_profile": user_profile or {},
        "messages": [],
        "turnos": 0,
    }

def append_user(state: dict, texto: str) -> None:
    state["messages"].append({"role": "user", "text": texto.strip()})


def append_assistant(state: dict, texto: str) -> None:
    state["messages"].append({"role": "assistant", "text": texto.strip()})
    state["turnos"] = state.get("turnos", 0) + 1


def ultimos_n(state: dict, n: int) -> list[dict]:
    msgs = state.get("messages", [])
    return msgs[-n:] if n > 0 else []
