import json
from datetime import date
from config import MODEL
from context import get_contexto
from prompts import build_prompt_chat, build_prompt_checklist
from logic import actualizar_historial, MAX_TURNOS
from state import crear_estado, guardar_dia, tareas_pendientes
from gemini_client import safe_generate
from validators import verificar_preguntas_json, verificar_entregables
from error import EscenarioNoAceptado


def resolver_faqs_docs(contexto):
    # Ya no dependemos de que el LLM cite IDs correctamente.
    # Usamos directamente lo que Python ya encontró por keywords,
    # así evitamos mostrar IDs inventados o mal recordados por el modelo.
    faqs_texto = [f"{f['id']}({f['pregunta']})" for f in contexto["faqs_keywords"]]
    docs_texto = [f"{d['id']}({d['titulo']})" for d in contexto["docs_keywords"]]
    return faqs_texto, docs_texto


def imprimir_respuesta_chat(respuesta_json, metricas, empleado, contexto):
    faqs_legibles, docs_legibles =resolver_faqs_docs(contexto)

    

    resultado = {
        "status": "ok",
        "message": "Turno procesado",
        "data": {
            "perfil": empleado["perfil"],
            "respuesta": respuesta_json["respuesta"],
            "faqs": [f["id"] for f in contexto["faqs_keywords"]],
            "docs": [d["id"] for d in contexto["docs_keywords"]],
            "metricas": {
                "elapsed_ms": metricas.elapsed_ms,
                "prompt_tokens": metricas.prompt_tokens,
                "output_tokens": metricas.output_tokens,
                "total_tokens": metricas.total_tokens,
            },
        },
    }

    print(f"\n[OK] Turno procesado: {resultado['data']['perfil']}")
    print("===================================")
    print(resultado["data"]["respuesta"])
    print(f"FAQs: [{', '.join(faqs_legibles)}]")
    print(f"Docs: [{', '.join(docs_legibles)}]")
    print(f"latencia: {metricas.elapsed_ms}")
    print(f"tokens entrada: {metricas.prompt_tokens}")
    print(f"tokens salida: {metricas.output_tokens}")
    return resultado


def imprimir_respuesta_checklist(checklist, empleado, metricas=None):
    resultado = {
        "status": "ok",
        "message": "Checklist creada",
        "data": {
            "empleado": empleado,
            "dia": checklist["dia"],
            "tareas": checklist["tareas"],
            "mensaje_resumen": checklist["mensaje_resumen"],
        },
    }

    print(f"\nNombre: {empleado['nombre']}    Día: {checklist['dia']}")
    print("=================================")
    print(checklist["mensaje_resumen"])
    print("Tareas:")
    for t in checklist["tareas"]:
        marca = "x" if t["completado"] else " "
        print(f" - [{marca}] {t['titulo']}")
    return resultado

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
    respuesta_raw, metricas = safe_generate(prompt, model=MODEL, json_mode=True)
    respuesta_json = json.loads(respuesta_raw)
    imprimir_respuesta_chat(respuesta_json, metricas, contexto["empleado"], contexto)


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
    checklist_str, metricas = safe_generate(prompt, model=MODEL, json_mode=True)
    checklist = json.loads(checklist_str)
    imprimir_respuesta_checklist(checklist, contexto["empleado"], metricas)


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
    respuesta_raw, metricas = safe_generate(prompt_comercial, model=MODEL, json_mode=True)
    respuesta_json = json.loads(respuesta_raw)
    imprimir_respuesta_chat(respuesta_json, metricas, contexto_comercial["empleado"], contexto_comercial)

    print("\n-- Empleado remoto UE (emp_03) --")
    contexto_remoto = get_contexto("emp_03", 1, pregunta)
    prompt_remoto = build_prompt_chat(contexto_remoto, pregunta, [])
    respuesta_raw, metricas = safe_generate(prompt_remoto, model=MODEL, json_mode=True)
    respuesta_json = json.loads(respuesta_raw)
    imprimir_respuesta_chat(respuesta_json, metricas, contexto_remoto["empleado"], contexto_remoto)


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

    pendientes = tareas_pendientes(empleado_id, dia)
    if pendientes:
        print("\n Tienes tareas pendientes de días anteriores: ")
        for t in pendientes:
            print(f" - [Día {t['dia_origen']}] {t['titulo']}")

    contexto = get_contexto(empleado_id, dia, "")
    prompt = build_prompt_checklist(contexto, pendientes)
    checklist_str, _ = safe_generate(prompt, model=MODEL, json_mode=True)
    checklist = json.loads(checklist_str)
    imprimir_respuesta_checklist(checklist, contexto["empleado"])
    estado = crear_estado(empleado_id, dia, checklist["tareas"])

    print(f"\nHola {contexto['empleado']['nombre']}, puedes hacerme hasta {MAX_TURNOS} preguntas.\n")

    while estado.turnos_restantes > 0:
        pregunta = input("Tu pregunta: ")
        contexto = get_contexto(empleado_id, dia, pregunta)
        prompt = build_prompt_chat(contexto, pregunta, estado.historial)
        respuesta_raw, metricas = safe_generate(prompt, model=MODEL, json_mode=True)
        respuesta_json = json.loads(respuesta_raw)

        imprimir_respuesta_chat(respuesta_json, metricas, contexto["empleado"], contexto)

        continuar = actualizar_historial(estado, pregunta, respuesta_json["respuesta"])
        if not continuar:
            break

    from logic import preguntar_tareas_completadas
    preguntar_tareas_completadas(estado)
    guardar_dia(estado)
    print("\n Fin de la conversación. ¡Mucho ánimo!")


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