# ============================================
# EL ASISTENTE (cerebro del sistema)
# ============================================

import os
import time
import json
import getpass

from dotenv import load_dotenv
from google import genai
from google.genai import types

from config import (
    MODEL, TEMPERATURE, MAX_CARACTERES,
    PERFILES, REGLAS, PATRONES_PELIGROSOS, ESQUEMA_CHECKLIST,
)
from datos import (
    seleccionar_faqs, seleccionar_docs, decidir_escalado,
)


# ============================================
# 1. AUTENTICACIÓN CON GEMINI
# ============================================

def configurar_api():
    """Carga la clave de Gemini desde .env, o la pide por terminal."""
    load_dotenv()
    if not os.getenv("GEMINI_API_KEY"):
        os.environ["GEMINI_API_KEY"] = getpass.getpass("Pega tu GEMINI_API_KEY: ")


# Cliente de Gemini (se crea una sola vez)
_cliente = None

def obtener_cliente():
    global _cliente
    if _cliente is None:
        configurar_api()
        _cliente = genai.Client()
    return _cliente


# ============================================
# 2. VALIDACIÓN (robustez / seguridad)
# ============================================

def validar_mensaje(mensaje):
    """Comprueba que el mensaje sea seguro. Devuelve lista de errores (vacía si todo ok)."""
    errores = []

    # ¿Está vacío?
    if not mensaje.strip():
        errores.append("El mensaje está vacío")
        return errores

    # ¿Es demasiado largo?
    if len(mensaje) > MAX_CARACTERES:
        errores.append(f"Mensaje demasiado largo ({len(mensaje)}/{MAX_CARACTERES})")

    # ¿Contiene frases peligrosas (intento de manipulación)?
    mensaje_min = mensaje.lower()
    for patron in PATRONES_PELIGROSOS:
        if patron in mensaje_min:
            errores.append("Mensaje sospechoso: posible intento de manipulación")
            break

    return errores


# ============================================
# 3. CONSTRUIR EL PROMPT
# ============================================

def construir_prompt(empleado, pregunta, faqs, docs):
    """Junta toda la información en un prompt claro para Gemini."""
    perfil = empleado.get("perfil", "dev_junior")
    instrucciones_perfil = PERFILES.get(perfil, PERFILES["dev_junior"])

    # Formateamos las FAQs
    texto_faqs = ""
    for faq in faqs:
        texto_faqs += f"- P: {faq['pregunta']}\n  R: {faq['respuesta_corta']}\n"

    # Formateamos los documentos
    texto_docs = ""
    for doc in docs:
        texto_docs += f"- {doc['titulo']} ({doc['departamento']}): {doc['cuerpo']}\n"

    # Montamos el prompt completo con delimitadores claros
    prompt = f"""
{instrucciones_perfil}

{REGLAS}

--- DATOS DEL EMPLEADO ---
Nombre: {empleado.get('nombre', '')}
Perfil: {perfil}
Departamento: {empleado.get('departamento', '')}

--- DOCUMENTACIÓN DISPONIBLE ---
FAQs:
{texto_faqs}
Documentos:
{texto_docs}
--- FIN DOCUMENTACIÓN ---

--- PREGUNTA DEL EMPLEADO ---
{pregunta}

Responde de forma breve (máximo 200 palabras) usando solo la documentación.
"""
    return prompt.strip()


# ============================================
# 4. LLAMAR A GEMINI
# ============================================

def llamar_gemini(prompt, json_mode=False):
    """Llama a Gemini y devuelve (respuesta, metricas)."""
    cliente = obtener_cliente()
    inicio = time.time()

    # Configuración: si es json_mode, pedimos respuesta en JSON
    if json_mode:
        config = types.GenerateContentConfig(
            temperature=TEMPERATURE,
            response_mime_type="application/json",
        )
    else:
        config = types.GenerateContentConfig(temperature=TEMPERATURE)

    respuesta = cliente.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=config,
    )

    # Calculamos las métricas
    tiempo_ms = int((time.time() - inicio) * 1000)
    uso = respuesta.usage_metadata
    metricas = {
        "elapsed_ms": tiempo_ms,
        "prompt_tokens": getattr(uso, "prompt_token_count", None),
        "output_tokens": getattr(uso, "candidates_token_count", None),
        "total_tokens": getattr(uso, "total_token_count", None),
    }

    return (respuesta.text or "").strip(), metricas


# ============================================
# 5. FUNCIÓN PRINCIPAL DEL CHAT
# ============================================

def procesar_chat(empleado, pregunta):
    """Procesa una pregunta del empleado y devuelve la respuesta estructurada."""

    # Paso 1: validar el mensaje
    errores = validar_mensaje(pregunta)
    if errores:
        return {"status": "error", "message": "Mensaje no válido", "errores": errores}

    # Paso 2: seleccionar contexto relevante
    faqs = seleccionar_faqs(pregunta)
    docs = seleccionar_docs(pregunta, faqs)

    # Paso 3: decidir a quién derivar
    contacto = decidir_escalado(docs)

    # Paso 4: construir el prompt y llamar a Gemini
    prompt = construir_prompt(empleado, pregunta, faqs, docs)
    respuesta, metricas = llamar_gemini(prompt)

    # Paso 5: devolver todo estructurado
    return {
        "status": "ok",
        "message": "Turno procesado",
        "data": {
            "perfil": empleado.get("perfil", "dev_junior"),
            "respuesta": respuesta,
            "faqs": [f["id"] for f in faqs],
            "docs": [d["id"] for d in docs],
            "escalar": contacto,
            "metricas": metricas,
        },
    }


# ============================================
# 6. FUNCIÓN PRINCIPAL DEL CHECKLIST
# ============================================

def procesar_checklist(empleado, dia):
    """Genera el checklist (plan del día) para un empleado."""

    # Validar el día
    if not isinstance(dia, int) or dia < 1 or dia > 5:
        return {"status": "error", "message": "Día no válido", "errores": ["El día debe estar entre 1 y 5"]}

    # Cargamos los documentos para basar las tareas
    from datos import cargar_docs
    docs = cargar_docs()
    texto_docs = "\n".join([f"- {d['id']}: {d['titulo']}" for d in docs])

    # Construimos el prompt para generar las tareas
    prompt = f"""
Empleado: {empleado.get('nombre', '')} (perfil: {empleado.get('perfil', '')})
Día de onboarding: {dia}

Documentos disponibles:
{texto_docs}

{ESQUEMA_CHECKLIST}
"""

    # Llamamos a Gemini en modo JSON
    respuesta, metricas = llamar_gemini(prompt.strip(), json_mode=True)

    # Convertimos la respuesta en JSON
    try:
        tareas = json.loads(respuesta)
    except:
        return {"status": "error", "message": "Error al generar checklist", "errores": ["JSON inválido"]}

    return {
        "status": "ok",
        "message": "Checklist creada",
        "data": {
            "empleado": empleado.get("nombre", ""),
            "dia": dia,
            "tareas": tareas,
            "metricas": metricas,
        },
    }