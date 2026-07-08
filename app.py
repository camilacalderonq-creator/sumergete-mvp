"""
SUMÉRGETE+ — MVP
-----------------
App educativa marina con tres secciones:
1. Asistente IA para docentes (chat con Claude)
2. Fichas de especies marinas
3. Panel estudiantes (quiz interactivo)

Cómo correr localmente:
    streamlit run app.py

Necesitas guardar tu clave de la API de Anthropic en:
    .streamlit/secrets.toml
como:
    ANTHROPIC_API_KEY = "tu-clave-aqui"
"""

import json
import random
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
    ["🤖 Asistente para docentes", "🐠 Fichas de especies", "🎮 Panel estudiantes"],
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

    if "mensajes" not in st.session_state:
        st.session_state.mensajes = []

    for m in st.session_state.mensajes:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

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
# Sección 3: Panel de estudiantes (quiz interactivo)
# ------------------------------------------------------------------
def generar_nueva_pregunta(especies):
    correcta = random.choice(especies)
    otras = [e for e in especies if e["nombre_comun"] != correcta["nombre_comun"]]
    incorrectas = random.sample(otras, k=min(2, len(otras)))

    opciones = [correcta["nombre_comun"]] + [e["nombre_comun"] for e in incorrectas]
    random.shuffle(opciones)

    st.session_state.pregunta_actual = {
        "dato_curioso": correcta["dato_curioso"],
        "respuesta_correcta": correcta["nombre_comun"],
        "opciones": opciones,
    }
    st.session_state.respondido = False


def mostrar_panel_estudiantes():
    st.title("🎮 Panel estudiantes")
    st.caption("¿Cuánto sabes de las especies marinas de Chile? ¡Pon a prueba tu conocimiento!")

    especies = cargar_especies()

    if "puntaje" not in st.session_state:
        st.session_state.puntaje = 0
    if "preguntas_respondidas" not in st.session_state:
        st.session_state.preguntas_respondidas = 0
    if "pregunta_actual" not in st.session_state:
        generar_nueva_pregunta(especies)

    col1, col2 = st.columns(2)
    col1.metric("✅ Puntaje", st.session_state.puntaje)
    col2.metric("📝 Preguntas respondidas", st.session_state.preguntas_respondidas)

    st.divider()

    pregunta = st.session_state.pregunta_actual
    st.subheader("💡 Pista:")
    st.info(pregunta["dato_curioso"])
    st.write("**¿A qué especie corresponde este dato curioso?**")

    cols = st.columns(len(pregunta["opciones"]))
    for i, opcion in enumerate(pregunta["opciones"]):
        if cols[i].button(opcion, key=f"opcion_{i}_{st.session_state.preguntas_respondidas}",
                           disabled=st.session_state.respondido):
            st.session_state.respondido = True
            st.session_state.preguntas_respondidas += 1
            if opcion == pregunta["respuesta_correcta"]:
                st.session_state.puntaje += 1
                st.session_state.ultimo_resultado = "correcto"
            else:
                st.session_state.ultimo_resultado = "incorrecto"
            st.rerun()

    if st.session_state.get("respondido"):
        if st.session_state.ultimo_resultado == "correcto":
            st.success(f"🎉 ¡Correcto! Era {pregunta['respuesta_correcta']}.")
        else:
            st.error(f"❌ No era esa. La respuesta correcta era: {pregunta['respuesta_correcta']}.")

        if st.button("Siguiente pregunta ➡️"):
            generar_nueva_pregunta(especies)
            st.rerun()


# ------------------------------------------------------------------
# Router
# ------------------------------------------------------------------
if seccion == "🤖 Asistente para docentes":
    mostrar_asistente()
elif seccion == "🐠 Fichas de especies":
    mostrar_fichas()
else:
    mostrar_panel_estudiantes()
