# ============================================
# CARGA Y SELECCIÓN DE DATOS
# ============================================

import json
from config import DATA_DIR, MAX_DOCS, MAX_FAQS, CONTACTOS


# --- Función genérica para cargar cualquier JSON ---
def cargar_json(nombre_archivo):
    """Abre un archivo JSON de la carpeta data y lo devuelve como objeto Python."""
    ruta = DATA_DIR / nombre_archivo
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)


# --- Cargamos cada archivo con su función clara ---
def cargar_empleados():
    return cargar_json("empleados_demo.json")

def cargar_faqs():
    return cargar_json("faq_onboarding.json")

def cargar_docs():
    return cargar_json("onboarding_docs.json")

def cargar_empresa():
    return cargar_json("empresa.json")


# --- Buscar un empleado por su id ---
def buscar_empleado(emp_id):
    """Devuelve el empleado con ese id, o None si no existe."""
    for emp in cargar_empleados():
        if emp["id"] == emp_id:
            return emp
    return None


# --- Seleccionar las FAQs relevantes a una pregunta ---
def seleccionar_faqs(pregunta):
    """Devuelve las FAQs más relacionadas con la pregunta (máximo MAX_FAQS)."""
    pregunta = pregunta.lower()
    relevantes = []

    for faq in cargar_faqs():
        puntos = 0
        # Sumamos puntos si algún tag aparece en la pregunta
        for tag in faq.get("tags", []):
            if tag.lower() in pregunta:
                puntos += 1
        # Guardamos la FAQ si tiene algún punto
        if puntos > 0:
            relevantes.append((puntos, faq))

    # Ordenamos de más a menos relevante y devolvemos las mejores
    relevantes.sort(key=lambda x: x[0], reverse=True)
    return [faq for puntos, faq in relevantes[:MAX_FAQS]]


# --- Seleccionar los documentos relevantes ---
def seleccionar_docs(pregunta, faqs_elegidas):
    """Devuelve los documentos más relevantes (máximo MAX_DOCS)."""
    pregunta = pregunta.lower()

    # Ids de documentos que ya referencian las FAQs elegidas
    docs_de_faqs = [faq.get("doc_id") for faq in faqs_elegidas]

    relevantes = []
    for doc in cargar_docs():
        puntos = 0
        # Prioridad alta si el doc está referenciado por una FAQ elegida
        if doc["id"] in docs_de_faqs:
            puntos = 5
        else:
            # Si no, puntuamos por tags
            for tag in doc.get("tags", []):
                if tag.lower() in pregunta:
                    puntos += 1
        if puntos > 0:
            relevantes.append((puntos, doc))

    relevantes.sort(key=lambda x: x[0], reverse=True)
    return [doc for puntos, doc in relevantes[:MAX_DOCS]]


# --- Decidir a quién derivar según el departamento del documento ---
def decidir_escalado(docs):
    """Mira el departamento del primer documento y devuelve el contacto adecuado."""
    if not docs:
        return CONTACTOS["onboarding"]  # por defecto

    departamento = docs[0].get("departamento", "")
    # Buscamos el contacto de ese departamento, o el de onboarding por defecto
    return CONTACTOS.get(departamento, CONTACTOS["onboarding"])