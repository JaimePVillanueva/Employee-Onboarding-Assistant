from config import (
    PATRONES_SOSPECHOSOS,
    DATA_DIR,
    MAX_INPUT_CHARS,
    DOM_KEY
    )
from context import lista_empleados

def valid_id(id:str)->list[str]:
    if not id.strip():
        return 'Hace falta un id de empleado'
    if id not in lista_empleados(DATA_DIR / 'empleados_demo.json') and id!='demo':
        return 'Id de usuario no reconocido'
    
def valid_state(state:dict)->list[str]:
    errores=[]
    if not state:
        return['No hay estado']
    if not isinstance(state,dict):
        errores.append('Estado debe ser un diccionario')
    return errores

def valid_data(message:str,state:dict)->list[str]:
    errores=[]
    if not message.strip():
        return ['No hay mensaje']
    m=message.lower()
    errores.extend(valid_state(state=state))
    if len(m)>MAX_INPUT_CHARS:
        errores.append(f'El mensaje excede el máximo de caracteres {len(m)}/{MAX_INPUT_CHARS}')
    if any(p in m for p in PATRONES_SOSPECHOSOS):
        errores.append('Mensaje peligroso')
    return errores

def valid_check(state:dict,dia:int)->list[str]:
    errores=[]
    errores.extend(valid_state(state=state))
    if not isinstance(dia,int):
        errores.append('Dia debe ser un entero')
    elif dia>5 or dia<1:
        errores.append('Dia deve estar entre 1 y 5')