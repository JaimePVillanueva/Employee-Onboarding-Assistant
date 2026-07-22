from google import genai
from asistente import configurar_api

configurar_api()
cliente = genai.Client()

print("Modelos disponibles con tu API key:")
for modelo in cliente.models.list():
    # Solo los que sirven para generar contenido
    if "generateContent" in modelo.supported_actions:
        print(" -", modelo.name)