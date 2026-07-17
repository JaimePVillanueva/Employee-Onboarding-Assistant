from copy import deepcopy
from config import (DATA_DIR,ASSISTANT_CONFIG_DEFAULT)
from context import (cargar_docs,cargar_faq,seleccion_doc,seleccion_faq,seleccion_empleado,cargar_empleados)
from gemini_client import(MetricasLlamada,safe_generate)
from prompts import (build_assistant_prompt)
from state import (inicializar_estado)
from validators import valid_data

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


def crear_estado_demo(empleado:dict|None=None) -> dict:
    if not empleado:
        return inicializar_estado(
            {
                "nombre": "",
                "departamento": "engineering",
                "rol": "Junior Software Engineer",
                "modalidad": "",
                "idioma_preferido": "es",
                "perfil": "dev_junior",
                "dia":1,
            }
        )
    return inicializar_estado(
            {
                "nombre": empleado.get('nombre',''),
                "departamento": empleado.get('departamento',''),
                "rol": empleado.get('rol',''),
                "modalidad": empleado.get('modalidad',''),
                "idioma_preferido": empleado.get('idioma_preferido',''),
                "perfil": empleado.get('perfil',''),
                "dia":1,
            }
        )

def initialize_assistant(perfil:str)->dict:
    config = deepcopy(ASSISTANT_CONFIG_DEFAULT)
    config["perfil_activo"] = perfil
    return config

def procesar_turno(
    user_id:str,
    u_message:str,
)->dict:
    errores=(valid_data(u_message,user_id))
    if errores:
        return respuesta_error('Turno no procesado',errores=errores)
    
    faqs=seleccion_faq(cargar_faq(DATA_DIR / 'faq_onboarding.json'),u_message)
    docs=seleccion_doc(cargar_docs(DATA_DIR / 'onboarding_docs.json'),faqs=faqs,pregunta=u_message)
    empleado=seleccion_empleado(cargar_empleados(DATA_DIR / 'empleados_demo.json'),user_id)
    state=crear_estado_demo(empleado=empleado)
    if empleado:
        config=initialize_assistant(empleado.get('perfil','dev_junior'))
    else:
        config=initialize_assistant('dev_junior')
    prompt=build_assistant_prompt(
        assistant_config=config,
        user_state=state,
        user_message=u_message,
        extra_context={
            'faqs':faqs,
            'docs':docs
        },
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