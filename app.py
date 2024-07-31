import streamlit as st
import anthropic
from dotenv import load_dotenv
import os
from PyPDF2 import PdfReader
import io
import traceback

# Cargar variables de entorno
load_dotenv()

# Configurar el cliente de Anthropic usando la API key del archivo .env
try:
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
except Exception as e:
    st.error(f"Error al inicializar el cliente de Anthropic: {str(e)}")
    st.stop()

st.title("Aplicación de Preguntas y Respuestas con Claude 3.5 Sonnet")

# Inicializar los historiales de chat y estados en la sesión si no existen
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'file_chat_history' not in st.session_state:
    st.session_state.file_chat_history = []
if 'file_content' not in st.session_state:
    st.session_state.file_content = ""
if 'file_uploaded' not in st.session_state:
    st.session_state.file_uploaded = False

def get_claude_response(prompt, context=""):
    system_prompt = ("Eres un asistente AI altamente preciso y confiable. "
                     "Proporciona respuestas detalladas y precisas basadas en la información disponible. "
                     "Si no tienes suficiente información para responder con certeza, indícalo claramente. "
                     "Evita especulaciones y céntrate en hechos verificables.")
    
    full_prompt = f"{context}\n\nPregunta del usuario: {prompt}"
    
    try:
        message = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=2000,
            temperature=0.2,
            system=system_prompt,
            messages=[
                {"role": "user", "content": full_prompt}
            ]
        )
        return message.content[0].text
    except Exception as e:
        st.error(f"Error al procesar la pregunta: {str(e)}")
        st.error(f"Traceback: {traceback.format_exc()}")
        return "Ha ocurrido un error inesperado. Por favor, inténtalo de nuevo o contacta al soporte técnico."

def on_general_question_submit():
    if st.session_state.user_question:
        response = get_claude_response(st.session_state.user_question)
        st.session_state.chat_history.append((st.session_state.user_question, response))
        st.session_state.user_question = ""  # Esto limpiará el campo de entrada

def on_file_question_submit():
    if st.session_state.file_question and st.session_state.file_content:
        context = f"Contexto del archivo PDF:\n\n{st.session_state.file_content[:4000]}\n\n"
        response = get_claude_response(st.session_state.file_question, context=context)
        st.session_state.file_chat_history.append((st.session_state.file_question, response))
        st.session_state.file_question = ""  # Esto limpiará el campo de entrada

# Crear pestañas
tab1, tab2 = st.tabs(["Chat General", "Chat con PDF"])

with tab1:
    st.header("Preguntas Generales")

    # Mostrar el historial de chat general
    for q, a in st.session_state.chat_history:
        st.subheader("Pregunta:")
        st.write(q)
        st.subheader("Respuesta:")
        st.write(a)
        st.markdown("---")

    # Área para nueva pregunta general
    st.text_area("Haga su nueva pregunta aquí:", key="user_question", height=100)
    st.button("Enviar Pregunta", key="general_submit", on_click=on_general_question_submit)

with tab2:
    st.header("Chat con PDF")

    # Subida de archivos
    uploaded_file = st.file_uploader("Elija un archivo PDF", type=["pdf"])
    if uploaded_file is not None:
        try:
            pdf_reader = PdfReader(io.BytesIO(uploaded_file.getvalue()))
            file_content = ""
            for page in pdf_reader.pages:
                file_content += page.extract_text() + "\n"

            st.session_state.file_content = file_content
            st.session_state.file_uploaded = True
            st.success("Archivo PDF subido exitosamente.")
        except Exception as e:
            st.error(f"Error al leer el archivo PDF: {str(e)}")
            st.error(f"Traceback: {traceback.format_exc()}")

    # Área para preguntas sobre el archivo
    if st.session_state.file_uploaded:
        # Mostrar el historial de chat del archivo
        for q, a in st.session_state.file_chat_history:
            st.subheader("Pregunta sobre el archivo:")
            st.write(q)
            st.subheader("Respuesta:")
            st.write(a)
            st.markdown("---")

        # Área para nueva pregunta sobre el archivo
        st.text_area("Haga una nueva pregunta sobre el archivo PDF:", key="file_question", height=100)
        st.button("Enviar Pregunta sobre el PDF", key="file_submit", on_click=on_file_question_submit)
    else:
        st.info("Por favor, suba un archivo PDF para hacer preguntas sobre él.")
