from pathlib import Path

from context import get_contexto, get_docs_por_departamento, get_docs_por_keywords, get_empleado, get_faq_por_tag
from gemini_client import MetricasLlamada
from state import inicializar_estado, last_messages, append_user, append_assistant
from prompts import build_prompt_chat
from config import WINDOW, MODELS
from gemini_client import llamar_gemini


def respuesta_ok(mensaje: str, data: dict | None = None) -> dict: ## Función para devolver el diccionario con mensaje "ok"
    return {"status": "ok", "mensaje": mensaje, "data": data or {}}

def respuesta_error(mensaje: str, errores: list[str]) -> dict: ## Función para devolver el diccionario con mensaje "error"
    return {"status": "error", "mensaje": mensaje, "data": {"errores": errores}}

def _metricas_a_dict(m: MetricasLlamada) -> dict:
    return {
        "elapsed_ms": m.elapsed_ms,
        "prompt_tokens": m.prompt_tokens,
        "output_tokens": m.output_tokens,
        "total_tokens": m.total_tokens,
    }

def procesar_turno(
    state: dict,
    user_message: str,
    respuesta_modelo: str
    ## assistant_config: dict | None = None,
    ## faq_entries: list[dict] | None = None,
) -> dict:
    if not user_message.strip():
        return respuesta_error("Mensaje vacío", ["El mensaje no puede estar vacío."])
    ## prompt = build_prompt_chat(faq_entries, user_message, last_messages(state, WINDOW))

    append_user(state, user_message)
    append_assistant(state, respuesta_modelo)  

    return respuesta_ok("Turno completado", {"respuesta": respuesta_modelo})