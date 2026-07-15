import json

def get_empleado(empleado_id):
    with open("data/empleados_demo.json", "r") as f:
        empleados =json.load(f)
    for x in empleados:
        if x["id"] == empleado_id:
            return x
    return None

def get_docs_por_departamento(departamento):
    with open("data/onboarding_docs.json", "r") as f:
        docs =json.load(f)
    resultado =[] 
    for x in docs:
        if x["departamento"] == departamento:
            resultado.append(x) 
    return resultado

def get_docs_por_keywords(pregunta):
    with open("data/onboarding_docs.json", "r") as f:
        docs= json.load(f)
    palabras= pregunta.lower().split()
    acumulador_tag = []
    for x in docs:
        if any(palabra in x["tags"] for palabra in palabras):
            acumulador_tag.append(x)
            return acumulador_tag

def get_contexto(empleado_id, dia, pregunta):
    empleado = get_empleado (empleado_id)
    departamento =empleado ["departamento"]
    docs_dpto =get_docs_por_departamento(departamento)
    docs_keywords = get_docs_por_keywords (pregunta)

    doc_dia_map= {
        "engineering": "doc_eng_01",
        "sales": "doc_sales_01",
        "operations" :"doc_ops_01"
    }
    doc_dia_id = doc_dia_map.get(departamento)
    doc_dia =next((d for d in docs_dpto if d["id"] == doc_dia_id), None)

    return {
        "empleado": empleado,
        "dia": dia,
        "doc_dia" : doc_dia,
        "docs_departamento" : docs_dpto,
        "docs_keywords" : docs_keywords
    }

if __name__ == "__main__":
    ctx =get_contexto("emp_01", 1, "Canales de Slack")
    print("===EMPLEADO===")
    print(ctx["empleado"])
    print("\n===DIA===")
    print(ctx["dia"])
    print("\n===DOC DEL DIA===")
    print(ctx["doc_dia"])
    print("\n===DOCS POR KEYWORDS===")
    for d in ctx["docs_keywords"]:
        print(f"-{d['id']}: {d['titulo']}")
