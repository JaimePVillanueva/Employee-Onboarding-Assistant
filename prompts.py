from config import WINDOW ## Importamos WINDOW



def build_prompt_chat(contexto, pregunta, historial, assitant_config):
    empleado = contexto["empleado"]
    doc_dia = contexto["doc_dia"]
    docs_keywords = contexto["docs_keywords"]

    docs_texto = ""
    for doc in docs_keywords:
        docs_texto += f"\n---\n{doc['titulo']}\n{doc['cuerpo']}"

    system = f"""Eres el asistente de onboarding de Bridge SA.
Ayudas a empleados nuevos en sus primeros días. Responde solo con información
de la documentación proporcionada.

<empleado>
Nombre: {empleado['nombre']}
Rol: {empleado['rol']}
Departamento: {empleado['departamento']}
Día de onboarding: {contexto['dia']}
Modalidad: {empleado['modalidad']}
</empleado>

<docs>
{doc_dia['cuerpo']}
{docs_texto}
</docs>

<reglas_derivacion>
- Salario, bonus o equity → no responder, derivar a manager o People en 1:1
- Problemas con portátil, accesos o software → derivar a it@bridgesa.example
- Bajas médicas, vacaciones, excedencias → derivar a rrhh@bridgesa.example
- Acoso o problemas de conducta → derivar a people@bridgesa.example
- Dudas de onboarding no resueltas → derivar a onboarding@bridgesa.example
- Consultas de participantes externos → no atender, solo empleados con contrato laboral
</reglas_derivacion>
"""

    mensajes = [{"role": "system", "content": system}]

    for turno in historial:
        mensajes.append({"role": "user", "content": turno["pregunta"]})
        mensajes.append({"role": "assistant", "content": turno["respuesta"]})

    mensajes.append({"role": "user", "content": pregunta})

    return mensajes


def build_prompt_checklist(contexto):
    empleado = contexto["empleado"]
    doc_dia = contexto["doc_dia"]

    system = f"""Eres el asistente de onboarding de Bridge SA.
Devuelve ÚNICAMENTE un JSON válido con las tareas del día, sin texto adicional.

<empleado>
Nombre: {empleado['nombre']}
Rol: {empleado['rol']}
Departamento: {empleado['departamento']}
Día de onboarding: {contexto['dia']}
</empleado>

<docs>
{doc_dia['cuerpo']}
</docs>

Devuelve el JSON con esta estructura exacta:
{{
    "empleado_id": "{empleado['id']}",
    "dia": {contexto['dia']},
    "tareas": [
        {{
            "id": "t01",
            "titulo": "tarea concreta",
            "completada": false,
            "fuente_doc": "{doc_dia['id']}"
        }}
    ],
    "mensaje_resumen": "frase corta de orientación"
}}
"""

    return system




def actualizar_historial(historial, pregunta, respuesta):
    if len(historial) >= WINDOW:
        return historial, False
    historial.append({"pregunta": pregunta, "respuesta": respuesta})
    return historial, True