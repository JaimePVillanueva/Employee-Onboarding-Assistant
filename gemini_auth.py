import os
import getpass

from dotenv import load_dotenv

_configured = False ## Declara la variable de configuración y la inicializa en falso


def configurar_gemini_api_key() -> None: ## Función para configurar la API key, la función no devuelve nada
    global _configured 
    if _configured: ## Si la variable _configured es True, termina la función
        return

    load_dotenv() ## Saca los datos de .env

    if not os.getenv("GEMINI_API_KEY"): ## Si en .env no hay nada en GEMINI_API_KEY
        os.environ["GEMINI_API_KEY"] = getpass.getpass(
            "Pega aquí tu GEMINI_API_KEY (input oculto): " ## Te la pide y la introduce en .env
        )

    print(
        "GEMINI_API_KEY configurada:",
        "sí" if os.getenv("GEMINI_API_KEY") else "no",
    )
    _configured = True ## Finalmente establece _configured a True si se llega a este punto