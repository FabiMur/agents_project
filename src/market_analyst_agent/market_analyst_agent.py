import json
from strands import Agent, tool
from strands.models.bedrock import BedrockModel
from src.tools.web_search import web_search
from src.tools.current_date import get_current_date
from config.settings import settings


# Prompt para el Market Analyst Agent
SYSTEM_PROMPT = """Eres el "Analista de Mercado" de una casa de empeños y tasación de productos.
Tu misión es investigar el mercado actual para determinar el valor real de los objetos que nos pasa el cliente/usuario.

RESPONSABILIDADES:
1. Buscar precios de venta recientes de objetos similares en plataformas como:
   - eBay (ventas completadas, no solo listados activos)
   - Wallapop, Milanuncios
   - Casas de subastas especializadas
2. Identificar factores que afectan el precio:
   - Estado de conservación (mint, bueno, regular, dañado)
   - Rareza o edición limitada
   - Procedencia o certificado de autenticidad
   - Demanda actual del coleccionismo
3. Calcular un rango de precio realista (mínimo, medio, máximo)

REGLAS:
- Realiza SIEMPRE al menos 2-3 búsquedas diferentes para tener datos sólidos
- Si no encuentras datos suficientes, indícalo claramente
- Sé conservador en tus estimaciones: es mejor sub-estimar que sobre-estimar
- Tu salida DEBE ser estrictamente un JSON válido con la estructura indicada, sin texto adicional

ESTRUCTURA DE SALIDA JSON:
{
  "objeto_analizado": "String - nombre del objeto analizado",
  "busquedas_realizadas": ["String - query 1", "String - query 2", ...],
  "fuentes_encontradas": [
    {
      "fuente": "String - nombre de la plataforma/tienda",
      "precio": "String - precio encontrado con su moneda",
      "estado": "String - estado del objeto en esa venta",
      "url_referencia": "String o null"
    }
  ],
  "rango_precio_mercado": {
    "minimo": "String - precio mínimo en EUR",
    "medio": "String - precio medio/típico en EUR",
    "maximo": "String - precio máximo en EUR"
  },
  "nivel_demanda": "alta | media | baja | desconocida",
  "confianza_analisis": "alta | media | baja",
  "notas_analista": "String - observaciones relevantes para el tasador"
}"""


# Agente principal
def analizar_mercado(nombre_objeto: str, descripcion_adicional: str = "") -> dict:
    """
    Punto de entrada principal del Market Analyst Agent.

    Parámetros
    ----------
    nombre_objeto : str
        Nombre del objeto a analizar (e.g. "reloj de bolsillo Longines 1920").
    descripcion_adicional : str, opcional
        Detalles extra del objeto (estado, marcas, materiales, etc.)

    Retorna
    -------
    dict
        Diccionario con el análisis de mercado estructurado.
    """
    # Instanciar el modelo dentro de la función.
    modelo = BedrockModel(
        model_id=settings.llm_model_id_medium,
        region_name=settings.aws_region,
        temperature=0.2,
    )

    agente = Agent(
        model=modelo,
        system_prompt=SYSTEM_PROMPT,
        tools=[web_search, get_current_date],
    )

    prompt_usuario = f"""Analiza el mercado para el siguiente objeto:

OBJETO: {nombre_objeto}
"""
    if descripcion_adicional:
        prompt_usuario += f"\nDESCRIPCIÓN ADICIONAL: {descripcion_adicional}\n"

    prompt_usuario += """
Realiza las búsquedas necesarias y devuelve ÚNICAMENTE el JSON de análisis de mercado,
sin texto adicional ni bloques de código markdown."""

    texto_respuesta: str = ""

    try:
        respuesta = agente(prompt_usuario)

        texto_respuesta = (
            str(respuesta.message) if hasattr(respuesta, "message") else str(respuesta)
        )

        # Limpiar posibles bloques de código markdown (```json ... ```)
        texto_limpio = texto_respuesta.strip()
        if texto_limpio.startswith("```"):
            lineas = texto_limpio.split("\n")
            texto_limpio = "\n".join(
                lineas[1:-1] if lineas[-1] == "```" else lineas[1:]
            )

        return json.loads(texto_limpio)

    except json.JSONDecodeError as e:
        print(f"Error al parsear JSON del Market Analyst Agent: {e}")
        preview = (
            texto_respuesta[:500]
            if isinstance(texto_respuesta, str)
            else str(texto_respuesta)
        )
        print(f"Respuesta recibida: {preview}")
        return _respuesta_error(nombre_objeto, f"Error al parsear respuesta: {e}")

    except Exception as e:
        print(f"Error crítico en el Market Analyst Agent: {e}")
        return _respuesta_error(nombre_objeto, str(e))


# Exposicion como tool para el orquestador
@tool
def market_analyst_tool(nombre_objeto: str, descripcion_adicional: str = "") -> str:
    """
    Herramienta que expone el Market Analyst Agent al orquestador.

    Investiga el mercado actual para un objeto dado y devuelve un análisis
    de precios en formato JSON con rangos de valor.

    Parámetros
    ----------
    nombre_objeto : str
        Nombre del objeto a analizar.
    descripcion_adicional : str, opcional
        Descripción adicional del objeto (estado, marcas, materiales, etc.)
    """
    resultado = analizar_mercado(nombre_objeto, descripcion_adicional)
    return json.dumps(resultado, ensure_ascii=False, indent=2)


# Helper de error para mantener la estructura de salida en caso de que falle
def _respuesta_error(nombre_objeto: str, motivo: str) -> dict:
    """Devuelve una respuesta de error con la estructura estándar del agente."""
    return {
        "objeto_analizado": nombre_objeto,
        "busquedas_realizadas": [],
        "fuentes_encontradas": [],
        "rango_precio_mercado": {
            "minimo": "No disponible",
            "medio": "No disponible",
            "maximo": "No disponible",
        },
        "nivel_demanda": "desconocida",
        "confianza_analisis": "baja",
        "notas_analista": f"Error interno del sistema de análisis: {motivo}",
    }


# Ejecución directa para pruebas
if __name__ == "__main__":
    import pprint

    resultado = analizar_mercado(
        nombre_objeto="reloj de bolsillo j.w. tucker",
        descripcion_adicional="reloj de bolsillo antiguo j.w. tucker gold hunter de 1860, san francisco",
    )
    pprint.pprint(resultado)
