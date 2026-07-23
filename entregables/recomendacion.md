# Recomendación — Employee Onboarding Assistant

## Caso de uso

El asistente acompaña a los empleados nuevos de Bridge SA durante sus primeros días: responde dudas sobre herramientas corporativas, primeros pasos y políticas internas usando únicamente la documentación de onboarding, y genera un checklist de tareas para cada día (1–5) adaptado al perfil del empleado.

**No** atiende consultas de participantes externos de los programas formativos, no da información salarial ni datos de otros empleados, y no inventa políticas que no consten en la documentación: en esos casos deriva a IT, People o al manager según corresponda.

## Modelo recomendado para producción

`gemini-flash-lite-latest` para el chat en tiempo real.

Con una latencia media de 822 ms frente a los 3906 ms del modelo estándar, responde casi 5 veces más rápido. En una conversación con un empleado que acaba de entrar, esa diferencia se nota: 4 segundos de espera por cada pregunta hace que el asistente se sienta lento y se deje de usar.

## Modelo alternativo (opcional)

`gemini-flash-latest` para la generación de checklists en batch.

El checklist no se genera en medio de una conversación: se prepara una vez por empleado y día. Ahí la latencia no importa, y sí interesa la mayor capacidad del modelo estándar para estructurar correctamente el JSON y repartir las tareas entre los 5 días sin repetirlas.

## Trade-off principal

**Ganamos:** velocidad (4.8x) y coste en tokens (3.3x menos: 221 frente a 732 de media por consulta). El sistema aguanta mucho mejor picos de uso y agota más tarde los límites del plan.

**Perdemos:** algo de matiz en la redacción. El modelo estándar adapta el tono al perfil con más finura y elabora respuestas más ricas. Para preguntas de onboarding —concretas y respaldadas por documentación que ya le pasamos en el prompt— esa capacidad extra no aporta lo suficiente como para justificar 5 veces más de espera.

## ¿Qué pasaría si duplicáramos el tráfico?

El consumo escala de forma directa con el volumen: tokens × número de consultas.

Con el modelo estándar, cada 1000 consultas suponen unos 732.000 tokens. Con el ligero, 221.000. Al duplicar el tráfico, esa diferencia de ~511.000 tokens por cada 1000 consultas también se duplica.

No es solo una cuestión de coste: durante el propio benchmark ya vimos el efecto práctico. El modelo estándar agotó la cuota disponible después de 6 casos, mientras que el ligero completó los 10. Con el doble de tráfico, el modelo que consume más agota antes los límites y deja de responder — que es el peor fallo posible en un asistente que la gente espera tener disponible.

## Riesgo o condición

**No usaríamos el flash-lite si** el asistente tuviera que razonar sobre casos ambiguos sin documentación de apoyo, o si tuviera que redactar textos largos donde el matiz importe.

**Antes de desplegar validaríamos:**

1. Que en el caso ambiguo (baja médica vs baja laboral) el modelo distingue los dos flujos y no los mezcla.
2. Que ante la pregunta salarial deriva a People sin dar cifras.
3. Que ante el intento de inyección mantiene su rol.
4. Que ante una política que no consta admite que no la tiene documentada en lugar de inventarla.

Estos cuatro casos están en el benchmark precisamente para poder comprobarlo antes de poner nada en producción.
