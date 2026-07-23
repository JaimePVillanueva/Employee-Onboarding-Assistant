from config import (
    PATRONES_SOSPECHOSOS,
    DATA_DIR,
    MAX_INPUT_CHARS,
    DOM_KEY,
    ENTREGABLES_DIR,
    MIN_PREGUNTAS,
    PREGUNTAS_PATH
    )
from context import lista_empleados
import re
import json

def valid_id(id:str)->list[str]:
    """valida el id de empleado"""
    if not id.strip():
        return 'Hace falta un id de empleado'
    if id not in lista_empleados(DATA_DIR / 'empleados_demo.json') and id!='demo': #Usamos demo para el perfil de prueba dev_junior
        return 'Id de usuario no reconocido'
    
def valid_state(state:dict)->list[str]:
    """valida el estado"""
    errores=[]
    if not state:
        return['No hay estado']
    if not isinstance(state,dict):
        errores.append('Estado debe ser un diccionario')
    return errores

def valid_data(message:str,state:dict)->list[str]:
    """Valida mensaje y estado
    
    Para validar estado llama a valid_state(state)"""
    errores=[]
    if not message.strip():
        return ['No hay mensaje']
    m=message.lower()
    errores.extend(valid_state(state=state))
    if len(m)>MAX_INPUT_CHARS: #Evitamos mensajes demasiado largos
        errores.append(f'El mensaje excede el máximo de caracteres {len(m)}/{MAX_INPUT_CHARS}') 
    if any(p in m for p in PATRONES_SOSPECHOSOS): #comprobamos que el mensaje no incluya patrones sospechosos de prompt inyection
        errores.append('Mensaje peligroso')
    return errores

def valid_check(state:dict,dia:int)->list[str]:
    """Valida estado y dia
    
    Para validar estado llama a valid_state(state)"""
    errores=[]
    errores.extend(valid_state(state=state))
    if not isinstance(dia,int):
        errores.append('Dia debe ser un entero')
    elif dia>5 or dia<1:
        errores.append('Dia deve estar entre 1 y 5')

_IDS_RESERVADOS = {"ejemplo_solo_formato"}
_MARCADOR_TODO = re.compile(r"\bTODO\b", re.IGNORECASE)


def _tiene_marcador_todo(texto: str) -> bool: ## Si en _MARCADOR_TODO no está texto (la variable de entrada) entonces devuelve False si sí está entonces devuelve True.
    return bool(_MARCADOR_TODO.search(texto))


def verificar_preguntas_json() -> tuple[bool, list[str]]:
    """Devuelve (ok, lista_de_errores)."""
    errores: list[str] = []

    if not PREGUNTAS_PATH.is_file():
        return False, [f"No existe {PREGUNTAS_PATH.name}"]

    try:
        preguntas = json.loads(PREGUNTAS_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return False, [f"JSON inválido en preguntas.json: {exc}"]

    if not isinstance(preguntas, list):
        return False, ["preguntas.json debe ser una lista de objetos"]

    ids_vistos: set[str] = set()
    validas = 0
    tiene_estructurada = True
    tiene_limite = True

    for i, p in enumerate(preguntas):
        if not isinstance(p, dict):
            errores.append(f"Entrada {i}: debe ser un objeto con id y prompt")
            continue

        pid = str(p.get("id", "")).strip()
        prompt = str(p.get("pregunta", "")).strip()

        if not pid:
            errores.append(f"Entrada {i}: falta id")
            continue
        if pid in _IDS_RESERVADOS:
            errores.append(f"Elimina la entrada de ejemplo: id={pid!r}")
            continue
        if pid in ids_vistos:
            errores.append(f"id duplicado: {pid!r}")
        ids_vistos.add(pid)

        if not prompt:
            errores.append(f"{pid}: prompt vacío")
            continue
        if _tiene_marcador_todo(pid) or _tiene_marcador_todo(prompt):
            errores.append(f"{pid}: sustituye los marcadores TODO por tu contenido")
            continue

        validas += 1
        texto = f"{pid} {prompt}".lower()
        if any(k in texto for k in ("json", "clasifica", "clasificar", "etiqueta", "solo una palabra")):
            tiene_estructurada = True
        if any(k in texto for k in ("limite", "límite", "fuera de dominio", "inyecc", "vacío", "vacio", "ignora")):
            tiene_limite = True

    if validas < MIN_PREGUNTAS:
        errores.append(
            f"Necesitas al menos {MIN_PREGUNTAS} preguntas propias (tienes {validas})"
        )
    if validas >= MIN_PREGUNTAS and not tiene_estructurada:
        errores.append(
            "Incluye al menos 1 pregunta con salida estructurada "
            "(JSON, clasificación cerrada, etc.) — revisa el README"
        )
    if validas >= MIN_PREGUNTAS and not tiene_limite:
        errores.append(
            "Incluye al menos 1 caso límite — revisa el README "
            "(fuera de dominio, inyección, vacío, formato estricto)"
        )

    return len(errores) == 0, errores


def verificar_entregables() -> tuple[bool, list[str]]:
    """Comprueba matriz y recomendación (Fase 2)."""
    errores: list[str] = []
    matriz = ENTREGABLES_DIR / "matriz_decision.md"
    recomendacion = ENTREGABLES_DIR / "recomendacion.md"

    for path in (matriz, recomendacion):
        if not path.is_file():
            errores.append(f"Falta {path.name}")
            continue
        texto = path.read_text(encoding="utf-8")
        if _tiene_marcador_todo(texto):
            errores.append(f"Completa {path.name} (quedan marcadores TODO)")

    if matriz.is_file():
        lineas_tabla = [
            ln
            for ln in matriz.read_text(encoding="utf-8").splitlines()
            if ln.startswith("|") and not ln.startswith("| Pregunta") and not ln.startswith("|--")
        ]
        filas_rellenas = [ln for ln in lineas_tabla if ln.count("|") >= 5 and "TODO_" not in ln]
        if len(filas_rellenas) < MIN_PREGUNTAS:
            errores.append(
                f"matriz_decision.md: rellena al menos {MIN_PREGUNTAS} filas de la tabla"
            )

    return len(errores) == 0, errores