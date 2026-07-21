from pathlib import Path

MODELS = [
    "gemini-3.1-flash-lite",
]

TEMPERATURE = 0.2 ## Establecemos la temperatura a 0.2 como aconseja el enunciado
TEMPERATURE_VULNERABLE = 0.2 ## También la establecemos a 0.2, más adelante se puede cambiar para observar comportamiento
WINDOW = 4
MAX_TOKENS_INPUT = 8_000
MAX_INPUT_CHARS = 2_000

DATA_DIR = Path(__file__).parent / "data" ## Entra en la carpeta data
PREGUNTAS_PATH = DATA_DIR / "faq_onboarding.json" ## Entra en el archivo faq_onboarding.json

OUTPUT_DIR = Path(__file__).parent / "output" ## Entra en la carpeta output
ENTREGABLES_DIR = Path(__file__).parent / "benchmark" ## Entra en la carpeta entregables
DIAS_DIR = Path(__file__).parent / "dias" ## Entra en la carpeta dias

MIN_PREGUNTAS = 0