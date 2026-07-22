import json

from copy import deepcopy

from config import (
    DATA_DIR,
    ASSISTANT_CONFIG_DEFAULT,
    KEY_CHECK
    )

from context import (
    cargar_docs,
    cargar_faq,
    cargar_empresa,
    seleccion_doc,
    seleccion_faq,
    seleccion_escalado
    )

from gemini_client import(
    MetricasLlamada,
    safe_generate
    )

from prompts import (
    build_assistant_prompt,
    prompt_tareas,
    comprobar_tareas,
    prompt_resumen_tareas
    )

from state import (
    inicializar_estado,
    append_assistant,
    append_user
    )

from validators import (
    valid_data,
    valid_check
    )

def inicializar_checklist(*,state:dict)->dict:
    p_tareas=prompt_tareas(state=state,docs=cargar_docs(DATA_DIR / 'onboarding_docs.json'))
    try:
       raw_tarea,metricas_tarea=safe_generate(p_tareas,temperature=0,json_mode=True)
    except ValueError as e:
        return respuesta_error('Error al generar',[str(e)])
    
    tareas=parsear_tareas(raw_tarea)
    state['tareas']=tareas
    return _metricas_to_dict(metricas_tarea)

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


def crear_estado_demo(*,empleado:dict|None=None,dia:int|None=None) -> dict:
    if not empleado:
        return inicializar_estado(
            user_profile={
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
            user_profile={
                "nombre": empleado.get('nombre',''),
                "departamento": empleado.get('departamento',''),
                "rol": empleado.get('rol',''),
                "modalidad": empleado.get('modalidad',''),
                "idioma_preferido": empleado.get('idioma_preferido',''),
                "perfil": empleado.get('perfil',''),
                "dia":dia or 1,
            }
        )

def initialize_assistant(perfil:str)->dict:
    config = deepcopy(ASSISTANT_CONFIG_DEFAULT)
    config["perfil_activo"] = perfil
    return config

def parsear_tareas(check:str)->list[dict]:
    try:
        tareas=json.loads(check)
    except:
        raise ValueError ('Formato JSON respuesta inválido')
    for t in tareas:
        if not all(key in t for key in KEY_CHECK):
            raise ValueError ('Faltan keywords')
    return tareas

def procesar_turno(
    *,
    state:dict,
    u_message:str,
)->dict:
    errores=valid_data(u_message,state)
    if errores:
        return respuesta_error('Turno no procesado',errores=errores)
    faqs=seleccion_faq(cargar_faq(DATA_DIR / 'faq_onboarding.json'),u_message)
    docs=seleccion_doc(cargar_docs(DATA_DIR / 'onboarding_docs.json'),faqs=faqs,pregunta=u_message)
    contacto=seleccion_escalado(empresa=cargar_empresa(DATA_DIR / 'empresa.json'),doc=docs[0])
    if state['user_profile']:
        config=initialize_assistant(state.get('user_profile').get('perfil','dev_junior'))
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
    
    append_user(state, u_message)
    append_assistant(state, texto)

    return respuesta_ok(
        "Turno procesado",
        {
            "respuesta": texto,
            "perfil": config["perfil_activo"],
            "metricas": _metricas_to_dict(metricas),
            "faqs":faqs,
            "docs":docs,
            'escalar': contacto
        },
    )

def procesar_checklist(
    *,
    state:dict,
    dia:int|None=None,
)->dict:
    if not dia:
        dia=1
    errores=valid_check(state,dia=dia)
    if errores:
        return respuesta_error('Turno no procesado',errores=errores)
    comprobar_tareas(state=state,dia=dia)
    tareas= [t for t in state.get('tareas') if not t.get('completada',False) and t.get('dia',1)<=dia]
    prompt=prompt_resumen_tareas(tareas=tareas)
    try:
        resumen,metricas=safe_generate(prompt=prompt)
    except ValueError as e:
        return respuesta_error("Error de resumen", [str(e)])
    return respuesta_ok(
        "Turno procesado",
        {
            "empleado": state.get('user_profile').get('nombre'),
            "dia": state.get('user_profile').get('dia'),
            "metricas": _metricas_to_dict(metricas),
            'tareas':tareas,
            'mensaje_resumen':resumen
        },
    )