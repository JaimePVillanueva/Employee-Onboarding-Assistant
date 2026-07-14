"""
state.py - Estado de sesión del asistente.

Qué hace este script:
 - Guarda el perfil usuario e historial de mensajes entre turnos.
 - Funciones básicas; append_user, append_assitant, last_messages.

"""

def inicializar_estado(user_profile: dict | None = None) -> dict: ## Función para crear el diccionario de la sesión
    return {
        "user_profile": user_profile or {},
        "messages": [],
        "turnos": 0,
    }


def append_user(state: dict, texto: str) -> None: ## Función para añadir el mensaje del usuario al historial
    state["messages"].append({"role": "user", "text": texto.strip()})


def append_assistant(state: dict, texto: str) -> None: ## Función para añadir el mensaje del asistente al historial
    state["messages"].append({"role": "assistant", "text": texto.strip()})
    state["turnos"] = state.get("turnos", 0) + 1


def last_messages(state: dict, messages: int) -> list[dict]: ## Función para devolver los últimos mensajes de la sesión
    msgs = state.get("messages", [])
    return msgs[-messages:] if n > 0 else []