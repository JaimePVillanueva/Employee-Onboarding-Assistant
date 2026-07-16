from context import get_contexto
from prompts import build_prompt_chat, build_prompt_checklist
from logic import actualizar_historial, MAX_TURNOS
from gemini_client import safe_generate


def demo_1():
    """Demo 1 — Conversación 1 turno con dev junior (emp_01)"""
    print("\n=== DEMO 1 — Conversación dev junior ===")
    pregunta = "¿A qué canales de Slack me uno?"
    contexto = get_contexto("emp_01", 1, pregunta)
    prompt = build_prompt_chat(contexto, pregunta, [])
    respuesta, metricas = safe_generate(prompt)
    print(f"Empleado: {pregunta}")
    print(f"Asistente: {respuesta}")
    print(f"Tokens: {metricas.total_tokens} | Latencia: {metricas.elapsed_ms}ms")


def demo_2():
    """Demo 2 — Checklist JSON día 1"""
    print("\n=== DEMO 2 — Checklist día 1 ===")
    contexto = get_contexto("emp_01", 1, "")
    prompt = build_prompt_checklist(contexto)
    checklist, metricas = safe_generate(prompt, json_mode=True)
    print(checklist)
    print(f"Tokens: {metricas.total_tokens} | Latencia: {metricas.elapsed_ms}ms")


def demo_3():
    """Demo 3 — Mismo mensaje con comercial vs remoto UE"""
    print("\n=== DEMO 3 — Comercial vs Remoto UE ===")
    pregunta = "¿Puedo trabajar desde otro país esta semana?"

    print("\n-- Empleado comercial (emp_02) --")
    contexto_comercial = get_contexto("emp_02", 1, pregunta)
    prompt_comercial = build_prompt_chat(contexto_comercial, pregunta, [])
    respuesta_comercial, _ = safe_generate(prompt_comercial)
    print(f"Asistente: {respuesta_comercial}")

    print("\n-- Empleado remoto UE (emp_03) --")
    contexto_remoto = get_contexto("emp_03", 1, pregunta)
    prompt_remoto = build_prompt_chat(contexto_remoto, pregunta, [])
    respuesta_remoto, _ = safe_generate(prompt_remoto)
    print(f"Asistente: {respuesta_remoto}")


def modo_interactivo():
    """Modo interactivo — el empleado hace preguntas"""
    print("\n=== ASISTENTE DE ONBOARDING BRIDGE SA ===")
    empleado_id = input("¿Cuál es tu ID de empleado? (ej: emp_01): ")
    dia = int(input("¿En qué día de onboarding estás? (1-5): "))

    contexto = get_contexto(empleado_id, dia, "")
    prompt_checklist = build_prompt_checklist(contexto)
    checklist, _ = safe_generate(prompt_checklist, json_mode=True)
    print("\n=== CHECKLIST DEL DÍA ===")
    print(checklist)

    print(f"\nHola {contexto['empleado']['nombre']}, puedes hacerme hasta {MAX_TURNOS} preguntas.\n")

    historial = []
    while len(historial) < MAX_TURNOS:
        pregunta = input("Tu pregunta: ")
        contexto = get_contexto(empleado_id, dia, pregunta)
        prompt = build_prompt_chat(contexto, pregunta, historial)
        respuesta, _ = safe_generate(prompt)
        print(f"\nAsistente: {respuesta}\n")
        historial, continuar = actualizar_historial(historial, pregunta, respuesta)
        if not continuar:
            break

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