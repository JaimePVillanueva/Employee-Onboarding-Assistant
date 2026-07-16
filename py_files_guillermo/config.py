MODEL = "gemini-3-flash-preview"
TEMPERATURE = 0.3
TEMPERATURE_VULNERABLE = 0.3
MAX_INPUT_TOKENS=8_000
MAX_INPUT_CHARS=2_000
WINDOW=4
DOCS=3
FAQS=2

PERFILES={
    'dev_junior':{
        'rol':(
            'Eres el enlace entre los nuevos miembros y la empresa. '
            'Respondes con un tono didactico y cercano'
        ),
        'nivel_explicacion':'basico'
    },
    'comercial':{
        'rol':(
            'Eres un asistente para el departamento de ventas'
            'Respondes con un tono menos tecnico y focalizado en herramientas comerciales'
        ),
        'nivel_explicacion':'intermedio'
    },
    'remoto_eu':{
        'rol':(
            'Eres un asistente para empleados trabajando en remoto inetrnacinalmente'
            'Respondes sobre politicas cross-border y con un tono profesional'
        ),
        'nivel_explicacion':'avanzado'
    }
}

ASSISTANT_CONFIG_DEFAULT = {
    "model": MODEL,
    "temperature": TEMPERATURE,
    "perfil_activo": "mentor",
    "max_turnos_historial": WINDOW,
    "idioma_respuesta": "español",
    "max_palabras": 200,
}

# JSON_SCHEMA_CHECKLIST = '''
# Devuelve SOLO un JSON con estas claves:
# - 'empleado_id':
# - 'dia':
# - 'tareas':
# - 'mensaje_resumen':
# '''