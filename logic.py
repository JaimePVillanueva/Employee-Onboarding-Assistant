import json

from copy import deepcopy

from config import (
    DATA_DIR,
    ASSISTANT_CONFIG_DEFAULT,
    KEY_CHECK,
    DEFAULT_CONTACT
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
    p_tareas=prompt_tareas(state=state,docs=cargar_docs(DATA_DIR / 'onboarding_docs.json')) #Genera el prompt para pedir que asigne tareas al usuario
    try:
       raw_tarea,metricas_tarea=safe_generate(p_tareas,temperature=0,json_mode=True) #llamamos al modelo pidiendo una estructura Json de vuelta
    except ValueError as e:
        return respuesta_error('Error al generar',[str(e)]) #Devolvemos el error que da si no se puede ejecutar la llamada
    
    tareas=parsear_tareas(raw_tarea) #Convertimos la respuesta en un diccionario
    state['tareas']=tareas #Añadimos las tareas al estado del usuario
    return _metricas_to_dict(metricas_tarea) #Devolvemos las metricas para imprimirlas

def respuesta_ok(message:str,data:dict)->dict: #Formato estandar de respuesta correcta
    return{
        'status':'ok',
        'message':message,
        'data':data #Dentro de data es dónd variarán las keywords dependiendo de la funcionalidad del asistente
    }

def respuesta_error(message:str,errores:list[str])->dict: #Formato estandar de respuesta erronea
    return{
        'status':'error',
        'message':message,
        'data':{'errores':errores} #Lista de todos los errores recogidos durante las distintas validaciones
    }

def _metricas_to_dict(metricas:MetricasLlamada)->dict: #Convierte las metricas en diccionario para una mejor lectura e impresion
    return{
        'elapsed_ms':metricas.elapsed_ms,
        'prompt_tokens':metricas.prompt_tokens,
        'output_tokens':metricas.output_tokens,
        'total_tokens':metricas.total_tokens
    }


def crear_estado_demo(*,empleado:dict|None=None,dia:int|None=None) -> dict: #creamos el estado que se irá actualizando durante todo el uso del asistente
    if not empleado:
        return inicializar_estado( #Estado por defecto
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
    return inicializar_estado( #Estado a partir de datos proporcionados
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

def initialize_assistant(perfil:str)->dict: #Configutamos el asistente a partir del perfil del usuario
    config = deepcopy(ASSISTANT_CONFIG_DEFAULT)
    config["perfil_activo"] = perfil
    return config

def parsear_tareas(check:str)->list[dict]: #Convertir en json de las tareas asignadas en diccionario
    try:
        tareas=json.loads(check)
    except:
        raise ValueError ('Formato JSON respuesta inválido')
    for t in tareas:
        if not all(key in t for key in KEY_CHECK): #KEY_CHECK contiene la lista de keywords que debe tener una tarea
            raise ValueError ('Faltan keywords')
    return tareas

def procesar_turno( #El eje central del asistente conversacional
    *,
    state:dict,
    u_message:str,
)->dict:
    errores=valid_data(u_message,state) #Validamos que los datos cumplan con las especificaciones acordadas
    if errores: #Si una o más validaciones fallan
        return respuesta_error('Turno no procesado',errores=errores) #Devolvemos respuesta para imprimirla por terminal
    faqs=seleccion_faq(cargar_faq(DATA_DIR / 'faq_onboarding.json'),u_message) #Seleccionamos las faqs utiles según la pregunta del ususario
    docs=seleccion_doc(cargar_docs(DATA_DIR / 'onboarding_docs.json'),faqs=faqs,pregunta=u_message) #Seleccionamos los documentos a partir de las faqs y de la pregunta del usuario
    empresa=cargar_empresa(DATA_DIR / 'empresa.json')
    if docs:
        contacto=seleccion_escalado(empresa=empresa,doc=docs[0]) #Obtenemos el contacto a quien escalar la pregunta
    else:
        contacto=empresa['contactos'][DEFAULT_CONTACT] #Por defecto definimos un contacto para preguntas sin documentacion de soporte
    if state['user_profile']:
        config=initialize_assistant(state.get('user_profile').get('perfil','dev_junior')) #Personalizamos el asistente
    else:
        config=initialize_assistant('dev_junior') #Por defecto el asistente adopta el nivel de explicacion mas bajo
    prompt=build_assistant_prompt( #Generamos el prompt con todo lo necesario para una correcta respuesta del asistente
        assistant_config=config,
        user_state=state,
        user_message=u_message,
        extra_context={
            'faqs':faqs,
            'docs':docs
        },
    )
    try:
        texto,metricas=safe_generate(prompt,temperature=config['temperature']) #Llamamos al asistente
    except ValueError as e:
        return respuesta_error('Error al generar',[str(e)]) #De no ponder devolvemos el por qué para imprimirlo
    
    #Actualizamos el historial
    append_user(state, u_message) 
    append_assistant(state, texto)

    return respuesta_ok( #Devolvemos la respuesta de la API
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

def procesar_checklist( #Eje central del asistente de tareas
    *,
    state:dict,
    dia:int=1, #Por defecto nos encontramos en el dia 1
)->dict:
    errores=valid_check(state,dia=dia) #Validamos que los datos cumplan con las especificaiones
    if errores:
        return respuesta_error('Turno no procesado',errores=errores) #Si hay datos no validados imprimimos la razón
    state['user_profile']['dia']=dia #Actualizamos el dia en el estado
    comprobar_tareas(state=state,dia=dia) #Comporbamos que se hayan hecho las tareas anteriores
    tareas= [t for t in state.get('tareas') if not t.get('completada',False) and t.get('dia',1)<=dia] #Recogemos todas las tareas que no estan compleatadas y deberían estarlo
    prompt=prompt_resumen_tareas(tareas=tareas) #Creamos un prompt para un resumen personalizado de las tareas a realizar
    try:
        resumen,metricas=safe_generate(prompt=prompt) #Llamamos a la API
    except ValueError as e:
        return respuesta_error("Error de resumen", [str(e)]) #Devolvemos, en caso de error, la razon
    return respuesta_ok( #Devolvemos la lista de tareas en un formato preestablecido para una correcta impresión
        "Turno procesado",
        {
            "empleado": state.get('user_profile').get('nombre'),
            "dia": state.get('user_profile').get('dia'),
            "metricas": _metricas_to_dict(metricas),
            'tareas':tareas,
            'mensaje_resumen':resumen
        },
    )