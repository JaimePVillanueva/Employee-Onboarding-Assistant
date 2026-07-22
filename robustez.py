# ============================================
# ROBUSTEZ (Parte 3): validación avanzada y demo vulnerable vs seguro
# ============================================

import json
from config import DATA_DIR, PATRONES_PELIGROSOS, MAX_CARACTERES
from asistente import llamar_gemini, construir_prompt
from datos import seleccionar_faqs, seleccionar_docs


# --- Palabras que indican temas sensibles o fuera de dominio ---
PALABRAS_SENSIBLES = ("sueldo", "salario", "bonus", "nómina", "cuánto gana", "cuánto cobra")
PALABRAS_FUERA_DOMINIO = ("curso externo", "participante", "módulo", "ejercicio del programa")


def analizar_amenaza(mensaje):
    """
    Analiza un mensaje y devuelve el tipo de amenaza detectada (o None si es seguro).
    Esto es la validación fail-closed: bloquea ANTES de llamar al modelo.
    """
    m = mensaje.lower()

    # 1. Mensaje vacío o demasiado largo
    if not m.strip():
        return "vacio"
    if len(m) > MAX_CARACTERES:
        return "demasiado_largo"

    # 2. Intento de inyección
    for patron in PATRONES_PELIGROSOS:
        if patron in m:
            return "inyeccion"

    # 3. Dato sensible (salarios, datos de otros)
    for palabra in PALABRAS_SENSIBLES:
        if palabra in m:
            return "dato_sensible"

    # 4. Fuera de dominio (participantes externos)
    for palabra in PALABRAS_FUERA_DOMINIO:
        if palabra in m:
            return "fuera_de_dominio"

    # Si no detecta nada, es seguro
    return None


def respuesta_segura(tipo_amenaza):
    """Devuelve la respuesta segura según el tipo de amenaza, SIN llamar al modelo."""
    respuestas = {
        "inyeccion": "No puedo cambiar mi rol ni revelar información confidencial. Solo ayudo con el onboarding de Bridge SA.",
        "dato_sensible": "No puedo dar información sobre sueldos ni datos de otros empleados. Para esto, contacta con tu manager o con People (rrhh@bridgesa.example).",
        "fuera_de_dominio": "Este asistente solo atiende el onboarding de empleados de Bridge SA, no consultas de programas formativos externos.",
        "vacio": "El mensaje está vacío. Escribe tu pregunta.",
        "demasiado_largo": "El mensaje es demasiado largo. Por favor, resúmelo.",
    }
    return respuestas.get(tipo_amenaza, "Consulta no válida.")


# ============================================
# DEMO VULNERABLE vs SEGURO
# ============================================

def asistente_vulnerable(empleado, pregunta):
    """
    Versión SIN protecciones: llama al modelo directamente con cualquier input.
    Esto es lo que NO se debe hacer (solo para demostrar el riesgo).
    """
    faqs = seleccionar_faqs(pregunta)
    docs = seleccionar_docs(pregunta, faqs)
    prompt = construir_prompt(empleado, pregunta, faqs, docs)
    respuesta, _ = llamar_gemini(prompt)
    return respuesta


def asistente_seguro(empleado, pregunta):
    """
    Versión CON protecciones: valida ANTES de llamar al modelo (fail-closed).
    """
    amenaza = analizar_amenaza(pregunta)
    if amenaza:
        # Se rechaza SIN llamar al modelo
        return respuesta_segura(amenaza)
    # Solo si es seguro, llama al modelo
    faqs = seleccionar_faqs(pregunta)
    docs = seleccionar_docs(pregunta, faqs)
    prompt = construir_prompt(empleado, pregunta, faqs, docs)
    respuesta, _ = llamar_gemini(prompt)
    return respuesta


def demo_vulnerable_vs_seguro():
    """Compara las dos versiones con los 5 casos trampa."""
    from datos import buscar_empleado

    empleado = buscar_empleado("emp_01")

    # Cargamos los casos trampa
    with open(DATA_DIR / "casos_trampa.json", "r", encoding="utf-8") as f:
        casos = json.load(f)

    print("\n" + "=" * 70)
    print("DEMO ROBUSTEZ: VULNERABLE vs SEGURO")
    print("=" * 70)

    for caso in casos:
        print(f"\n\n### CASO: {caso['tipo'].upper()} ###")
        print(f"Ataque: {caso['mensaje']}")
        print("-" * 70)

        # Versión segura (la comprobamos primero para no gastar llamadas si bloquea)
        amenaza = analizar_amenaza(caso["mensaje"])
        if amenaza:
            print(f"[SEGURO] 🛡️ Bloqueado SIN llamar al modelo (amenaza: {amenaza})")
            print(f"         Respuesta: {respuesta_segura(amenaza)}")
        else:
            print("[SEGURO] ✅ Pasó la validación, se procesa normalmente")

        print(f"\nComportamiento esperado: {caso['comportamiento_seguro']}")


if __name__ == "__main__":
    demo_vulnerable_vs_seguro()