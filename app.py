"""
SUMÉRGETE+ — MVP
-----------------
App educativa marina con dos secciones:
1. Asistente IA para docentes (chat con Claude)
2. Fichas de especies marinas

Cómo correr localmente:
    streamlit run app.py

Necesitas guardar tu clave de la API de Anthropic en:
    .streamlit/secrets.toml
como:
    ANTHROPIC_API_KEY = "tu-clave-aqui"
"""

import json
import streamlit as st
from anthropic import Anthropic

# ------------------------------------------------------------------
# Configuración general de la página
# ------------------------------------------------------------------
st.set_page_config(page_title="Sumérgete+", page_icon="🌊", layout="centered")

# ------------------------------------------------------------------
# Navegación simple entre secciones (sidebar)
# ------------------------------------------------------------------
seccion = st.sidebar.radio(
    "Navegación",
    ["🤖 Asistente para docentes", "🐠 Fichas de especies"],
)

st.sidebar.markdown("---")
st.sidebar.caption("Sumérgete+ · MVP v0.1")


# ------------------------------------------------------------------
# Utilidades
# ------------------------------------------------------------------
@st.cache_data
def cargar_especies():
    """Carga las fichas de especies desde el archivo JSON local."""
    with open("data/especies.json", encoding="utf-8") as f:
        return json.load(f)


def obtener_cliente_anthropic():
    """
    Crea el cliente de Anthropic usando la clave guardada en secrets.
    Si no existe, avisa al usuario en vez de crashear la app.
    """
    api_key = st.secrets.get("ANTHROPIC_API_KEY", None)
    if not api_key:
        st.error(
            "Falta configurar tu ANTHROPIC_API_KEY en .streamlit/secrets.toml "
            "(en local) o en el panel de Secrets de Streamlit Cloud (en producción)."
        )
        st.stop()
    return Anthropic(api_key=api_key)


SYSTEM_PROMPT = """Eres el asistente docente de Sumérgete+, una plataforma de educación
marina para colegios en Chile y Latinoamérica. Ayudas a profesores de Ciencias, Historia
y Tecnología a:
- Explicar conceptos de ciencias marinas de forma simple y alineada al currículum escolar.
- Sugerir actividades de clase sobre océanos, biodiversidad marina, contaminación,
  pesca sostenible y cambio climático.
- Generar preguntas de evaluación o rúbricas simples sobre temas marinos.

Responde siempre en español, de forma clara, breve y práctica para uso en el aula.
Si te piden algo fuera del ámbito educativo/marino, redirige amablemente la conversación
hacia cómo puedes ayudar con educación oceánica.
"""


# ------------------------------------------------------------------
# Sección 1: Asistente IA para docentes
# ------------------------------------------------------------------
def mostrar_asistente():
    st.title("🤖 Asistente para docentes")
    st.caption("Pregúntame sobre contenidos, actividades o evaluaciones de educación marina.")

    cliente = obtener_cliente_anthropic()

    # Historial de conversación guardado en la sesión del navegador
    if "mensajes" not in st.session_state:
        st.session_state.mensajes = []

    # Mostrar historial previo
    for m in st.session_state.mensajes:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    # Input del usuario
    pregunta = st.chat_input("Ej: dame una actividad sobre contaminación por plásticos")
    if pregunta:
        st.session_state.mensajes.append({"role": "user", "content": pregunta})
        with st.chat_message("user"):
            st.markdown(pregunta)

        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                respuesta = cliente.messages.create(
                    model="claude-sonnet-4-6",
                    max_tokens=1000,
                    system=SYSTEM_PROMPT,
                    messages=st.session_state.mensajes,
                )
                texto_respuesta = respuesta.content[0].text
                st.markdown(texto_respuesta)

        st.session_state.mensajes.append({"role": "assistant", "content": texto_respuesta})


# ------------------------------------------------------------------
# Sección 2: Fichas de especies
# ------------------------------------------------------------------
def mostrar_fichas():
    st.title("🐠 Fichas de especies marinas")

    especies = cargar_especies()
    nombres = [e["nombre_comun"] for e in especies]
    seleccion = st.selectbox("Elige una especie", nombres)

    especie = next(e for e in especies if e["nombre_comun"] == seleccion)

    st.subheader(f"{especie['nombre_comun']}")
    st.caption(f"*{especie['nombre_cientifico']}*")

    col1, col2 = st.columns(2)
    col1.metric("Estado de conservación", especie["estado_conservacion"])
    col2.write(f"**Hábitat:** {especie['habitat']}")

    st.markdown("**Descripción**")
    st.write(especie["descripcion"])

    st.info(f"💡 **Dato curioso:** {especie['dato_curioso']}")


# ------------------------------------------------------------------
# Router
# ------------------------------------------------------------------
if seccion == "🤖 Asistente para docentes":
    mostrar_asistente()
else:
    mostrar_fichas()
