def imprimir_resultado(respuesta:dict)->None:
    status=respuesta.get('status','unknown').upper()
    message=respuesta.get('message','')
    print(f'[{status}] {message}\n{'='*60}\n')
    data=respuesta.get('data',{})
    if status=='ERROR':
        for e in data.get('errores',[]):
            print (' -',e)
        return
    print (f'P: {data.get('question','')}\nR: {data.get('answer','')}\nFAQs: {data.get('faqs',[])}')

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