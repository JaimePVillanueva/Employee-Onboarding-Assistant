from context import get_contexto, get_empleado
from prompts import build_prompt_chat, build_prompt_checklist, actualizar_historial
from logic import procesar_turno, respuesta_ok, respuesta_error
from gemini_client import safe_generate
from state import inicializar_estado, last_messages, append_user, append_assistant
from config import WINDOW, MODELS
from validators import verificar_preguntas_json, verificar_entregables
from error import EscenarioNoAceptado
from benchmark import ejecutar_benchmark
from report import guardar_csv, _medias_por_modelo, generar_reporte_md, guardar_json



def demo_1():
    """Demo 1 — Conversación 1 turno con dev junior (emp_01)"""
    print("Comprobando archivos...")
    ok_preguntas, errores_preguntas = verificar_preguntas_json()
    ok_entregables, errores_entregables = verificar_entregables()
    if (ok_preguntas == True and not errores_preguntas) and (ok_entregables == True and not errores_entregables):
        print("Archivos comprobados y aceptados")
    else:
        print(errores_entregables, errores_preguntas)
        raise EscenarioNoAceptado("Archivos no permitidos, revisar archivos")
    print("\n=== DEMO 1 — Conversación dev junior ===")
    pregunta = "¿A qué canales de Slack me uno?"
    contexto = get_contexto("emp_01", 1, pregunta)
    prompt = build_prompt_chat(contexto, pregunta, [])
    respuesta, metricas = safe_generate(prompt, MODELS[0], json_mode=True)
    print(f"Empleado: {pregunta}")
    print(f"Asistente: {respuesta}")
    print("Ejecutando benchmark...")
    filas = ejecutar_benchmark(prompt)
    csv_path = guardar_csv(filas)
    md_path = generar_reporte_md(filas, csv_path)
    print(f"\nCSV: {csv_path}")
    print(f"Informe: {md_path}")
    print("\nSiguiente: completa entregables/matriz_decision.md y recomendacion.md")


def demo_2():
    """Demo 2 — Checklist JSON día 1"""
    print("Comprobando archivos...")
    ok_preguntas, errores_preguntas = verificar_preguntas_json()
    ok_entregables, errores_entregables = verificar_entregables()
    if (ok_preguntas == True and not errores_preguntas) and (ok_entregables == True and not errores_entregables):
        print("Archivos comprobados y aceptados")
    else:
        print(errores_entregables, errores_preguntas)
        raise EscenarioNoAceptado("Archivos no permitidos, revisar archivos")
    print("\n=== DEMO 2 — Checklist día 1 ===")
    contexto = get_contexto("emp_01", 1, "")
    prompt = build_prompt_checklist(contexto)
    checklist, metricas = safe_generate(prompt, MODELS[0], json_mode=True)
    print(checklist)
    print(f"Tokens: {metricas.total_tokens} | Latencia: {metricas.elapsed_ms}ms")


def demo_3():
    """Demo 3 — Mismo mensaje con comercial vs remoto UE"""
    print("Comprobando archivos...")
    ok_preguntas, errores_preguntas = verificar_preguntas_json()
    ok_entregables, errores_entregables = verificar_entregables()
    if (ok_preguntas == True and not errores_preguntas) and (ok_entregables == True and not errores_entregables):
        print("Archivos comprobados y aceptados")
    else:
        print(errores_entregables, errores_preguntas)
        raise EscenarioNoAceptado("Archivos no permitidos, revisar archivos")
    print("\n=== DEMO 3 — Comercial vs Remoto UE ===")
    pregunta = "¿Puedo trabajar desde otro país esta semana?"

    print("\n-- Empleado comercial (emp_02) --")
    contexto_comercial = get_contexto("emp_02", 1, pregunta)
    prompt_comercial = build_prompt_chat(contexto_comercial, pregunta, [])
    respuesta_comercial, _ = safe_generate(prompt_comercial, MODELS[0], json_mode=True)
    print(f"Asistente: {respuesta_comercial}")

    print("\n-- Empleado remoto UE (emp_03) --")
    contexto_remoto = get_contexto("emp_03", 1, pregunta)
    prompt_remoto = build_prompt_chat(contexto_remoto, pregunta, [])
    respuesta_remoto, _ = safe_generate(prompt_remoto, MODELS[0], json_mode=True)
    print(f"Asistente: {respuesta_remoto}")


def modo_interactivo():
    """Modo interactivo — el empleado hace preguntas"""
    print("Comprobando archivos...")
    ok_preguntas, errores_preguntas = verificar_preguntas_json()
    ok_entregables, errores_entregables = verificar_entregables()
    if (ok_preguntas == True and not errores_preguntas) and (ok_entregables == True and not errores_entregables):
        print("Archivos comprobados y aceptados")
    else:
        print(errores_entregables, errores_preguntas)
        raise EscenarioNoAceptado("Archivos no permitidos, revisar archivos")
    print("\n=== ASISTENTE DE ONBOARDING BRIDGE SA ===")
    empleado_id = input("¿Cuál es tu ID de empleado? (ej: emp_01): ")
    dia = int(input("¿En qué día de onboarding estás? (1-5): "))

    contexto = get_contexto(empleado_id, dia, "")
    prompt_checklist = build_prompt_checklist(contexto)
    checklist = safe_generate(prompt = prompt_checklist, model = MODELS[0], json_mode = True)
    print("\n=== CHECKLIST DEL DÍA ===")
    print(checklist)


    print(f"\nHola {contexto['empleado']['nombre']}, puedes hacerme hasta {WINDOW} preguntas.\n")
    sesion = inicializar_estado(get_empleado)
    historial = []
    while len(historial) < WINDOW:
        pregunta = input("Tu pregunta: ")
        contexto = get_contexto(empleado_id, dia, pregunta)
        prompt = build_prompt_chat(contexto, pregunta, historial)
        respuesta = safe_generate(prompt = prompt, model = MODELS[0], json_mode=True)
        if not sesion:
            ultimo_turno = procesar_turno(ultimo_turno, pregunta, respuesta[0])
        else:
            ultimo_turno = procesar_turno(sesion, pregunta, respuesta[0])
        print(f"\nAsistente: {respuesta} \n")
        historial, continuar = actualizar_historial(historial, pregunta, respuesta)
        if not continuar:
            break
    guardar_json(ultimo_turno)
    print("Fin de la conversación. ¡Mucho ánimo!")


if __name__ == "__main__":
    print("¿Qué quieres ejecutar?")
    print("1 — Demo conversación dev junior")
    print("2 — Demo checklist día 1")
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