from config import PERFILES

def build_faq_block(faq_entries: list[dict]) -> str:
    """Bloque de texto con entradas FAQ seleccionadas."""
    if not faq_entries:
        return ""
    lines = ["--- FAQ (referencia seleccionada) ---"]
    for entry in faq_entries:
        lines.append(f"P: {entry.get('pregunta', '')}")
        lines.append(f"R: {entry.get('respuesta_corta', '')}")
        lines.append("")
    lines.append("--- FIN FAQ ---")
    return "\n".join(lines)

def build_history_block(messages: list[dict]) -> str:
    """Formatea el historial reciente como texto."""
    if not messages:
        return "(sin turnos previos en la ventana)"
    return "\n".join(f"{m['role']}: {m['text']}" for m in messages)

def resolver_perfil(assistant_config: dict) -> dict:
    """Resuelve el perfil activo desde assistant_config. Helper ya implementado."""
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
{perfil.get('rol')}

Instrucciones del asistente de empleados:
- Responde en {assistant_config["idioma_respuesta"]}.
- Nivel de explicación del perfil: {perfil["nivel_explicacion"]}.
- Máximo aproximado: {assistant_config["max_palabras"]} palabras.

Perfil del usuario:
- Nombre: {profile.get("nombre") or "(desconocido)"}
- Nivel declarado: {profile.get("nivel", "junior")}
- Tema actual: {profile.get("tema_actual") or "(sin tema fijado)"}

{build_faq_block(faqs)}

Historial reciente:
{build_history_block(recent)}

Mensaje actual del usuario:
{user_message.strip()}
'''.strip()
    