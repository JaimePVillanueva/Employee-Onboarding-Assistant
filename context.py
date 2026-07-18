import json
import os

DATA_DIR = "data"

def cargar_json(nombre_archivo):
    """Carga un archivo JSON de la carpeta data y lo devuelve como objeto Python."""
    ruta = os.path.join(DATA_DIR, nombre_archivo)
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)

empresa = cargar_json("empresa.json")
empleados = cargar_json("empleados_demo.json")
onboarding_docs = cargar_json("onboarding_docs.json")
faq = cargar_json("faq_onboarding.json")

print("=== EMPRESA ===")
print(f"Nombre: {empresa['nombre']}")
print(f"Sector: {empresa['sector']}")
print(f"Departamentos: {len(empresa['departamentos'])}")

print("\n=== EMPLEADOS DEMO ===")
print(f"Total empleados: {len(empleados)}")
for emp in empleados:
    print(f"  - {emp['nombre']} ({emp['perfil']}) - {emp['rol']}")

print("\n=== DOCUMENTOS DE ONBOARDING ===")
print(f"Total documentos: {len(onboarding_docs)}")

print("\n=== FAQ ===")
print(f"Total preguntas frecuentes: {len(faq)}")