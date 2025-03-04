# IA FUNCTION CALLING SYSTEM
Cuando un usuario envía un mensaje, este se envía primero a una IA para analizar si el mensaje solicita alguna función específica de una lista predefinida. En el prompt de la IA, se le indica que debe identificar si el mensaje menciona alguna de las funciones disponibles, proporcionando solo la ID de la función en minúsculas y sin caracteres adicionales. Un ejemplo de prompt podría ser:

**"Eres una IA enfocada en describir si el mensaje pide una de las funciones que están en la lista:**
```
codigo_morse: traduce el mensaje a código Morse
otra_funcion: descripción de otra función
```
**Asegúrate de dar la ID de la función específicamente, solo la ID, en minúscula, sin puntos o cosas similares. En caso de no existir una función, devuelve 'none'."**

Si se detecta una función, su ID se mostrará debajo del mensaje del usuario. Si la respuesta es "none", no se mostrará nada.

Después de este análisis, si la respuesta es "none", se procede a procesar el mensaje normalmente con la IA, como en un chatbot típico. Sin embargo, si se detecta una función válida, en lugar de procesar el mensaje con la IA, se ejecutará la función correspondiente. Por ejemplo, podría haber una función que traduzca el mensaje a código Morse, y la IA devolverá el resultado en ese formato.

Es importante distinguir entre "procesar el mensaje con la IA" (como en un chatbot) y "procesar el mensaje con function calling", que implica pasar el mensaje a un modelo que identifica y ejecuta funciones específicas.

## Implementación Paso a Paso

A continuación, se describen los pasos para implementar la funcionalidad de llamada a funciones en el sistema de IA:

1. **Definir las Funciones Disponibles**:
   - Crear un diccionario o lista que contenga las funciones disponibles y sus descripciones. Esto permitirá a la IA identificar qué funciones pueden ser llamadas.

2. **Modificar el Prompt de la IA**:
   - Ajustar el prompt que se envía a la IA para que incluya instrucciones sobre cómo identificar las funciones disponibles en el mensaje del usuario.

3. **Analizar la Respuesta de la IA**:
   - Implementar la lógica para analizar la respuesta de la IA. Si la respuesta contiene una ID de función válida, se procederá a ejecutar esa función.

4. **Ejecutar la Función Correspondiente**:
   - Si se detecta una función válida, ejecutar la función correspondiente y devolver el resultado al usuario.

5. **Manejo de Errores**:
   - Implementar un manejo de errores adecuado para situaciones en las que la IA no pueda identificar una función o si ocurre un error al ejecutar la función.

6. **Pruebas**:
   - Realizar pruebas exhaustivas para asegurarse de que la funcionalidad de llamada a funciones funcione como se espera y que no afecte el flujo normal del chatbot.
