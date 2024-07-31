import streamlit as st
import anthropic
import pandas as pd
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# Configurar el cliente de Anthropic usando la API key del archivo .env
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

st.title("Aplicación de Preguntas y Respuestas con Claude 3.5 Sonnet")

# Inicializar los historiales de chat en la sesión si no existen
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'file_chat_history' not in st.session_state:
    st.session_state.file_chat_history = []

def get_claude_response(prompt, context=""):
    system_prompt = ("Eres un asistente AI altamente preciso y confiable. "
                     "Proporciona respuestas detalladas y precisas basadas en la información disponible. "
                     "Si no tienes suficiente información para responder con certeza, indícalo claramente. "
                     "Evita especulaciones y céntrate en hechos verificables.")
    
    full_prompt = f"{system_prompt}\n\nContexto: {context}\n\nPregunta del usuario: {prompt}"
    
    message = client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=2000,
        temperature=0.2,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": full_prompt}
        ]
    )
    return message.content[0].text

# Área de preguntas generales
st.header("Preguntas Generales")

# Mostrar el historial de chat general
for q, a in st.session_state.chat_history:
    st.text_area("Pregunta:", value=q, height=100, disabled=True)
    st.text_area("Respuesta:", value=a, height=200, disabled=True)
    st.markdown("---")

# Área para nueva pregunta general
user_question = st.text_input("Haga su nueva pregunta aquí:")
if st.button("Enviar Pregunta"):
    if user_question:
        response = get_claude_response(user_question)
        
        # Agregar la nueva pregunta y respuesta al historial
        st.session_state.chat_history.append((user_question, response))
        
        # Mostrar la nueva respuesta
        st.text_area("Respuesta:", value=response, height=200, disabled=True)
        
        # Limpiar el campo de entrada
        st.rerun()

# Subida de archivos
st.header("Subir Archivo")
uploaded_file = st.file_uploader("Elija un archivo", type=["csv", "txt", "pdf"])
if uploaded_file is not None:
    # Leer el archivo
    if uploaded_file.type == "text/csv":
        df = pd.read_csv(uploaded_file)
        st.write("Archivo CSV subido exitosamente. Primeras filas:")
        st.write(df.head())
        file_content = df.to_string()
    elif uploaded_file.type == "text/plain":
        file_content = uploaded_file.getvalue().decode("utf-8")
        st.write("Archivo de texto subido exitosamente. Primeras líneas:")
        st.write(file_content[:500])  # Mostrar los primeros 500 caracteres
    elif uploaded_file.type == "application/pdf":
        st.write("Archivo PDF subido exitosamente.")
        file_content = "Contenido del archivo PDF"  # Placeholder para PDF
        # Aquí iría el código para procesar el PDF, si es necesario

    # Área para preguntas sobre el archivo
    st.header("Preguntas sobre el Archivo")

    # Mostrar el historial de preguntas sobre el archivo
    for q, a in st.session_state.file_chat_history:
        st.text_area("Pregunta sobre el archivo:", value=q, height=100, disabled=True)
        st.text_area("Respuesta:", value=a, height=200, disabled=True)
        st.markdown("---")

    file_question = st.text_input("Haga una nueva pregunta sobre el archivo:")
    if st.button("Enviar Pregunta sobre el Archivo"):
        if file_question:
            response = get_claude_response(file_question, context=file_content[:4000])
            
            # Agregar la nueva pregunta y respuesta al historial
            st.session_state.file_chat_history.append((file_question, response))
            
            # Mostrar la nueva respuesta
            st.text_area("Respuesta:", value=response, height=200, disabled=True)
            
            # Limpiar el campo de entrada
            st.rerun()
