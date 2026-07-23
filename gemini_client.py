import time
from dataclasses import dataclass

from google import genai
from google.genai import types

from config import MAX_TOKENS_INPUT, MODEL, TEMPERATURE, TEMPERATURE_VULNERABLE ## No importamos MAX_INPUT_CHARS
from gemini_auth import configurar_gemini_api_key

configurar_gemini_api_key()


@dataclass
class MetricasLlamada: ## Clase MetricasLlamada
    elapsed_ms: int
    prompt_tokens: int | None
    output_tokens: int | None
    total_tokens: int | None


_client_instance: genai.Client | None = None ## Declaración de la variable de cliente


def _client() -> genai.Client: ## Función de cliente: establece el cliente de genai si está vacío
    global _client_instance
    if _client_instance is None:
        _client_instance = genai.Client()
    return _client_instance


def count_tokens(contents: str) -> int: ## Mide la cantidad de tokens que gastará la entrada
    r = _client().models.count_tokens(model=MODEL, contents=contents)
    return int(r.total_tokens or 0)


def _metricas_from_response(response, started: float) -> MetricasLlamada: ## Devuelve un objeto de la clase MetricasLlamada con los parámetros de la respuesta
    elapsed_ms = int((time.time() - started) * 1000) ## Mide el tiempo que ha tomado hacer la llamada
    um = response.usage_metadata 
    return MetricasLlamada(
        elapsed_ms=elapsed_ms,
        prompt_tokens=getattr(um, "prompt_token_count", None),
        output_tokens=getattr(um, "candidates_token_count", None),
        total_tokens=getattr(um, "total_token_count", None),
    )


def llamar_gemini( ## Función para llamar a gemini
    prompt: str,
    *,
    model: str,
    temperature: float = TEMPERATURE_VULNERABLE, ## Está establecida a 0.2
) -> tuple[str, MetricasLlamada]:
    started = time.time() ## Guarda en started la hora en la que se ha hecho la llamada
    response = _client().models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(temperature=temperature),
    )
    return (response.text or "").strip(), _metricas_from_response(response, started) ## Llama a la función anterior para sacar el objeto MetricasLlamada


def llamar_gemini_json( ## Misma función que la anterior pero fuerza la respuesta en formato JSON
    prompt: str,
    *,
    model: str,
    temperature: float = TEMPERATURE,
) -> tuple[str, MetricasLlamada]:
    started = time.time()
    response = _client().models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=temperature,
            response_mime_type="application/json",
        ),
    )
    return (response.text or "").strip(), _metricas_from_response(response, started)


def safe_generate( ## Llama a una función un otra (de llamada a gemini) dependiendo de si se pide a la función que la respuesta sea en JSON o no
    prompt: str,
    *,
    model: str,
    temperature: float = TEMPERATURE,
    json_mode: bool = False,
) -> tuple[str, MetricasLlamada]:
    tokens = count_tokens(prompt)
    if tokens > MAX_TOKENS_INPUT:
        raise ValueError(
            f"Prompt demasiado grande: {tokens} tokens (máx {MAX_TOKENS_INPUT}). "
            "Recorta contexto en Python."
        )
    if json_mode:
        return llamar_gemini_json(prompt, model= model, temperature=temperature)
    return llamar_gemini(prompt, model, temperature=temperature)