import json
import os
from dataclasses import dataclass, field

#Este modulo gestiona el Estado de la conversación
# Definimos Estado como todo lo que el asistente necesita "recordar"
# Mientras habla con el empleado; Quién es, qué día es, qué ha preguntado.
# Y además tareas pendientes.


@dataclass
class EstadoConversacion:
    empleado_id: str
    dia: int
    historial: list = field(default_factory=list)
    turnos_restantes: int = 4
    tareas : list = field(default_factory=list)


def crear_estado(empleado_id: str, dia: int, tareas : list) -> EstadoConversacion:
    return EstadoConversacion(
        empleado_id=empleado_id,
        dia=dia,
        tareas=tareas
        )

def last_messages (estado : EstadoConversacion) -> dict:
    #Convierte el estado en un diccionario serializable a JSON.
    # Porque los dataclasses no son serializables a JSON por defecto.
    # En un archivo JSON primero hay que convertirlos a diccionario.
    return {
        "empleado_id" : estado.empleado_id,
        "dia" : estado.dia,
        "historial" : estado.historial,
        "tareas" : estado.tareas
    }
def guardar_dia (estado: EstadoConversacion):
    # Guarda el estado del dia en un JSON en la carpeta "dias/"
    # os.makedirs crea la carpeta si no existe (exist_ok= True evita error)
    os.makedirs("dias", exist_ok=True)
    datos =last_messages(estado)
    ruta= f"dias/{estado.empleado_id}_dia_{estado.dia}.json"
    #ensure_ascii=False permite guardar caracteres especiales
    # Indent=2 formatea el JSON con sangría 2 para que sea legible
    with open( ruta, "w", encoding= "utf-8") as f:
        json.dump (datos, f, ensure_ascii=False, indent=2)
    print (f"Día guardado en {ruta}")
def cargar_dia_anterior (empleado_id:str, dia:int) -> dict | None:
    # Carga el archivo del dia anterior.
    # Si no existe (primer día o no se cargó) devuelve None
    ruta =f"dias/{empleado_id}_dia_{dia - 1}.json"
    if os.path.exists(ruta):
        with open(ruta, "r", encoding = "utf-8") as f:
            return json.load(f)
    return None
def tareas_pendientes (empleado_id :str , dia:int) ->list:
    # Devuelve las tareas del dia anterior que no se completaron
    # List comprehension para filtrar por "completado == False"
    dia_anterior =cargar_dia_anterior (empleado_id, dia)
    if not dia_anterior:
         return [] # Primer dia- no hay dia anterior
    return [t for t in dia_anterior ["tareas"] if not t["completado"]]