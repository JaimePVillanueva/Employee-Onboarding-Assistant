from config import (
    PERFILES,
    SYSTEM_RULES,
    DOM_KEY,
    JSON_SCHEMA_CHECKLIST,
    RESUMEN
    )

def build_faqs_block(faqs: list[dict]) -> str:
    if not faqs:
        return ""
    lines = ["--- FAQs ---"]
    # for f in range (len(faqs)):
    for f in faqs:
        lines.append(f"P: {f.get('pregunta', '')}")
        lines.append(f"R: {f.get('respuesta_corta', '')}")
        lines.append("")
    lines.append("--- FIN FAQs ---")
    return "\n".join(lines)

def build_docs_block(docs:list[dict]) -> str:
    if not docs:
        return ""
    lines = ["--- DOCs ---"]
    # for d in range (len(docs)):
    for d in docs:
        lines.append(f"Titulo: {d.get('titulo','')}")
        lines.append(f'Departamento: {d.get('departamento','')}')
        lines.append(f"Cuerpo: {d.get('cuerpo','')}")
        lines.append("")
    lines.append("--- FIN DOCs ---")
    return "\n".join(lines)

def build_history_block(messages: list[dict]) -> str:
    """Formatea el historial reciente como texto."""
    if not messages:
        return "(sin turnos previos en la ventana)"
    return "\n".join(f"{m['role']}: {m['text']}" for m in messages)

def build_documentation_block(*,faqs:list[dict],docs:list[dict])->str:
    return f'''
===== DOCUMENTACIÓN =====

{build_faqs_block(faqs)}

{build_docs_block(docs)}

===== FIN DOCUMENTACIÓN =====
'''.strip()

def build_tareas_block(tareas:list[dict]) -> str:
    if not tareas:
        return ""
    lines = ["--- TAREAS ---"]
    # for d in range (len(docs)):
    for t in tareas:
        lines.append(f"Titulo: {t.get('titulo','')}")
        lines.append(f'Departamento: {t.get('departamento','')}')
        lines.append(f"Cuerpo: {t.get('cuerpo','')}")
        lines.append("")
    lines.append("--- FIN TAREAS ---")
    return "\n".join(lines)

def resolver_perfil(assistant_config: dict) -> dict:
    clave = assistant_config["perfil_activo"]
    if clave not in PERFILES:
        raise ValueError(f"Perfil desconocido: {clave}")
    return PERFILES[clave]


def build_assistant_prompt(
    *,
    assistant_config: dict,
    user_state: dict,
    user_message: str,
    extra_context: dict | None = None,
    recent_messages: list[dict] | None = None,)->str:
    perfil=resolver_perfil(assistant_config=assistant_config)
    profile=user_state.get('user_profile',{})
    faqs=extra_context.get('faqs',[]) or []
    docs=extra_context.get('docs',[]) or []
    recent=recent_messages or []
    
    return f'''
Instrucciones del asistente de empleados:

{perfil['rol']}
{SYSTEM_RULES}
- Nivel de explicación del perfil: {perfil["nivel_explicacion"]}.
- Máximo aproximado: {assistant_config["max_palabras"]} palabras.

Perfil del usuario:
- Nombre: {profile.get("nombre") or "(desconocido)"}
- Perfil: {profile.get("perfil", "dev_junior")}
- Rol: {profile.get('rol')}
- Departamento: {profile.get('depatamento')}
- Modalidad: {profile.get('modalidad')}
- Idioma: {profile.get('idioma_preferido')}
- Tema actual: {profile.get("tema_actual",'sin tema')}

{build_documentation_block(faqs=faqs,docs=docs)}

Historial reciente:
{build_history_block(recent)}

Mensaje actual del usuario:
{user_message.strip()}
'''.strip()
    
def prompt_tareas(
    *,
    state:dict,
    docs:list[dict]          
)->str:
    user=state.get('user_profile')
    return f'''
--- USUARIO ---
- Perfil: {user.get("perfil", "dev_junior")}
- Rol: {user.get('rol')}
- Departamento: {user.get('depatamento')}
- Modalidad: {user.get('modalidad')}
--- FIN USUARIO ---

{build_docs_block(docs=docs)}

Crea una lista de tareas a partir de los documentos proporcionados que aplican a el perfil del usuario
Debes responder en idioma {user.get('idioma_preferido')}

{JSON_SCHEMA_CHECKLIST}
'''
def comprobar_tareas(*,state:dict,dia:int)->None:
    tareas=state.get('tareas',[])
    for t in tareas:
        if t.get('dia',1)<dia and not t.get('completada',False):
            respuesta=input(f'Has completado {t.get('titulo')}? (S/N) :')
            while respuesta!='S' and respuesta!='N':
                respuesta=input('Resoponde solo S ó N :')
            if respuesta=='S':
                t['completada']=True

def prompt_resumen_tareas(tareas:list[dict])->str:
    return f'''
{RESUMEN}

{build_tareas_block(tareas=tareas)}
'''.strip()