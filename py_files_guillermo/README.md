# Estructura Json Chat
```json
{
    "pregunta": "pregunta",
    "respuesta": "respuesta",
    "faqs": ["faq_01","faq_03"]
}
```

# Esctructura Respuesta Chat
```json
{
    "status":"ok",
    "message":"Pregunta respondida",
    "data":{
        "pregunta": "pregunta",
        "respuesta": "respuesta",
        "faqs": ["faq_01","faq_03"]
    }
}
```

# Impresion Chat
```text
[OK] Pregunta respondida
=========================
P: pregunta
R: respuesta
FAQs: [faq_01,faq_03]
```

# Estructura Json Checklist
```json
{
  "empleado_id": "emp_01",
  "dia": 1,
  "tareas": [
    {
      "id": "t01",
      "titulo": "Unirse a los canales obligatorios de Slack (#general, #anuncios y canal de departamento)",
      "completada": false,
      "fuente_doc": "doc_it_02"
    },
    {
      "id": "t02",
      "titulo": "Asistir a la reunión de bienvenida de las 9:30 y saludar a tu buddy en Slack",
      "completada": false,
      "fuente_doc": "doc_bienvenida_01"
    }
  ],
  "mensaje_resumen": "Primer día: Dar accesos básicos al empleado."
}
```

# Estructura Respuesta Checklist
```json
{
  "empleado": {
    "id": "emp_01",
    "nombre": "Laura Méndez",
    "departamento": "engineering",
    "rol": "Junior Software Engineer",
    "fecha_inicio": "2026-03-02",
    "manager": "Carlos Ruiz",
    "modalidad": "remoto",
    "ubicacion": "Valencia, España",
    "idioma_preferido": "es",
    "perfil": "dev_junior"
  },
  "dia": 1,
  "tareas": [
    {
      "id": "t01",
      "titulo": "Unirse a los canales obligatorios de Slack (#general, #anuncios y canal de departamento)",
      "completada": false,
      "fuente_doc": "doc_it_02"
    },
    {
      "id": "t02",
      "titulo": "Asistir a la reunión de bienvenida de las 9:30 y saludar a tu buddy en Slack",
      "completada": false,
      "fuente_doc": "doc_bienvenida_01"
    }
  ],
  "mensaje_resumen": "Primer día: Dar accesos básicos al empleado."
}
```

# Impresion Checklist
```text
Nombre: Laura Méndez    Día: 1
=================================
Primer día: Dar accesos básicos al empleado
Tareas:
 - Unirse a los canales obligatorios de Slack (#general, #anuncios y canal de departamento)
 - Asistir a la reunión de bienvenida de las 9:30 y saludar a tu buddy en Slack
```