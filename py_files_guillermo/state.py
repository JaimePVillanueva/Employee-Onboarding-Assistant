
def inicializar_estado(*,user_profile: dict | None = None) -> dict:
    """Inicializa el estado con el perfil de usuario y pone los mensajes y turnos a cero """
    return {
        "user_profile": user_profile or {},
        "messages": [],
        "turnos": 0,
    }

def append_user(state: dict, texto: str) -> None:
    """añade el mensaje del usuario al hitorial"""
    state["messages"].append({"role": "user", "text": texto.strip()})


def append_assistant(state: dict, texto: str) -> None:
    """añade respuesta del asistente al historial e incrementa turnos +1"""
    state["messages"].append({"role": "assistant", "text": texto.strip()})
    state["turnos"] = state.get("turnos", 0) + 1


def ultimos_n(state: dict, n: int) -> list[dict]:
    """Devuelve lista de los ultimos mensajes
    
    Parametro n es el número de mensajes a devolver"""
    msgs = state.get("messages", [])
    return msgs[-n:] if n > 0 else []
