import streamlit as st
import anthropic
import pandas as pd
from dotenv import load_dotenv
import os
from PyPDF2 import PdfReader
import io

# Cargar variables de entorno
load_dotenv()

# Configurar el cliente de Anthropic usando la API key del archivo .env
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

st.title("Aplicación de Preguntas y Respuestas con Claude 3.5 Sonnet")

# Inicializar los historiales de chat y estados en la sesión si no existen
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'file_chat_history' not in st.session_state:
    st.session_state.file_chat_history = []
if 'conversation_context' not in st.session_state:
    st.session_state.conversation_context = ""
if 'user_question' not in st.session_state:
    st.session_state.user_question = ""
if 'file_question' not in st.session_state:
    st.session_state.file_question = ""

def get_claude_response(prompt, context=""):
    system_prompt = ("Eres un asistente AI altamente preciso y confiable. "
                     "Proporciona respuestas detalladas y precisas basadas en la información disponible. "
                     "Si no tienes suficiente información para responder con certeza, indícalo claramente. "
                     "Evita especulaciones y céntrate en hechos verificables.")
    
    full_prompt = f"Contexto de la conversación: {context}\n\nNueva pregunta del usuario: {prompt}\n\nPor favor, responde a la nueva pregunta teniendo en cuenta el contexto de la conversación anterior."
    
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
    except anthropic.APIError as e:
        st.error(f"Error en la API de Anthropic: {str(e)}")
        return "Lo siento, ha ocurrido un error al procesar tu pregunta. Por favor, inténtalo de nuevo más tarde."
    except Exception as e:
        st.error(f"Error inesperado: {str(e)}")
        return "Ha ocurrido un error inesperado. Por favor, inténtalo de nuevo o contacta al soporte técnico."

def on_general_question_submit():
    if st.session_state.user_question:
        response = get_claude_response(st.session_state.user_question, context=st.session_state.conversation_context)
        
        # Actualizar el contexto de la conversación
        st.session_state.conversation_context += f"\nPregunta: {st.session_state.user_question}\nRespuesta: {response}\n"
        
        # Agregar la nueva pregunta y respuesta al historial
        st.session_state.chat_history.append((st.session_state.user_question, response))
        
        # Limpiar el campo de entrada
        st.session_state.user_question = ""

def on_file_question_submit():
    if st.session_state.file_question and 'file_content' in st.session_state:
        response = get_claude_response(st.session_state.file_question, context=st.session_state.file_content[:4000])
        
        # Agregar la nueva pregunta y respuesta al historial
        st.session_state.file_chat_history.append((st.session_state.file_question, response))
        
        # Limpiar el campo de entrada
        st.session_state.file_question = ""

# Área de preguntas generales
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
if st.button("Enviar Pregunta", key="general_submit"):
    on_general_question_submit()

# Subida de archivos
st.header("Subir Archivo")
uploaded_file = st.file_uploader("Elija un archivo", type=["csv", "txt", "pdf"])
if uploaded_file is not None:
    # Leer el archivo
    try:
        if uploaded_file.type == "text/csv":
            df = pd.read_csv(uploaded_file)
            file_content = df.to_string()
        elif uploaded_file.type == "text/plain":
            file_content = uploaded_file.getvalue().decode("utf-8")
        elif uploaded_file.type == "application/pdf":
            pdf_reader = PdfReader(io.BytesIO(uploaded_file.getvalue()))
            file_content = ""
            for page in pdf_reader.pages:
                file_content += page.extract_text() + "\n"

        # Guardar el contenido del archivo en la sesión
        st.session_state.file_content = file_content
        st.success("Archivo subido exitosamente.")
    except Exception as e:
        st.error(f"Error al leer el archivo: {str(e)}")

    # Área para preguntas sobre el archivo
    st.header("Preguntas sobre el Archivo")

    # Mostrar el historial de preguntas sobre el archivo
    for q, a in st.session_state.file_chat_history:
        st.subheader("Pregunta sobre el archivo:")
        st.write(q)
        st.subheader("Respuesta:")
        st.write(a)
        st.markdown("---")

    st.text_area("Haga una nueva pregunta sobre el archivo:", key="file_question", height=100)
    if st.button("Enviar Pregunta sobre el Archivo", key="file_submit"):
        on_file_question_submit()
