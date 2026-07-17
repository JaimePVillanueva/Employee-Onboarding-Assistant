from config import (ASSISTANT_CONFIG_DEFAULT,WINDOW)
from gemini_client import(MetricasLlamada,safe_generate)
from prompts import (build_assistant_prompt)
from state import (inicializar_estado)
def respuesta_ok(message:str,data:dict)->dict:
    return{
        'status':'ok',
        'message':message,
        'data':data
    }

def respuesta_error(message:str,errores:list[str])->dict:
    return{
        'status':'error',
        'message':message,
        'data':{'errores':errores}
    }

def _metricas_to_dict(metricas:MetricasLlamada)->dict:
    return{
        'elapsed_ms':metricas.elapsed_ms,
        'prompt_tokens':metricas.prompt_tokens,
        'output_tokens':metricas.output_tokens,
        'total_tokens':metricas.total_tokens
    }

def procesar_turno(
    state:dict,
    u_message:str,
    assistant_config:dict | None = None,
    faqs:list[dict] | None = None,
    docs:list[dict] | None = None
)->dict:
    errores=[]
    if not u_message.strip():
        errores.append('Mensaje de usuario no puede estar vacio')
    if not isinstance(state,dict):
        errores.append('State tiene que ser un diccionario')
    if errores:
        return respuesta_error('Turno no procesado',errores=errores)
    config= assistant_config or ASSISTANT_CONFIG_DEFAULT.copy()
    ventana= max(config.get('max_turnos_historial',WINDOW),WINDOW)
    prompt=build_assistant_prompt(
        assistant_config=config,
        user_state=state,
        user_message=u_message,
        extra_context={
            'faqs':faqs or [],
            'docs':docs or []
            },
            # recent_messages= ultimos_n(state,ventana)
    )
    try:
        texto,metricas=safe_generate(prompt,temperature=config['temperature'])
    except ValueError as e:
        return respuesta_error('Error al generar',[str(e)])
    # actualizar_perfil_desde_mensaje(state, u_message)
    # append_user(state, u_message)
    # append_assistant(state, texto)

    return respuesta_ok(
        "Turno procesado",
        {
            "respuesta": texto,
            "perfil": config["perfil_activo"],
            "metricas": _metricas_to_dict(metricas),
            "faqs":faqs,
            "docs":docs
        },
    )

def crear_estado_demo() -> dict:
    return inicializar_estado(
        {
            "nombre": "",
            "nivel": "junior",
            "tema_actual": "",
        }
    )