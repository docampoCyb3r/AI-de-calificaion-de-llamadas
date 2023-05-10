import speech_recognition as sr
import openai

openai.api_key = "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"

# Función para analizar el estado de ánimo del audio
def analizar_estado_de_animo(audio):
    # Convertir el audio en texto utilizando SpeechRecognition
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio) as source:
        audio_text = recognizer.record(source)
        texto = recognizer.recognize_google(audio_text)

    # Analizar el texto utilizando la API de OpenAI
    modelo = "text-davinci-002"
    respuesta_analizada = openai.Completion.create(
        engine=modelo,
        prompt=texto,
        max_tokens=10,
        n=1,
        stop=None
    )

    # Devolver la predicción de sentimiento del modelo
    return respuesta_analizada.choices[0].text.strip()

# análisis de audio y calificación de llamada
def calificar_llamada(audio):
    # Analizar el estado de ánimo del audio
    estado_de_animo = analizar_estado_de_animo(audio)

    # Establecer parámetros para calificar la llamada
    if "bueno" in estado_de_animo:
        calificacion = "Excelente"
    elif "neutro" in estado_de_animo:
        calificacion = "Regular"
    else:
        calificacion = "Mala"

    # Devolver la calificación de la llamada y el estado de ánimo del cliente
    return calificacion, estado_de_animo

# Ejemplo de calificación de llamada
calificacion, estado_de_animo = calificar_llamada("agresivo.wav")
print(f"La llamada fue calificada como {calificacion} y el estado de ánimo del cliente fue {estado_de_animo}.")
