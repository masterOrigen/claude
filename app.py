import streamlit as st
import anthropic
import pandas as pd
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# Configurar el cliente de Claude usando la API key del archivo .env
client = anthropic.Client(api_key=os.getenv("ANTHROPIC_API_KEY"))

st.title("Aplicación de Preguntas y Respuestas con Claude 3.5 Sonnet")

# Área de preguntas generales
st.header("Preguntas Generales")
user_question = st.text_input("Haga su pregunta aquí:")
if st.button("Enviar Pregunta"):
    if user_question:
        # Enviar la pregunta a Claude y obtener la respuesta
        response = client.complete(
            prompt=user_question,
            model="claude-3.5-sonnet",
            max_tokens_to_sample=1000
        )
        st.write("Respuesta:", response.completion)

# Subida de archivos
st.header("Subir Archivo")
uploaded_file = st.file_uploader("Elija un archivo", type=["csv", "txt", "pdf"])
if uploaded_file is not None:
    # Leer el archivo (este ejemplo asume un CSV, ajuste según sea necesario)
    if uploaded_file.type == "text/csv":
        df = pd.read_csv(uploaded_file)
        st.write("Archivo CSV subido exitosamente. Primeras filas:")
        st.write(df.head())
    elif uploaded_file.type == "text/plain":
        content = uploaded_file.getvalue().decode("utf-8")
        st.write("Archivo de texto subido exitosamente. Primeras líneas:")
        st.write(content[:500])  # Mostrar los primeros 500 caracteres
    elif uploaded_file.type == "application/pdf":
        st.write("Archivo PDF subido exitosamente.")
        # Aquí iría el código para procesar el PDF, si es necesario

    # Área para preguntas sobre el archivo
    st.header("Preguntas sobre el Archivo")
    file_question = st.text_input("Haga una pregunta sobre el archivo:")
    if st.button("Enviar Pregunta sobre el Archivo"):
        if file_question:
            # Preparar el contexto según el tipo de archivo
            if uploaded_file.type == "text/csv":
                context = df.to_string()
            elif uploaded_file.type == "text/plain":
                context = content
            else:
                context = "Contenido del archivo PDF"  # Placeholder para PDF
            
            # Procesar la pregunta con Claude, incluyendo el contexto del archivo
            prompt = f"Contexto del archivo:\n{context[:2000]}\n\nPregunta: {file_question}"
            response = client.complete(
                prompt=prompt,
                model="claude-3.5-sonnet",
                max_tokens_to_sample=1000
            )
            st.write("Respuesta:", response.completion)
