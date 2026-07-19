import json


def get_empleado(empleado_id) -> str: ## Devuelve el Id de empleado, buscando por el número de orden de empleados de la lista
    with open("data/empleados_demo.json", "r", encoding="utf-8") as f:
        empleados = json.load(f)
    for emp_id in empleados:
        if emp_id["id"] == empleado_id:
            return emp_id
    return None


def get_docs_por_departamento(departamento) -> list: ## 
    with open("data/onboarding_docs.json", "r", encoding="utf-8") as f:
        docs = json.load(f)
    resultado = []
    for doc in docs:
        if doc["departamento"] == departamento:
            resultado.append(doc)
    return resultado


def get_docs_por_keywords(pregunta) -> list:
    with open("data/onboarding_docs.json", "r", encoding="utf-8") as f:
        docs = json.load(f)
    palabras = pregunta.lower().split()
    acumulador_tag = []
    for doc in docs:
        if any(palabra in doc["tags"] for palabra in palabras):
            acumulador_tag.append(doc)
    return acumulador_tag

def get_faq_por_tag(pregunta) -> list:
    with open("data/faq_onboarding.json", "r", encoding="utf-8") as pregs:
        preguntas = json.load(pregs)
    palabras_pregunta = pregunta.lower().split()
    guardar_pregunta = []
    for preg in preguntas:
        if any(palabra in preg["tags"] for palabra in palabras_pregunta):
            guardar_pregunta.append(preg)
    return guardar_pregunta

def get_contexto(empleado_id, dia, pregunta) -> dict:
    empleado = get_empleado(empleado_id)
    departamento = empleado["departamento"]
    docs_dpto = get_docs_por_departamento(departamento)
    docs_keywords = get_docs_por_keywords(pregunta)

    doc_dia_map = {
        "engineering": "doc_eng_01",
        "sales": "doc_sales_01",
        "operations": "doc_ops_01"
    }
    doc_dia_id = doc_dia_map.get(departamento)
    doc_dia = next((d for d in docs_dpto if d["id"] == doc_dia_id), None)

    return {
        "empleado": empleado,
        "dia": dia,
        "doc_dia": doc_dia,
        "docs_departamento": docs_dpto,
        "docs_keywords": docs_keywords
    }