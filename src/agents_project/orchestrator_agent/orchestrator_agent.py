import base64

from strands import Agent
from strands.models.bedrock import BedrockModel

from config.settings import settings
from src.image_analyst_agent.image_analyst_agent import image_analyst_tool
from src.research_agent.research_agent import research_tool
from src.market_analyst_agent.market_analyst_agent import market_analyst_tool
from src.negotiator_agent.negotiator_agent import negotiator_tool
from src.tools.calculator import calculator
from src.tools.current_date import get_current_date
from src.tools.web_search import web_search
from src.tools.image_search import image_search


ORCHESTRATOR_SYSTEM_PROMPT = """Eres el Orquestador Principal de una prestigiosa Casa de Empeños con IA.
Tu trabajo es coordinar a un equipo de agentes especializados para tasar objetos de forma precisa y profesional.

EQUIPO DISPONIBLE (herramientas):
- **image_analyst_tool**: Analista Visual. Analiza imágenes para identificar objetos y verificar si son tasables.
- **research_tool**: Investigador e Historiador. Busca historia, origen, materiales y detalles técnicos del objeto.
- **market_analyst_tool**: Analista de Mercado. Investiga precios actuales en plataformas de venta y subastas.
- **negotiator_tool**: Negociador Experto. Genera estrategia de venta, precios de salida y tácticas de negociación.
- **web_search**: Búsqueda web general para cualquier consulta adicional.
- **image_search**: Búsqueda de imágenes de referencia.
- **calculator**: Calculadora para operaciones matemáticas (márgenes, porcentajes, etc.).
- **get_current_date**: Fecha actual, útil para contextualizar tendencias de mercado.

COMPORTAMIENTO:
- Si el usuario proporciona una imagen, empieza siempre por **image_analyst_tool**.
- Si el objeto NO es tasable, informa al usuario y detente.
- Usa las herramientas tantas veces como necesites y en el orden que consideres más útil.
- Puedes volver a llamar a **research_tool** si descubres nuevos detalles tras el análisis de mercado.
- Puedes usar **web_search** para ampliar o contrastar información en cualquier momento.
- Antes de llamar a **negotiator_tool**, asegúrate de que tienes suficiente contexto histórico y de mercado.
- Si un agente falla, reporta el error pero continúa con los demás.
- Responde SIEMPRE en español.

FORMATO DE RESPUESTA FINAL:
- 🔍 Identificación del Objeto
- 📚 Contexto Histórico
- 💰 Análisis de Mercado
- 🤝 Estrategia de Negociación
- 📋 Resumen Ejecutivo con precio recomendado
"""


def crear_orquestador() -> Agent:
    """Crea y devuelve una instancia del agente orquestador."""
    modelo = BedrockModel(
        model_id=settings.llm_model_id_medium,
        region_name=settings.aws_region,
        temperature=0.3,
    )

    return Agent(
        model=modelo,
        system_prompt=ORCHESTRATOR_SYSTEM_PROMPT,
        tools=[image_analyst_tool, research_tool, market_analyst_tool, negotiator_tool, calculator, get_current_date, web_search, image_search],
    )


def procesar_solicitud(
    imagen_bytes: bytes | None = None,
    nombre_archivo: str = "",
    texto_usuario: str = "",
) -> str:
    """
    Punto de entrada principal del sistema de tasación.

    Parámetros
    ----------
    imagen_bytes : bytes | None
        Bytes de la imagen subida por el usuario.
    nombre_archivo : str
        Nombre del archivo de imagen (para detectar formato).
    texto_usuario : str
        Descripción textual del objeto proporcionada por el usuario.
    """
    orquestador = crear_orquestador()

    prompt = ""

    if imagen_bytes:
        imagen_b64 = base64.b64encode(imagen_bytes).decode("utf-8")
        prompt += f"El usuario ha subido una imagen del objeto (base64, archivo: {nombre_archivo}):\n{imagen_b64}\n\n"

    if texto_usuario:
        prompt += f"Descripción del usuario: {texto_usuario}\n\n"

    if not prompt:
        return "No se proporcionó ni imagen ni descripción del objeto."

    prompt += "Ejecuta el flujo completo de tasación."

    respuesta = orquestador(prompt)
    return str(respuesta.message) if hasattr(respuesta, "message") else str(respuesta)
