import json
from pathlib import Path
from config import (DOCS,FAQS,DEFAULT_CONTACT)

def cargar_empleados(ruta:Path)->list[dict]:
    with ruta.open(encoding='utf-8') as e:
        data=json.load(e)
    if not isinstance(data,list):
        raise ValueError ('empleados_demo.json debe ser una lista')
    return data

def cargar_faq(ruta:Path)->list[dict]:
    with ruta.open(encoding='utf-8') as f:
        data=json.load(f)
    if not isinstance(data,list):
        raise ValueError ('empleados_demo.json debe ser una lista')
    return data

def cargar_docs(ruta:Path)->list[dict]:
    with ruta.open(encoding='utf-8') as d:
        data=json.load(d)
    if not isinstance(data,list):
        raise ValueError ('empleados_demo.json debe ser una lista')
    return data

def cargar_empresa(ruta:Path)->dict:
    with ruta.open(encoding='utf-8') as d:
        data=json.load(d)
    if not isinstance(data,dict):
        raise ValueError ('empresa.json debe ser una lista')
    return data

def seleccion_faq(faqs:list[dict],pregunta:str,max_faq:int = FAQS)-> list[dict]:
    quest=pregunta.strip().lower()
    orden:list[tuple[int,dict]]=[]
    for f in faqs:
        score=0
        for t in f.get('tags',[]):
            if t.lower() in quest:
                score+=2
        if f.get('pregunta','').strip().lower() in quest:
            score+=3
        if score>0:
            orden.append((score,f))
    orden.sort(key=lambda x: x[0],reverse=True)
    return [o[1] for o in orden[:max_faq]]

def seleccion_doc(docs:list[dict],*,faqs:list[dict] | None=None,pregunta:str,max_doc:int = DOCS)-> list[dict]:
    quest=pregunta.strip().lower()
    orden:list[tuple[int,dict]]=[]
    faq_doc_list=[]
    if faqs:
        for f in faqs:
            ref=f.get('doc_id')
            if ref not in faq_doc_list:
                faq_doc_list.append(ref)
    for d in docs:
        score=0
        if d.get('id') in faq_doc_list:
            score=7
        else:
            for t in d.get('tags',[]):
                if t.lower() in quest:
                    score+=2
            if d.get('titulo','').strip().lower() in quest:
                score+=3
        if score>0:
            orden.append((score,d))
    orden.sort(key=lambda x: x[0],reverse=True)
    return [o[1] for o in orden[:max_doc]]

def seleccion_empleado(emps:list[dict],emp_id:str)->dict|None:
    for e in emps:
        if e.get('id')==emp_id:
            return e
def seleccion_escalado(*,empresa:dict,doc:dict)->str:
    contact=empresa.get('contactos',{})
    contact_importance=dict.fromkeys(contact,0)
    for k in contact_importance:
        if contact.get(k) in doc['cuerpo'].lower():
            return contact.get(k)
        if k==DEFAULT_CONTACT:
            continue
        if (
            any(c in k for c in doc['cuerpo'].lower())
            or any (t in k for t in doc['tags'].lower())
            or any (t in k for t in doc['titulo'].lower())
            or k in doc['id'].lower()
            or k==doc['departamento'].lower()
            ):
            return contact.get(k)
    return  contact.get(DEFAULT_CONTACT)
def lista_empleados(ruta:Path)->list[str]:
    empleados=cargar_empleados(ruta=ruta)
    return [e.get('id') for e in empleados]