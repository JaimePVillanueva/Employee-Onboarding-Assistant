from state import EstadoConversacion

MAX_TURNOS = 4


def actualizar_historial(estado: EstadoConversacion, pregunta: str, respuesta: str):
    if len(estado.historial) >= MAX_TURNOS:
        return False
    estado.historial.append({"pregunta": pregunta, "respuesta": respuesta})
    estado.turnos_restantes -= 1
    return True