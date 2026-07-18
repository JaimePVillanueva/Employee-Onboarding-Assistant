from copy import deepcopy
from config import ASSISTANT_CONFIG_DEFAULT,DATA_DIR
from logic import (procesar_turno,crear_estado_demo)
from context import (seleccion_empleado,cargar_empleados)


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
''')
    
def demo_perfiles() -> None:
    print("=" * 60)
    print("1) conversación de 1 turno (empleado tipo dev junior).")
    print("=" * 60)

    pregunta = "¿Cuál es el horario de entrada?"
    user_id='emp_01'
    empleado=seleccion_empleado(cargar_empleados(DATA_DIR / 'empleados_demo.json'),user_id)
    state=crear_estado_demo(empleado=empleado)
    imprimir_resultado(procesar_turno(state=state,u_message=pregunta))

def main()->None:
    demo_perfiles()

if __name__ == '__main__':
    main()