from config import DATA_DIR

from logic import (
    procesar_turno,
    crear_estado_demo,
    procesar_checklist,
    inicializar_checklist
    )

from context import (
    seleccion_empleado,
    cargar_empleados
    )

from validators import valid_id


def imprimir_resultado(respuesta:dict)->None:
    status=respuesta.get('status','unknown').upper()
    message=respuesta.get('message','')
    print(f'[{status}]')
    data=respuesta.get('data',{})
    if status=='ERROR':
        print(message)
        for e in data.get('errores',[]):
            print ('\n -',e)
        return
    print (f'''
{message}: {data.get('perfil','junior')}
{'='*60}

{data.get('respuesta','')}

Para más información contacta con {data.get('escalar')}

FAQs: {('\n -').join([f.get('pregunta','') for f in data.get('faqs',[])])}
Docs: {('\n -').join([d.get('titulo','') for d in data.get('docs',[])])}

Latencia: {data.get('metricas')['elapsed_ms']}
Tokens entrada: {data.get('metricas')['prompt_tokens']}
Tokens salida: {data.get('metricas')['output_tokens']}
''')

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
Nombre: {data.get('empleado')}    Día: {data.get('dia',0)}
{'-'*50}
{data.get('mensaje_resumen','')}
{'-'*50}
Tareas: 
    - {'\n    - '.join([x.get('titulo','') for x in data.get('tareas',[])])}

--- INICIO METRICAS MENSAJE RESUMEN ---

Latencia: {data.get('metricas')['elapsed_ms']}
Tokens entrada: {data.get('metricas')['prompt_tokens']}
Tokens salida: {data.get('metricas')['output_tokens']}

--- FIN METRICAS MENSAJE RESUMEN ---
''')
    
def demo_1() -> None:
    print("=" * 60)
    print("1) conversación de 1 turno (empleado tipo dev junior).")
    print("=" * 60)

    pregunta = "¿Cuál es el horario de entrada?"
    user_id='demo'
    error=valid_id(user_id)
    if error:
        raise ValueError(error)
    empleado=seleccion_empleado(cargar_empleados(DATA_DIR / 'empleados_demo.json'),user_id)
    state=crear_estado_demo(empleado=empleado)
    imprimir_resultado(procesar_turno(state=state,u_message=pregunta))

def demo_2()->None:
    print("=" * 60)
    print("2) creacion checklist.")
    print("=" * 60)
    user_id='emp_01'
    error=valid_id(user_id)
    if error:
        raise ValueError(error)
    empleado=seleccion_empleado(cargar_empleados(DATA_DIR / 'empleados_demo.json'),user_id)
    state=crear_estado_demo(empleado=empleado)
    metricas=inicializar_checklist(state=state)
    print (f'''
--- INICIO METRICAS ASIGNACION TAREAS ---

Latencia: {metricas['elapsed_ms']}
Tokens entrada: {metricas['prompt_tokens']}
Tokens salida: {metricas['output_tokens']}

--- FIN METRICAS ASGINACION TAREAS ---
''')
    imprimir_resultado_checklist(procesar_checklist(state=state))
    imprimir_resultado_checklist(procesar_checklist(state=state,dia=2))

def demo_3()->None:
    print("=" * 60)
    print("3) conversación de 1 turno (empleado tipo comercial vs remoto UE).")
    print("=" * 60)

    pregunta = "¿Cuál es el horario de entrada?"
    for user in ['emp_02','emp_03']:
        error=valid_id(user)
        if error:
            raise ValueError(error)
        empleado=seleccion_empleado(cargar_empleados(DATA_DIR / 'empleados_demo.json'),user)
        state=crear_estado_demo(empleado=empleado)
        imprimir_resultado(procesar_turno(state=state,u_message=pregunta))

def main()->None:
    demo_1()
    demo_2()
    demo_3()

if __name__ == '__main__':
    main()