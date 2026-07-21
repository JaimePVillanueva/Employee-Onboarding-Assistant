
CONTACTOS_DERIVACION = {
    "people" : "people@bridgesa.example",
    "it" : "it@bridgesa.example",
    "rrhh" : "rrhh@bridgesa.example",
    "engineering" : "engineering@bridgesa.example",
    "sales" : "sales@bridgesa.example",
    "operations" : "operations@bridgesa.example"

}
EMAIL_GENERAL = "onboarding@bridgesa.example"
# Diccionario que mapea departamentos a emails de contacto
# ¿Por qué un diccionario y no if/elif?
# Más facil de mantener y añadir de cara al futuro
def build_prompt_chat(contexto, pregunta, historial): # Conversacion libre
    # Respuesta en texto
    empleado = contexto["empleado"]
    doc_dia = contexto["doc_dia"]
    docs_keywords = contexto["docs_keywords"]
    departamento_relevante = contexto.get ("departamento_relevante")
    empresa = contexto["empresa"]
    
    # .get() es más seguro que. ["clave"]-devuelve None si no existe
    # En vez de lanzar un KeyError

    # Determinamos el email de derivacion segun el departamento relevante.
    # Si no hay departamento, usamos email general
    email_derivacion = CONTACTOS_DERIVACION.get(
        departamento_relevante, EMAIL_GENERAL
    ) if departamento_relevante else EMAIL_GENERAL

    # Construimos el texto de los docs relevantes por keywords.
    # Los concatenamos con un separador "---" para que el LLM
    # pueda distinguir donde empieza y termina el documento
    docs_texto = ""
    for doc in docs_keywords:
        docs_texto += f"\n---\n{doc['titulo']}\n{doc['cuerpo']}"

    valores_texto ="\n".join(f" -{v}" for v in empresa["valores"])

    system = f"""Eres el asistente de onboarding de Bridge SA.
Ayudas a empleados nuevos en sus primeros días. Responde solo con información
de la documentación proporcionada.

<empresa>
Mision: {empresa['mision']}
Valores:
{valores_texto}
</empresa>
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
- Si la pregunta tiene documentación relevante en el departamento "{departamento_relevante or 'general'} -> derivar a {email_derivacion} 
- Si no hay departamento relevante identificado -> derivar a {EMAIL_GENERAL}
- Consultas de participantes externos -> No atender, solo empleados con contrato laboral
</reglas_derivacion>
"""
    # Construimos la lista de mensajes en el formato que espera el LLM
    mensajes = [{"role": "system", "content": system}]
    # Añadimos el historial de turnos anteriores.
    # Cada turno tiene una pregunta (user) y una pregunta (assistant)
    # ¿Por qué dos append por turno?
    # Porque cada mensaje del historial son dos mensajes separados:
    # uno del user y otro del assistant
    for turno in historial:
        mensajes.append({"role": "user", "content": turno["pregunta"]})
        mensajes.append({"role": "assistant", "content": turno["respuesta"]})
    # La pegunta actual va siempre al final - es lo mas reciente
    # El LLM lee en orden, asi que lo ultimo que lee es lo que debe responder
    mensajes.append({"role": "user", "content": pregunta})

    return "\n".join(f"{m['content']}: {m['content']}" for m in mensajes)


def build_prompt_checklist(contexto, tareas_pendientes = None): # Para generar el plan del dia (JSON)
   # Este prompt es diferente al del chat:
   # - No hay historial (es una generación automatica, no una conversacion)
   # - Le pedimos un JSON explicitamente
   # - Incluye recordatorio de tareas pendientes del dia anterior si las hay
    empleado = contexto["empleado"]
    doc_dia = contexto["doc_dia"]

    # Construimos el recordatorio de tareas pendientes si las hay
    # Si no hay pendientes, el string queda vacio y no aparece en el prompt
    recordatorio = ""
    if tareas_pendientes:
        titulos = "\n".join(f"- {t['titulo']}" for t in tareas_pendientes)
        recordatorio = """
<tareas_pendientes_dia_anterior>
Estas tareas del dia anterior quedaron sin completar:
{titulos}
< /tareas_pendientes_dia_anterior>
"""

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