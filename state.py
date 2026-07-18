from dataclasses import dataclass, field


@dataclass
class EstadoConversacion:
    empleado_id: str
    dia: int
    historial: list = field(default_factory=list)
    turnos_restantes: int = 4


def crear_estado(empleado_id: str, dia: int) -> EstadoConversacion:
    return EstadoConversacion(empleado_id=empleado_id, dia=dia)