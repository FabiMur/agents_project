import json
import boto3

from src.tools.web_search import web_search
from config.settings import settings

bedrock_client = boto3.client("bedrock-runtime", region_name=settings.aws_region)


def investigar_precio_mercado(nombre_objeto: str) -> dict:
    """
    1. Usa la herramienta de busqueda web para buscar el precio.
    2. Envia los resultados crudos a Claude para que los analice.
    3. Devuelve un JSON estructurado con el rango de precios.
    """

    # 1. Ejecutar la herramienta
    query_busqueda = f"historia caracteristicas rareza coleccionismo {nombre_objeto}"
    print(f"Buscando en internet: {query_busqueda}")

    # Llamamos a la funcion de web_search
    resultados_web_crudos = web_search(query_busqueda, max_results=5)

    # 2. Preparar el prompt para la IA con los datos de internet incrustados
    system_prompt = """Eres el "Investigador Jefe e Historiador" de una prestigiosa casa de empeños.
    Tu única misión es leer resultados crudos de internet sobre un objeto y redactar un informe enciclopédico, detallado y fascinante sobre él.

    REGLAS ESTRICTAS:
    - NO menciones precios, estimaciones económicas ni valores monetarios. Esa es tarea de otro departamento.
    - Céntrate en: origen histórico, materiales, fabricante, por qué es buscado por coleccionistas, años de producción y características clave para identificar su autenticidad.
    - Tu salida DEBE ser estrictamente un JSON válido con esta estructura exacta, sin texto fuera del JSON:
    {
      "resumen_extenso": "Un texto de 2 a 3 párrafos muy rico en detalles históricos y técnicos.",
      "palabras_clave_identificacion": ["lista", "de", "detalles", "para", "autenticar"],
      "fuentes_usadas": ["lista", "de", "sitios web proporcionados en los resultados"]
    }"""

    prompt_usuario = f"""
    Objeto a tasar: {nombre_objeto}

    Resultados crudos de la busqueda en internet:
    {resultados_web_crudos}

    Analiza estos datos, extrae todo el jugo historico/tecnico y devuelve UNICAMENTE el JSON solictado.
    """

    body = json.dumps(
        {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1500,
            "temperature": 0.4,
            "system": system_prompt,
            "messages": [{"role": "user", "content": prompt_usuario}],
        }
    )

    try:
        # Usamos Claude 3 Haiku o Sonnet
        response = bedrock_client.invoke_model(
            modelId=settings.llm_model_id_medium, body=body
        )

        response_body = json.loads(response.get("body").read())
        texto_respuesta = response_body.get("content")[0].get("text")

        # Extraemos el JSON (a veces los modelos meten ```json al principio)
        if "```json" in texto_respuesta:
            texto_respuesta = (
                texto_respuesta.split("```json")[1].split("```")[0].strip()
            )

        resultado_diccionario = json.loads(texto_respuesta)
        return resultado_diccionario

    except Exception as e:
        print(f"Error critico en el Agente de Investigación: {e}")
        # Fallback de seguridad por si falla la API o el parseo
        return {
            "resumen_mercado": "Hubo un error al buscar en internet. Se asume un valor simbólico por defecto.",
            "fuentes_usadas": ["Ninguna"],
        }
