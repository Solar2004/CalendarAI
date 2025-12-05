import requests
import json
from config.constants import OPENROUTER_API_KEY, AI_MODEL

def codigo_morse(message: str) -> str:
    """Traduce el mensaje a código Morse."""
    morse_code_dict = {
        'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 
        'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 
        'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---', 
        'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-', 
        'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--', 
        'Z': '--..', '1': '.----', '2': '..---', '3': '...--', 
        '4': '....-', '5': '.....', '6': '-....', '7': '--...', 
        '8': '---..', '9': '----.', '0': '-----', ' ': '/'
    }
    return ' '.join(morse_code_dict.get(char.upper(), '') for char in message)

def estadisticas_texto(text: str) -> str:
    """Calcula estadísticas del texto."""
    words = len(text.split())
    chars = len(text)
    # Estimate reading time (approx 200 words per minute)
    reading_time_min = words / 200
    reading_time_sec = int((reading_time_min * 60) % 60)
    reading_time_min = int(reading_time_min)

    return (f"Estadísticas del texto:\n"
            f"- Palabras: {words}\n"
            f"- Caracteres: {chars}\n"
            f"- Tiempo de lectura estimado: {reading_time_min} min {reading_time_sec} s")

def sugerir_titulo(text: str) -> str:
    """Sugiere un título para el texto usando IA."""
    api_url = "https://openrouter.ai/api/v1/chat/completions"
    prompt = f"Sugiere un título corto y creativo para el siguiente texto:\n\n{text}"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": AI_MODEL,
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        response = requests.post(api_url, headers=headers, data=json.dumps(data), timeout=10)
        response.raise_for_status()
        response_data = response.json()
        title = response_data['choices'][0]['message']['content'].strip()
        return f"Título sugerido: {title}"
    except Exception as e:
        return f"Error al generar título: {str(e)}"
