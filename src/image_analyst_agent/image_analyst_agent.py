import json
import base64
import boto3

from config.settings import settings

bedrock_client = boto3.client(
    "bedrock-runtime",
    region_name=settings.aws_region,
)


def codificar_imagen(imagen_bytes: bytes, nombre_archivo: str = "") -> tuple[str, str]:
    """Convierte bytes de imagen a base64 + detecta media_type."""
    imagen_base64 = base64.b64encode(imagen_bytes).decode("utf-8")
    media_type = (
        "image/png" if nombre_archivo.lower().endswith(".png") else "image/jpeg"
    )
    return imagen_base64, media_type


def analizar_imagen_detallado(imagen_bytes: bytes, nombre_archivo: str = "") -> dict:
    """
    Analiza la imagen en detalle.
    Devuelve una descripción concreta, breve y útil para el historiador.
    """

    imagen_base64, media_type = codificar_imagen(imagen_bytes, nombre_archivo)
    system_prompt = """
Eres un "Analista Experto en Identificación y Validación de Objetos" en una casa de empeños profesional.

Tu tarea es:
1. Determinar si el objeto es tasable.
2. Identificar el objeto con la mayor precisión posible.
3. Dar una descripción breve y útil.

REGLAS CRÍTICAS:
- Si la imagen contiene personas, material explicito o armas modernas, es "no tasable".
- Si es comida, basura o un objeto cotidiano sin valor coleccionable, a no ser que haya justificación, es "no tasable".
- Prioriza SIEMPRE la decisión de "es_tasable" antes de cualquier análisis detallado.
- Si determinas que el objeto NO es tasable, NO continúes con la identificación detallada.
    - En ese caso, devuelve directamente el JSON con:
    - "es_tasable": false
    - "motivo_rechazo": explicación clara
    - El resto de campos como valores null o vacíos.

- Si el objeto si es tasable entonces se continua.
- Si el objeto puede tener múltiples variantes, menciona la más probable, pero también se añadirán las otras variantes en la respuesta.
- Si no puedes identificar detalles concretos (año exacto, modelo específico, etc.), di claramente que es una estimación.
- NO inventes información. Es mejor ser GENERAL que incorrecto.
- NO des precios.
- NO hagas suposiciones sin evidencia visual clara.

SALIDA (JSON estricto):

{
  "es_tasable": true/false,
  "motivo_rechazo": "string o null",
  "nombre_objeto_refinado": "string o null",
  "descripcion_corta": "string o null",
  "confianza": "alta | media | baja",
  "posibles_variantes": ["string", "string"]
}

EJEMPLO:

{
  "es_tasable": true,
  "motivo_rechazo": null,
  "nombre_objeto_refinado": "Moneda romana de bronce (posiblemente siglo III)",
  "descripcion_corta": "Moneda antigua con desgaste visible y características numismáticas.",
  "confianza": "media",
  "posibles_variantes": ["Moneda griega antigua"]
}
"""

    body = json.dumps(
        {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 500,
            "temperature": 0.2,
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
                            "text": "Analiza esta imagen y devuelve únicamente el JSON solicitado.",
                        },
                    ],
                }
            ],
        }
    )

    try:
        response = bedrock_client.invoke_model(
            modelId=settings.llm_model_id_medium,
            body=body,
        )

        response_body = json.loads(response.get("body").read())
        texto_respuesta = response_body.get("content")[0].get("text")

        resultado = json.loads(texto_respuesta)
        return resultado

    except Exception as e:
        print(f"Error en Image Analyst Agent: {e}")

        return {
            "es_tasable": False,
            "motivo_rechazo": "Error interno del sistema visual",
            "nombre_objeto_refinado": None,
            "descripcion_corta": "No se pudo analizar la imagen.",
            "confianza": "baja",
            "posibles_variantes": [],
        }
