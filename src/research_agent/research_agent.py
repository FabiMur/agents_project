import json
import boto3

from src.tools.web_search import web_search

bedrock_client = boto3.client("bedrock-runtime", region_name="eu-west-1")


def investigar_precio_mercado(nombre_objeto: str) -> dict:
    """
    1. Usa la herramienta de busqueda web para buscar el precio.
    2. Envia los resultados crudos a Claude para que los analice.
    3. Devuelve un JSON estructurado con el rango de precios.
    """

    # 1. Ejecutar la herramienta
    query_busqueda = f"precio actual mercado subasta {nombre_objeto}"
    print(f"Buscando en internet: {query_busqueda}")

    # Llamamos a la funcion de web_search
    resultados_web_crudos = web_search(query_busqueda, max_results=5)

    # 2. Preparar el prompt para la IA con los datos de internet incrustados
    system_prompt = """Eres el "Analista Jefe de Mercado y Tasador Historico".
    Analiza los resultados de busqueda web proporcionados y extrae el valor de mercado.
    Tu salida DEBE ser estrictamente un JSON valido:
    {
      "rango_precio_minimo": numero,
      "rango_precio_maximo": numero,
      "confianza_datos": "Alta|Media|Baja",
      "resumen_mercado": "String detallando el contexto",
      "fuentes_usadas": ["web1", "web2"]
    }
    NO inventes precios. Si no hay datos, da tu mejor estimacion experta y marca confianza Baja."""

    prompt_usuario = f"""
    Objeto a tasar: {nombre_objeto}

    Resultados crudos de la busqueda en internet:
    {resultados_web_crudos}

    Analiza estos datos y devuelve UNICAMENTE el JSON.
    """

    body = json.dumps(
        {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 800,
            "temperature": 0.2,
            "system": system_prompt,
            "messages": [{"role": "user", "content": prompt_usuario}],
        }
    )

    try:
        # Usamos Claude 3 Haiku o Sonnet
        response = bedrock_client.invoke_model(
            modelId="eu.anthropic.claude-3-haiku-20240307-v1:0", body=body
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
        print(f"Error crítico en el Agente de Investigación: {e}")
        # Fallback de seguridad por si falla la API o el parseo
        return {
            "rango_precio_minimo": 10,
            "rango_precio_maximo": 50,
            "confianza_datos": "Baja",
            "resumen_mercado": "Hubo un error al buscar en internet. Se asume un valor simbólico por defecto.",
            "fuentes_usadas": ["Ninguna"],
        }
