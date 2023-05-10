import openai
import speech_recognition as sr
from pyAudioAnalysis import audioSegmentation as segmento
import nltk
from nltk.tokenize import word_tokenize
from textblob import TextBlob

nltk.download("punkt")

#---------------- Transcribe el audio a texto ---------------#

def transcribe_audio(audio_file):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as llamada:
        audio = recognizer.record(llamada)
        
    return recognizer.recognize_google(audio, language='es-ES')

#------------- Separa el audio de las dos personas ----------#

def separate_speakers(audio_file):
    resultados = segmento.speaker_diarization(audio_file, n_speakers=2)
    segmen = resultados[0]

    return segmen

#----------------- Genera una respuesta con OpenAI ---------------#

def generar_respuesta(pregunta):
    # Llamamos a la API de OpenAI para generar una respuesta en función de la pregunta dada
    openai.api_key = "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"
    response = openai.Completion.create(
      engine="davinci",
      prompt=pregunta,
      max_tokens=50,
      n=1,
      stop=None,
      temperature=0.5,
    )
    return response.choices[0].text

#----------------- Analiza las palabras clave ---------------#

def analisis_palabra(text, keywords):
    palabras = word_tokenize(text)
    keywords_count = 0
    for word in palabras:
        if word.lower() in keywords:
            keywords_count = keywords_count + 1
    return keywords_count

#--------- Califica la llamada y sus palabras clave ---------#

def llamada(conteo_clave, total_palabras, agente_palabras_por_segundo, umbral_palabras_por_segundo, umbral_velocidad_hablada):
    # Verificar si el agente dijo alguna palabra clave
    if conteo_clave == 0:
        print("El agente no mencionó ninguna palabra clave.")
        return False
    
    # Verificar si la tasa de palabras habladas del agente es demasiado baja
    if agente_palabras_por_segundo < umbral_palabras_por_segundo:
        print("La tasa de palabras habladas del agente es demasiado baja.")
        return False
    
    # Verificar si la velocidad de habla del agente es adecuada
    if agente_palabras_por_segundo < umbral_velocidad_hablada[0] or agente_palabras_por_segundo > umbral_velocidad_hablada[1]:
        print("La velocidad de habla del agente es demasiado lenta o demasiado rápida.")
        return False
    

#----------------- Detecta la emoción en el texto ---------------#

def detectar_emocion(texto):
    blob = TextBlob(texto)
    emociones = {"positive": 0, "negative": 0, "neutral": 0}
    for sentence in blob.sentences:
        sentiment = sentence.sentiment.polarity
        if sentiment > 0:
            emociones["positive"] += 1
        elif sentiment < 0:
            emociones["negative"] += 1
        else:
            emociones["neutral"] += 1
    emocion_max = max(emociones, key=emociones.get)
    return emocion_max

#----------------- Verifica la calidad de la llamada ---------------#

def verificar_calidad(conteo_clave_agente, total_palabras_agente, conteo_clave_cliente, total_palabras_cliente):
    # Si el agente o el cliente no dijeron ninguna palabra clave, la calidad de la llamada es mala
    if conteo_clave_agente == 0 or conteo_clave_cliente == 0:
        return "Mala"
    
    # Si la proporción de palabras clave dichas por el agente es menor al 50%, la calidad de la llamada es regular
    if conteo_clave_agente / total_palabras_agente < 0.5:
        return "Regular"
    
    # Si la proporción de palabras clave dichas por el agente es mayor o igual al 50%, la calidad de la llamada es buena
    return "Buena"

    
if __name__ == "__main__":
    archivo_audio = "C:/Users/Cyber/Desktop/curso selenium/emociones/llamada/llamada.wav"
    palabras_clave = ['producto', 'servicio', 'problema']
    threshold = 0.05
    
    transcripcion = transcribe_audio(archivo_audio)  
    segmen = separate_speakers(archivo_audio)
    
    agente = ''
    cliente = ''
    palabras_clave_detectadas = []
    
    for i, palabra in enumerate(word_tokenize(transcripcion)):
        if segmen[i] == 0:
            agente += palabra + ' '
            if palabra.lower() in palabras_clave:
                palabras_clave_detectadas.append(palabra)
        else:
            cliente += palabra + ' '        
            if palabra.lower() in palabras_clave:
                palabras_clave_detectadas.append(palabra)
    
    agente_palabra_clave = analisis_palabra(agente, palabras_clave)
    cliente_palabra_clave = analisis_palabra(cliente, palabras_clave)
    
    total_palabras_agente = len(word_tokenize(agente))
    total_palabras_cliente = len(word_tokenize(cliente))
    
    # Si el agente no dijo ninguna palabra clave, no es necesario generar una respuesta
    if agente_palabra_clave == 0:
        print("El agente no mencionó ninguna palabra clave.")
        print("La llamada no fue exitosa.")
        print("El cliente está", detectar_emocion(cliente))
    else:
        # Si el cliente dijo alguna palabra clave, la llamada es exitosa y generamos una respuesta
        if llamada(cliente_palabra_clave, total_palabras_cliente, threshold):
            print("La llamada fue exitosa.")
            pregunta = "¿En qué puedo ayudarle?"
            respuesta = generar_respuesta(pregunta)
            print("Respuesta generada por AI:", respuesta)
        else:
            print("La llamada no fue exitosa.")
        
        # Imprime las palabras clave detectadas por el agente y el cliente
        if palabras_clave_detectadas:
            print("Palabras clave detectadas:", ", ".join(set(palabras_clave_detectadas)))
    
        # Verifica si la calidad de la llamada cumple con los parámetros estándar
        calidad = verificar_calidad(agente_palabra_clave, total_palabras_agente, cliente_palabra_clave, total_palabras_cliente)
        if calidad == "Buena":
            print("La calidad de la llamada fue buena.")
        elif calidad == "Regular":
            print("La calidad de la llamada fue regular.")
        else:
            print("La calidad de la llamada fue mala.")
        
        # Detectamos la emoción del cliente y la imprimimos en pantalla
        emocion = detectar_emocion(cliente)
        print("El cliente está", emocion)
