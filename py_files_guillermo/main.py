from config import DATA_DIR
from logic import (
    procesar_turno,
    crear_estado_demo,
    procesar_checklist,
    inicializar_checklist,
)
from context import seleccion_empleado, cargar_empleados
from validators import valid_id
from state import guardar_estado, cargar_estado, tareas_pendientes_dias_anteriores

MAX_TURNOS = 4


def imprimir_resultado(respuesta: dict) -> None:
    status = respuesta.get('status', 'unknown').upper()
    message = respuesta.get('message', '')
    print(f'[{status}]')
    data = respuesta.get('data', {})
    if status == 'ERROR':
        print(message)
        for e in data.get('errores', []):
            print('\n -', e)
        return
    print(f'''
{message}: {data.get('perfil', 'junior')}
{'=' * 60}

{data.get('respuesta', '')}

Para más información contacta con {data.get('escalar')}

FAQs: {chr(10).join([f.get('pregunta', '') for f in data.get('faqs', [])])}
Docs: {chr(10).join([d.get('titulo', '') for d in data.get('docs', [])])}

Latencia: {data.get('metricas')['elapsed_ms']}
Tokens entrada: {data.get('metricas')['prompt_tokens']}
Tokens salida: {data.get('metricas')['output_tokens']}
''')


def imprimir_resultado_checklist(respuesta: dict) -> None:
    status = respuesta.get('status', 'unknown').upper()
    message = respuesta.get('message', '')
    print(f'[{status}] {message}\n')
    data = respuesta.get('data', {})
    if status == 'ERROR':
        for e in data.get('errores', []):
            print(' -', e)
        return
    print(f'''
Nombre: {data.get('empleado')}    Día: {data.get('dia', 0)}
{'-' * 50}
{data.get('mensaje_resumen', '')}
{'-' * 50}
Tareas:
 - {('\n - ').join(x.get('titulo', '') for x in data.get('tareas', []))}

--- INICIO METRICAS MENSAJE RESUMEN ---

Latencia: {data.get('metricas')['elapsed_ms']}
Tokens entrada: {data.get('metricas')['prompt_tokens']}
Tokens salida: {data.get('metricas')['output_tokens']}

--- FIN METRICAS MENSAJE RESUMEN ---
''')


def demo_1() -> None:
    print("=" * 60)
    print("1) conversación de 1 turno (empleado tipo dev junior).")
    print("=" * 60)
    pregunta = "¿Cuál es el horario de entrada?"
    user_id = 'demo'
    error = valid_id(user_id)
    if error:
        raise ValueError(error)
    empleado = seleccion_empleado(cargar_empleados(DATA_DIR / 'empleados_demo.json'), user_id)
    state = crear_estado_demo(empleado=empleado)
    imprimir_resultado(procesar_turno(state=state, u_message=pregunta))


def demo_2() -> None:
    print("=" * 60)
    print("2) creacion checklist.")
    print("=" * 60)
    user_id = 'emp_01'
    error = valid_id(user_id)
    if error:
        raise ValueError(error)
    empleado = seleccion_empleado(cargar_empleados(DATA_DIR / 'empleados_demo.json'), user_id)
    state = crear_estado_demo(empleado=empleado)
    metricas = inicializar_checklist(state=state)
    print(f'''
--- INICIO METRICAS ASIGNACION TAREAS ---

Latencia: {metricas['elapsed_ms']}
Tokens entrada: {metricas['prompt_tokens']}
Tokens salida: {metricas['output_tokens']}

--- FIN METRICAS ASGINACION TAREAS ---
''')
    imprimir_resultado_checklist(procesar_checklist(state=state))
    imprimir_resultado_checklist(procesar_checklist(state=state, dia=2))


def demo_3() -> None:
    print("=" * 60)
    print("3) conversación de 1 turno (empleado tipo comercial vs remoto UE).")
    print("=" * 60)
    pregunta = "¿Cuál es el horario de entrada?"
    for user in ['emp_02', 'emp_03']:
        error = valid_id(user)
        if error:
            raise ValueError(error)
        empleado = seleccion_empleado(cargar_empleados(DATA_DIR / 'empleados_demo.json'), user)
        state = crear_estado_demo(empleado=empleado)
        imprimir_resultado(procesar_turno(state=state, u_message=pregunta))

def modo_interactivo() -> None:
    print("=" * 60)
    print("MODO INTERACTIVO — ASISTENTE DE ONBOARDING BRIDGE SA")
    print("=" * 60)

    user_id = input("¿Cuál es tu ID de empleado? (ej: emp_01): ")
    error = valid_id(user_id)
    if error:
        raise ValueError(error)

    dia = int(input("¿En qué día de onboarding estás? (1-5): "))

    # Si ya existe progreso guardado de este empleado, lo recuperamos
    state = cargar_estado(user_id)

    if state:
        state["user_profile"]["dia"] = dia
        print(f"\nSe ha recuperado tu progreso anterior, {state['user_profile'].get('nombre')}.")
    else:
        empleado = seleccion_empleado(cargar_empleados(DATA_DIR / 'empleados_demo.json'), user_id)
        state = crear_estado_demo(empleado=empleado, dia=dia)
        metricas = inicializar_checklist(state=state)
        print(f'''
--- INICIO METRICAS ASIGNACION TAREAS ---

Latencia: {metricas['elapsed_ms']}
Tokens entrada: {metricas['prompt_tokens']}
Tokens salida: {metricas['output_tokens']}

--- FIN METRICAS ASIGNACION TAREAS ---
''')

    pendientes = tareas_pendientes_dias_anteriores(state, dia)
    if pendientes:
        print("\nTienes tareas pendientes de días anteriores:")
        for t in pendientes:
            print(f" - [Día {t['dia']}] {t['titulo']}")

    imprimir_resultado_checklist(procesar_checklist(state=state, dia=dia))

    print(f"\nPuedes hacerme hasta {MAX_TURNOS} preguntas (escribe 'salir' para terminar antes).\n")

    turno = 0
    while turno < MAX_TURNOS:
        pregunta = input("Tu pregunta: ")
        if pregunta.strip().lower() == "salir":
            break
        imprimir_resultado(procesar_turno(state=state, u_message=pregunta))
        turno += 1

    guardar_estado(user_id, state)
    print("\nFin de la conversación. ¡Mucho ánimo!")


# def main() -> None:
#     demo_1()
#     demo_2()
#     demo_3()


if __name__ == "__main__":
    print("¿Qué quieres ejecutar?")
    print("1 — Demo conversación dev junior")
    print("2 — Demo checklist")
    print("3 — Demo comercial vs remoto UE")
    print("4 — Modo interactivo")

    opcion = input("\nElige (1-4): ")

    if opcion == "1":
        demo_1()
    elif opcion == "2":
        demo_2()
    elif opcion == "3":
        demo_3()
    elif opcion == "4":
        modo_interactivo()
    else:
        print("Opción no válida.")