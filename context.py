import json
import os

def get_empresa():
    with open("data/empresa.json", "r") as f:
        return json.load(f)
#--- Función 1: get_empleado---
# Recibe el ID del empleado y devuelve su ficha completa en JSON.
# ¿Por qué una función separada? La lógica se reutiliza en varios lugares.

def get_empleado(empleado_id):
    with open("data/empleados_demo.json", "r") as f:
        empleados =json.load(f)
    for x in empleados:
        if x["id"] == empleado_id:
            return x
    return None

#--- Función 2: get_docs_por_departamento---
# Devuelve todos los documentos ordenados por importancia.
# El departamento propio del empleado va primero, luego people, it, etc.
# ¿Por qué este orden? PAra que el LLM priorice lo mas relevante


def get_docs_por_departamento(departamento):
    with open("data/onboarding_docs.json", "r") as f:
        docs =json.load(f)
        #Orden de importancia: Primero el departamento del empleado.
        #Luego los genericos que aplican a todos.
    orden = [departamento, "people", "it", "engineering", "sales", "operations"]
    resultado =[] 
    ids_añadidos = set () # Set para evitar duplicados (cada doc aparece una sola vez)
    for dpt in orden:
        # Buscamos todos los docs de ese departamento
        for x in docs:
            if x["departamento"] == departamento and x["id"] not in ids_añadidos:
                resultado.append(x)
                ids_añadidos.add(x["id"]) # Marcamos como añadido.
    return resultado

#--- Función 3: get_docs_por_keywords---
# Buscamos documentos cuyos "tags" coincidan con palabras de la pregunta.
# ¿Por qué? Porque no queremos mandar TODOS los docs al LLM en cada pregunta.
# Eso sería caro y lento. Solo mandamos los relevantes.
def get_docs_por_keywords(pregunta):
    with open("data/onboarding_docs.json", "r") as f:
        docs= json.load(f)
    palabras= pregunta.lower().split()
    acumulador_tag = []
    for x in docs:
        if any(palabra in x["tags"] for palabra in palabras):
            acumulador_tag.append(x)
    return acumulador_tag

#--- Función 4: get_departamento_relevante---
# DEvuelve el pdeparta,emtp deñ primer doc encontrado por keywords.
# ¿Por qué el primero? Porque es el más relevante para la pregunta.
# Este dato lo usará prompts.py para saber a quién derivar.
def get_departamento_relevante(docs_keywords):
    if not docs_keywords:
        return None
    return docs_keywords[0]["departamento"]

#---Función 5: get_contexto---
# Función principal del módulo. Une todo lo anterior en un solo diccionario.
# Este diccionario es lo que recibe promppts.py para construir el prompt.
def get_contexto(empleado_id, dia, pregunta):
    empleado = get_empleado (empleado_id)
    departamento =empleado ["departamento"]
    docs_dpto =get_docs_por_departamento(departamento)
    docs_keywords = get_docs_por_keywords (pregunta)
    departamento_relevante = get_departamento_relevante(docs_keywords)
    empresa= get_empresa()

# Mapeamos cada departamento al ID de su doc de primeros 5 días.
# Usamos un diccionario en vez de if/elif por limpieza y extensión.
    doc_dia_map= {
        "engineering": "doc_eng_01",
        "sales": "doc_sales_01",
        "operations" :"doc_ops_01"
    }
    doc_dia_id = doc_dia_map.get(departamento)
    doc_dia =next((d for d in docs_dpto if d["id"] == doc_dia_id), None)
    # next() recorre la lista y devuelve el primero que cumple la condicion.
    # El segundo argumento (None) es el valor por defecto si no encuentra nada.

    return {
        "empleado": empleado,
        "dia": dia,
        "doc_dia" : doc_dia,
        "docs_departamento" : docs_dpto,
        "docs_keywords" : docs_keywords,
        "departamento_relevante" : departamento_relevante,
        "empresa" : empresa
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
