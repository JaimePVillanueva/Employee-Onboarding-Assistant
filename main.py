# ============================================
# PROGRAMA PRINCIPAL (demos)
# ============================================

from datos import buscar_empleado
from asistente import procesar_chat, procesar_checklist


# --- Función para imprimir el resultado del chat bonito ---
def imprimir_chat(resultado):
    print("=" * 60)
    if resultado["status"] == "error":
        print(f"[ERROR] {resultado['message']}")
        for e in resultado["errores"]:
            print(f"  - {e}")
        return

    data = resultado["data"]
    print(f"[OK] {resultado['message']} — perfil: {data['perfil']}")
    print("=" * 60)
    print(f"\n{data['respuesta']}\n")
    print(f"Para más info, contacta con: {data['escalar']}")
    print(f"FAQs usadas: {data['faqs']}")
    print(f"Docs usados: {data['docs']}")
    print(f"\nLatencia: {data['metricas']['elapsed_ms']} ms")
    print(f"Tokens entrada: {data['metricas']['prompt_tokens']}")
    print(f"Tokens salida: {data['metricas']['output_tokens']}")


# --- Función para imprimir el checklist bonito ---
def imprimir_checklist(resultado):
    print("=" * 60)
    if resultado["status"] == "error":
        print(f"[ERROR] {resultado['message']}")
        for e in resultado["errores"]:
            print(f"  - {e}")
        return

    data = resultado["data"]
    print(f"[OK] Checklist de {data['empleado']} — Día {data['dia']}")
    print("=" * 60)
    print("Tareas:")
    for tarea in data["tareas"]:
        print(f"  - {tarea.get('titulo', '')}")
    print(f"\nLatencia: {data['metricas']['elapsed_ms']} ms")


# --- DEMO 1: conversación de 1 turno (empleado dev junior) ---
def demo_chat():
    print("\n\n### DEMO 1: CHAT (dev junior) ###\n")
    empleado = buscar_empleado("emp_01")  # Laura, dev_junior
    pregunta = "¿Qué canales de Slack debo unirme?"
    resultado = procesar_chat(empleado, pregunta)
    imprimir_chat(resultado)


# --- DEMO 2: checklist del día 1 ---
def demo_checklist():
    print("\n\n### DEMO 2: CHECKLIST (día 1) ###\n")
    empleado = buscar_empleado("emp_01")  # Laura
    resultado = procesar_checklist(empleado, dia=1)
    imprimir_checklist(resultado)


# --- DEMO 3: mismo mensaje, empleado comercial vs remoto ---
def demo_perfiles():
    print("\n\n### DEMO 3: MISMA PREGUNTA, PERFILES DISTINTOS ###\n")
    pregunta = "¿Cómo pido vacaciones?"

    print(">>> Empleado COMERCIAL (Pablo):")
    comercial = buscar_empleado("emp_02")
    imprimir_chat(procesar_chat(comercial, pregunta))

    print("\n>>> Empleado REMOTO UE (Sofia):")
    remoto = buscar_empleado("emp_03")
    imprimir_chat(procesar_chat(remoto, pregunta))


# --- Ejecutar todas las demos ---
def main():
    demo_chat()
    demo_checklist()
    demo_perfiles()


if __name__ == "__main__":
    main()