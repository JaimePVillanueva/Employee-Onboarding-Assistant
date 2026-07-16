from copy import deepcopy
from pathlib import Path
from config import ASSISTANT_CONFIG_DEFAULT
from logic import (crear_estado_demo, procesar_turno)

DATA_DIR = Path(__file__).parent.parent / "data"

def imprimir_resultado(respuesta:dict)->None:
    status=respuesta.get('status','unknown').upper()
    message=respuesta.get('message','')
    print(f'[{status}] {message}')
    data=respuesta.get('data',{})
    if status=='ERROR':
        for e in data.get('errores',[]):
            print ('\n -',e)
        return
    print (f': {data.get('perfil','junior')}\n{'='*60}\nR: {data.get('respuesta','')}\nFAQs: {data.get('faqs',[])}\nDocs: {data.get('docs',[])}')

def imprimir_resultado_checklist(respuesta:dict)->None:
    status=respuesta.get('status','unknown').upper()
    message=respuesta.get('message','')
    print(f'[{status}] {message}\n')
    data=respuesta.get('data',{})
    if status=='ERROR':
        for e in data.get('errores',[]):
            print (' -',e)
        return
    print (f'''
Nombre: {data.get('empleado').get('nombre')}    Día: {data.get('dia',0)}
{'-'*50}
{data.get('mensaje_resumen','')}
{'-'*50}
Tareas: 
    - {'\n    - '.join([x.get('titulo','') for x in data.get('tareas',[])])}
''')
    
def demo_perfiles() -> None:
    print("=" * 60)
    print("1) Misma pregunta, distinto perfil del asistente")
    print("=" * 60)

    pregunta = "¿Qué es un asistente conversacional con LLM?"
    for perfil in ("dev_junior", "comercial", "remoto_eu"):
        config = deepcopy(ASSISTANT_CONFIG_DEFAULT)
        config["perfil_activo"] = perfil
        state = crear_estado_demo()
        imprimir_resultado(procesar_turno(state, pregunta, assistant_config=config))