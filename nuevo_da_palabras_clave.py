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

def llamada(conteo_clave, total_palabras, threshold):
    return conteo_clave / total_palabras >= threshold

#------------- Detecta la emoción del cliente ----------------#

def detectar_emocion(texto):
    analizador = TextBlob(texto)
    polaridad = analizador.sentiment.polarity
    
    if polaridad > 0.3:
        return "feliz"
    elif polaridad < -0.3:
        return "molesto"
    else:
        return "sereno"

if __name__ == "__main__":
    archivo_audio = "C:/Users/Cyber/Desktop/curso selenium/emociones/llamada/llamada.wav"
    palabras_clave = ['factura', 'pago']
    threshold = 0.05
    
    transcripcion = transcribe_audio(archivo_audio)  
    segmen = separate_speakers(archivo_audio)
    
    agente = ''
    cliente = ''
    
    for i, palabra in enumerate(word_tokenize(transcripcion)):
        if segmen[i] == 0:
            agente += palabra + ' '
            # Verifica si la palabra es una de las palabras clave
            if analisis_palabra(palabra, palabras_clave) > 0:
                print("El agente dijo la palabra clave:", palabra)
        else:
            cliente += palabra + ' '        
    
    ...
    agente_palabra_clave = analisis_palabra(agente, palabras_clave)
    cliente_palabra_clave = analisis_palabra(cliente, palabras_clave)
    
    total_palabras_agente = len(word_tokenize(agente))
    total_palabras_cliente = len(word_tokenize(cliente))
    
    # Imprimimos las palabras clave que dice el agente
    print("Palabras clave que dice el agente:")
    for i, palabra in enumerate(word_tokenize(agente)):
        if palabra.lower() in palabras_clave:
            print(palabra)
    
    # Si el agente no dijo ninguna palabra clave, no es necesario generar una respuesta
    if agente_palabra_clave == 0:
        print("El agente no mencionó ninguna palabra clave.")
    else:
        # Si el cliente dijo alguna palabra clave, la llamada es exitosa y generamos una respuesta
        if llamada(cliente_palabra_clave, total_palabras_cliente, threshold):
            print("La llamada fue exitosa.")
            pregunta = "¿En qué puedo ayudarle?"
            respuesta = generar_respuesta(pregunta)
            print("Respuesta generada por AI:", respuesta)
        else:
            print("La llamada no fue exitosa.")
    
    # Detectamos la emoción del cliente y la imprimimos en pantalla
    emocion = detectar_emocion(cliente)
    print("El cliente está", emocion)

