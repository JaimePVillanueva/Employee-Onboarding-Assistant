![!\[Cabecera\](./assets/cabecera_jupyter_markdown.png)](assets/cabecera_thebridge.png)

# Employee Onboarding Assistant

<p align="left">
<img src="https://img.shields.io/badge/STATUS-EN%20DESAROLLO-green">
</p> 

[![GitHub stars](https://img.shields.io/github/stars/JaimePVillanueva?style=for-the-badge&label=Estrellas&logo=github)](https://github.com/JaimePVillanueva/Employee-Onboarding-Assistant)


## Índice
* [Descripción del proyecto](#descripción-del-proyecto)
* [Estado del proyecto](#Estado-del-proyecto)
* [Características de la aplicación](#Características-de-la-aplicación)
* [Acceso al proyecto](#acceso-proyecto)
* [Tecnologías utilizadas](#tecnologías-utilizadas)
* [Desarrolladores del Proyecto](#desarrolladores-del-proyecto)
* [Conclusión](#conclusión)

## Descripción del proyecto
El *Employee Onboarding Assistant* se trata de un chatbot de acompañamiento para las nuevas incorporaciones a la empresa de TheBridge S.A. en sus primeros días. 

El chatbot cuenta con una serie de preguntas FAQ y documentación de la empresa como contexto para así poder ayudar al personal de forma exhaustiva. A su vez el desarrollo cuenta con validación de las preguntas de los empleados, benchmark de los modelos LLM a los que llama vía API para desarrollar las respuestas, y comprobación de la información que recibe como contexto. 

## Estado del proyecto
*Employee Onboarding Assistant* se encuentra en fase **prototipo** dado que todavía no cuenta con front-end y todo el proyecto se trata de un ejercicio enfocado en el aprendizaje de los desarrolladores.

## Características de la aplicación
**Parte 1 Contexto:**  Dentro de *data* se encuentra la información de la empresa, para contexto del programador, y los ficheros json que el chatbot utiliza como contexto.

**Parte 2 Asistente:** 
1. **Conversación**: El empleado escribe una pregunta libre y el asistente responde en texto, usando documentación relevante y, si aplica, historial reciente.
2. **Checklist de la semana**: Se le pasa quién es el empleado y qué día de onboarding le toca. El asistente no responde en texto libre: devuelve un plan del día en JSON con tareas concretas basadas en la documentación.

**Parte 3 Robustez:** El sistema se defiende frente a inyecciones, datos sensibles y consultas fuera de dominio. El agente ayuda con:
 - Herramientas corporativas y primeros pasos
 - Cultura de TheBridge S.A.
 - Vacaciones según documentación
 - A quién contactar / cómo escalar

El asistente no hara nada de los siguiente:
 - Inventar políticas, plazos o cifra no documentadas
 - Responder sobre salarios o datos de otros empleados
 - Atender a participantes externos de los programas formativos
 - Llamar al modelo si la validación falla (fail-closed)

 **Parte 4 Benchmark y decisión de modelo:** Se elige entre 2 modelos LLM de Gemini que sirva el propósito del chatbot a la perfección. Se determina la competencia de cada modelo comparando los resultados de latencia, tokens de salida, calidad, tono y fidelidad.

## Acceso al proyecto
### Requisitos

- Python 3.10+
- Cuenta en [Google AI Studio](https://aistudio.google.com/) (`GEMINI_API_KEY`)

### Entorno virtual

**Linux / macOS / Git Bash:**

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env               # edita tu clave dentro de .env
python main.py
```

**Windows (PowerShell):**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env             # edita tu clave dentro de .env
python main.py
```

Sin `.env`, `gemini_auth.py` pedirá la clave con `getpass` al usar la API.

---

### Estructura del proyecto

```text
.
├── README.md
├── requirements.txt       ← dependencias (pip install -r)
├── .gitignore             ← excluye .env, .venv, etc.
├── .env.example           ← plantilla de API key (sí va al repo)
├── .env                   ← tu clave real (lo creas tú; no en Git)
├── config.py              ← PERFILES, ASSISTANT_CONFIG, reglas seguridad
├── context.py             ← FAQ, documentación interna de la empresa
├── state.py               ← memoria de sesión
├── prompts.py             ← build_assistant_prompt + prompts seguros
├── validators.py          ← validación de contexto
├── logic.py               ← procesar_turno + pipelines seguridad
├── gemini_auth.py         ← configuración de la API key
├── gemini_client.py       ← llamada al modelo y obtención de métricas
├── data                   ← json de datos de contexto
├── benchmark              ← resultados de benchmark obtenidos
├── output                 ← reportes de métricas de llamadas a API
├── assets                 ← contenido del README
└── main.py                ← demos y función modo_interactivo()
```
## Tecnologías utilizadas

## Desarrolladores del proyecto
 - Dimas Amores (github: DimasAmores)
 - Guillermo Lucas (github: Guille-33)
 - Pol Castelló (github: polcastelloo)
 - Jaime Pérez (github: JaimePVillanueva)

---

¡Muchas gracias por tu tiempo y esperamos que el proyecto te sea útil!
