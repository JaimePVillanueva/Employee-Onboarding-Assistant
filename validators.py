from config import (
    PATRONES_SOSPECHOSOS,
    DATA_DIR,
    MAX_INPUT_CHARS,
    DOM_KEY
    )
from context import lista_empleados

def valid_id(id:str)->list[str]:
    """valida el id de empleado"""
    if not id.strip():
        return 'Hace falta un id de empleado'
    if id not in lista_empleados(DATA_DIR / 'empleados_demo.json') and id!='demo': #Usamos demo para el perfil de prueba dev_junior
        return 'Id de usuario no reconocido'
    
def valid_state(state:dict)->list[str]:
    """valida el estado"""
    errores=[]
    if not state:
        return['No hay estado']
    if not isinstance(state,dict):
        errores.append('Estado debe ser un diccionario')
    return errores

def valid_data(message:str,state:dict)->list[str]:
    """Valida mensaje y estado
    
    Para validar estado llama a valid_state(state)"""
    errores=[]
    if not message.strip():
        return ['No hay mensaje']
    m=message.lower()
    errores.extend(valid_state(state=state))
    if len(m)>MAX_INPUT_CHARS: #Evitamos mensajes demasiado largos
        errores.append(f'El mensaje excede el máximo de caracteres {len(m)}/{MAX_INPUT_CHARS}') 
    if any(p in m for p in PATRONES_SOSPECHOSOS): #comprobamos que el mensaje no incluya patrones sospechosos de prompt inyection
        errores.append('Mensaje peligroso')
    return errores

def valid_check(state:dict,dia:int)->list[str]:
    """Valida estado y dia
    
    Para validar estado llama a valid_state(state)"""
    errores=[]
    errores.extend(valid_state(state=state))
    if not isinstance(dia,int):
        errores.append('Dia debe ser un entero')
    elif dia>5 or dia<1:
        errores.append('Dia deve estar entre 1 y 5')