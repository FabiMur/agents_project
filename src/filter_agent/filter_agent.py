import json
import base64
import boto3

# El Orquestador deberia manejar la inicializacion del cliente,
# pero lo ponemos aqui para que el modulo sea independiente.
bedrock_client = boto3.client("bedrock-runtime", region_name="eu-west-1")


def codificar_imagen(ruta_imagen):
    """Convierte la imagen local a bytes y especifica el media_type."""
    with open(ruta_imagen, "rb") as archivo_imagen:
        imagen_bytes = archivo_imagen.read()
        imagen_base64 = base64.b64encode(imagen_bytes).decode("utf-8")

        media_type = "image/jpeg"
        if ruta_imagen.lower().endswith(".png"):
            media_type = "image/png"

        return imagen_base64, media_type


def analizar_antiguedad(ruta_imagen: str) -> dict:
    """
    Recibe la ruta de una imagen, la envia a Claude 3
    y devuelve un diccionario Python garantizado.
    """

    imagen_base64, media_type = codificar_imagen(ruta_imagen)

    # System Prompt exacto para forzar el comportamiento de filtro
    system_prompt = """Eres el "Recepcionista y Filtro de Seguridad" de una prestigiosa casa de empeños y tasación de antigüedades.
    Tienes un ojo clinico para identificar rapidamente que objetos tienen valor de coleccion o reventa y cuales son basura o articulos prohibidos.

    REGLAS:
    - NO des una estimacion de precio.
    - Si la imagen contiene personas, material explicito o armas modernas, es "no tasable".
    - Si es comida, basura o un objeto cotidiano sin valor coleccionable, es "no tasable".
    - Tu salida DEBE ser estrictamente un JSON valido con esta estructura exacta, sin texto adicional:
    {
      "es_tasable": booleano (true o false),
      "motivo_rechazo": "String o null",
      "nombre_objeto_detectado": "String o null",
      "mensaje_usuario": "Mensaje para el usuario. Si es tasable, pregunta: 'Parece que nos traes un [objeto]. ¿Es este el producto que deseas que nuestro equipo tase hoy?'"
    }"""

    # Estructura de mensajes para Claude 3
    body = json.dumps(
        {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 500,
            "temperature": 0.1,  # Baja temperatura para JSON estricto
            "system": system_prompt,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": imagen_base64,
                            },
                        },
                        {
                            "type": "text",
                            "text": "Analiza esta imagen y devuelve unicamente el JSON correspondiente.",
                        },
                    ],
                }
            ],
        }
    )

    try:
        # Llamada a Claude 3 Haiku
        response = bedrock_client.invoke_model(
            modelId="eu.anthropic.claude-3-haiku-20240307-v1:0", body=body
        )

        response_body = json.loads(response.get("body").read())
        texto_respuesta = response_body.get("content")[0].get("text")

        # Parsear el string devuelto por Claude a un diccionario de Python
        resultado_diccionario = json.loads(texto_respuesta)
        return resultado_diccionario

    except Exception as e:
        print(f"Error critico en el Agente Filtro (Bedrock): {e}")
        return {
            "es_tasable": False,
            "motivo_rechazo": "Error interno del sistema visual.",
            "nombre_objeto_detectado": None,
            "mensaje_usuario": "Lo siento, mis gafas de tasar se han empañado. No he podido procesar la imagen. ¿Podrias subirla de nuevo?",
        }
