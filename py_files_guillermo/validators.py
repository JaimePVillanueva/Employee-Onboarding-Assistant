from config import (
    PATRONES_SOSPECHOSOS,
    DATA_DIR,
    MAX_INPUT_CHARS,
    DOM_KEY
    )
from context import lista_empleados

def valid_data(message:str,id:str)->list[str]:
    errores=[]
    if not message.strip():
        return ['No hay mensaje']
    m=message.lower()
    if not id.strip():
        return ['Hace falta un id de empleado']
    if id not in lista_empleados(DATA_DIR / 'empleados_demo.json') and id!='demo':
        errores.append('Id de usuario no reconocido')
    if len(m)>MAX_INPUT_CHARS:
        errores.append(f'El mensaje excede el máximo de caracteres {len(m)}/{MAX_INPUT_CHARS}')
    if any(p in m for p in PATRONES_SOSPECHOSOS):
        errores.append('Mensaje peligroso')
    return errores