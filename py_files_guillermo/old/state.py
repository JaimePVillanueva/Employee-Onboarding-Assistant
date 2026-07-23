def inicializar_estado(user_profile: dict | None = None) -> dict:
    return {
        "user_profile": user_profile or {},
        "messages": [],
        "turnos": 0,
    }