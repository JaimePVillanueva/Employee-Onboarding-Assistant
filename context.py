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
    """Seleccion de faqs relevantes
        
        Parámteros:
        - faqs: lista de todas las faqs
        - pregunta: pregunta del usuario
        - max_faq: número máximo de faqs a seleccionar"""
    quest=pregunta.strip().lower() #Limpiamos la pregunta para que sea más fácil comparar
    orden:list[tuple[int,dict]]=[] #Creamos la lista para ordenar las faqs segun importancia
    for f in faqs:
        score=0 #score representa el grado de importancia
        for t in f.get('tags',[]): #primero comprobamos si alguno de los tags de la faq se encuentra en la pregunta
            if t.lower() in quest:
                score+=2 #se le asigna un nivel intermedio de importancia
        if f.get('pregunta','').strip().lower() in quest: #Comprobamos si la pregunta tiene coincidencia directa con algún faq
            score+=3 #se le asigna un nivel alto de importancia
        if score>0: #Seleccionamos solo aquellas que tengan alguna relevancia para la pregunta
            orden.append((score,f))
    orden.sort(key=lambda x: x[0],reverse=True) #Las ordenamos según importancia
    return [o[1] for o in orden[:max_faq]] #devolvemos solo la faq (el nivel de importancia ya no interesa)

def seleccion_doc(docs:list[dict],*,faqs:list[dict] | None=None,pregunta:str,max_doc:int = DOCS)-> list[dict]:
    """Seleccion de documentos relevantes
    
    Parámteros:
    - docs: lista de todos los documentos
    - faqs: lista de faqs de relevancia para la pregunta
    - max_doc: número máximo de documentos a seleccionar"""
    quest=pregunta.strip().lower() #Limpiamos la pregunta para que sea más fácil comparar
    orden:list[tuple[int,dict]]=[] #Creamos la lista para ordenar las faqs segun importancia
    faq_doc_list=[] #Creamos una lista con los documentos utilizados para las faqs seleccionadas previamente
    if faqs:

        #Añadimos los id del documento evitando duplicados (varios faqs hacen referencia al mismo documento)
        for f in faqs:
            ref=f.get('doc_id')
            if ref not in faq_doc_list:
                faq_doc_list.append(ref)
    #Empezamos clasificación 
    for d in docs:
        score=0
        if d.get('id') in faq_doc_list: #Máxima importancia a los documentos que son utilizados en los faqs seleccionados
            score=7 

        #Misma idea que con los faqs pero comparando con titulo en vez de con pregunta
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
    """Devuelve el diccionario del empleado según su id"""
    for e in emps:
        if e.get('id')==emp_id:
            return e
def seleccion_escalado(*, empresa: dict, doc: dict) -> str:
    """Seleccionar departamento a escalar en funcion del documento"""
    contact = empresa.get('contactos', {}) #Obtenemos todos los contactos de la empresa

    #Limpiamos los datos proporcionados
    cuerpo = doc['cuerpo'].lower().strip()
    id_doc = doc['id'].lower().strip()
    departamento = doc['departamento'].lower().strip()
    titulo = doc['titulo'].lower().strip()
    tags = [t.lower().strip() for t in doc['tags']] if isinstance(doc['tags'], list) else [] #como tags es una lista hay que acceder a cada dato individiualmente
    for k in contact: #Comporbamos para cada contacto
        k_clean = k.lower().strip() #limpuamos nombre de contacto
        if contact.get(k) in cuerpo: #Antes que nada miramos si el documento nos indica el correo al que escalar
            return contact.get(k) #De ser así devolvemos ese correo sin cuestionar nada más
        if k == DEFAULT_CONTACT: #Saltamos comprobaciones del contacto por defecto ya que a ese siempre se escala si no hay nadie más al que acudir
            continue
        if ( #Comprobamos en todos los sitios del documento si se hace referencia al contacto
            k_clean in cuerpo  
            or k_clean in tags
            or k_clean in titulo
            or k_clean in id_doc
            or k_clean == departamento
        ):
            return contact.get(k) #En cuento haya una referencia devolvemos el correo para ahorrar cálculos inecesarios
            
    return contact.get(DEFAULT_CONTACT) #Como ya dijimos, si no hay coincidencias devolvemos el correo de contacto por defecto
def lista_empleados(ruta:Path)->list[str]:
    """Devuelve una lista con los id de los empleados"""
    empleados=cargar_empleados(ruta=ruta)
    return [e.get('id') for e in empleados]