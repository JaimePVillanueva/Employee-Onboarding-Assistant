from state import EstadoConversacion

MAX_TURNOS = 4


def actualizar_historial(estado: EstadoConversacion, pregunta: str, respuesta: str):
    if len(estado.historial) >= MAX_TURNOS:
        return False
    estado.historial.append({"pregunta": pregunta, "respuesta": respuesta})
    estado.turnos_restantes -= 1
    return True
def marcar_tarea (estado, tarea_id: str, completado : bool):
    # Busca la tarea por ID y actualiza su estado
    # Devuelve True si lo encontro, False si no
    for tarea in estado.tareas:
        if tarea ["id"] == tarea_id:
            tarea ["completado"] = completado
            return True
    return False
def preguntar_tareas_completadas (estado):
    # Al final del dia pregunta la empleado qué tareas completo
    # Actualiza el estado que mañana sepa que quedo pendiente
    print ("\n=== REVISIÓN DE TAREAS DEL DÍA ===")
    for tarea in estado.tareas:
        respuesta = input (f" ¿Completaste '{tarea['titulo']}'? (S/N): ")
        # Comparamos con "s" - cualquier otra respuesta = no completada.
        tarea["completado"] = respuesta.lower() == "s"
    print ("Tareas actualizadas")