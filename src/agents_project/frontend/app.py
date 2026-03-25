import streamlit as st
import time

# Simulamos la importación del orquestador (el AgentCore Lead debe conectar esto al real)
# from src.orchestrator_agent.orchestrator_agent import procesar_nueva_solicitud

st.set_page_config(
    page_title="Pawn Shop AI - Tasador", page_icon="💎", layout="centered"
)

# --- 1. INICIALIZACIÓN DE LA MEMORIA (SESSION STATE) ---
if "fase_actual" not in st.session_state:
    st.session_state.fase_actual = 0
if "imagen_subida" not in st.session_state:
    st.session_state.imagen_subida = None
if "texto_usuario" not in st.session_state:
    st.session_state.texto_usuario = None
if "modo_entrada" not in st.session_state:
    st.session_state.modo_entrada = None
if "datos_objeto" not in st.session_state:
    st.session_state.datos_objeto = None
if "historial_chat" not in st.session_state:
    st.session_state.historial_chat = []


# --- FUNCIONES DE CONTROL DE FLUJO ---
def reiniciar_app():
    """Resetea todo si el usuario cancela o el objeto es rechazado."""
    st.session_state.fase_actual = 0
    st.session_state.imagen_subida = None
    st.session_state.texto_usuario = None
    st.session_state.modo_entrada = None
    st.session_state.datos_objeto = None
    st.session_state.historial_chat = []
    st.rerun()


def confirmar_objeto():
    """Avanza a la fase de investigación cuando el usuario dice 'Sí'."""
    st.session_state.fase_actual = 2
    st.rerun()


# --- INTERFAZ DE USUARIO ---
st.title("💎 Tasador de Antigüedades")
st.write(
    "Sube una foto de tu objeto y nuestro equipo de expertos lo evaluará en tiempo real."
)

# FASE 0: ENTRADA
if st.session_state.fase_actual == 0:
    archivo_imagen = st.file_uploader("Foto del artículo", type=["jpg", "jpeg", "png"])
    texto = st.text_area("Descripción del artículo")

    if st.button("Enviar", disabled=not archivo_imagen and not texto, type="primary"):
        if archivo_imagen is not None:
            st.session_state.imagen_subida = archivo_imagen.getvalue()

        st.session_state.texto_usuario = texto or None
        st.session_state.fase_actual = 1
        st.rerun()

# FASE 1: FILTRO Y CONFIRMACIÓN (Human-in-the-Loop)
elif st.session_state.fase_actual == 1:
    if st.session_state.imagen_subida is not None:
        st.image(
            st.session_state.imagen_subida,
            caption="Tu artículo",
            use_container_width=True,
        )

    # Aquí llamamos al orquestador (que a su vez llama al Agente Filtro)
    with st.spinner("El Tasador Jefe está examinando la pieza con su lupa..."):
        # MOCK: Aquí el AgentCore Lead debe meter la llamada real:
        # resultado = procesar_nueva_solicitud(st.session_state.imagen_subida)

        # Simulación de lo que devolvería el filtro tras 2 segundos:
        time.sleep(2)
        resultado = {
            "es_tasable": True,
            "mensaje_usuario": "Parece que nos traes una moneda antigua de plata. ¿Es este el producto que deseas que nuestro equipo tase hoy?",
            "nombre_objeto_detectado": "Moneda antigua de plata",
        }

        st.session_state.datos_objeto = resultado

    # Lógica de bifurcación basada en el JSON del Agente Filtro
    if not st.session_state.datos_objeto["es_tasable"]:
        st.error("🚫 Artículo Rechazado")
        st.write(st.session_state.datos_objeto["mensaje_usuario"])
        st.button("Intentar con otro objeto", on_click=reiniciar_app)

    else:
        st.success("✅ Artículo pre-aprobado")
        st.write(
            f"**Tasador Jefe:** {st.session_state.datos_objeto['mensaje_usuario']}"
        )

        # LOS BOTONES MÁGICOS QUE NO ROMPEN STREAMLIT
        col1, col2 = st.columns(2)
        with col1:
            st.button(
                "Sí, es correcto. Proceder a tasar.",
                on_click=confirmar_objeto,
                type="primary",
            )
        with col2:
            st.button("No, me he equivocado de foto.", on_click=reiniciar_app)

# FASE 2: INVESTIGACIÓN Y NEGOCIACIÓN
elif st.session_state.fase_actual == 2:
    if (
        st.session_state.imagen_subida is not None
        and st.session_state.datos_objeto is not None
    ):
        st.image(
            st.session_state.imagen_subida,
            caption=st.session_state.datos_objeto["nombre_objeto_detectado"],
            width=200,
        )

    st.info(
        "🔍 Enviando a nuestro equipo de investigación (Historiador y Analista de Mercado)..."
    )

    # Aquí irá la lógica del chat continuo con el Agente Negociador
    st.write("*(Aquí irá el componente st.chat_input para regatear el precio)*")

    if st.button("Empezar de nuevo"):
        reiniciar_app()
