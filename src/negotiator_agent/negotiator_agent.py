from pydantic import BaseModel, Field

negotiator_prompt = """
Eres el Agente Negociador de una Casa de Empeños de alto nivel. 
Tu especialidad es el "Storyselling" y la maximización de valor.

OBJETIVO: 
Transformar cualquier dato técnico, histórico o de mercado proporcionado por otros agentes en una estrategia de venta ganadora. 
Tu meta es maximizar el beneficio de la casa de empeños asegurando una rotación rápida del inventario.


TU TAREA ES GENERAR:
1. Puntos de Venta Únicos (USPs): Resalta lo que hace especial a este objeto frente a otros iguales, .
3. Estrategia de Cierre: Sugiere tácticas de negociación (ej. margen de descuento aceptable o "anclaje" de precio).

REGLAS DE ORO:
- Nunca inventes datos técnicos; usa lo que te proporcionan los otros agentes. Es decir, conecta el estado físico con el contexto y el valor.
- SEGMENTACIÓN: 
   - Colección/Lujo: Enfócate en la escasez, la historia y la inversión a largo plazo.
   - Funcionales (Tech/Herramientas): Enfócate en la utilidad inmediata, durabilidad y ahorro frente a PVP nuevo.
- El "Precio de Salida" debe servir como un ancla psicológica para el regateo, pero siempre deja espacio para la negociación.

FORMATO DE SALIDA:
Debes responder estrictamente en el formato JSON estructurado solicitado:
"""


class InformeNegociacion(BaseModel):
    narrativa_valor: str = Field(
        description="Narrativa persuasiva que integra el estado, historia y utilidad del objeto."
    )
    precio_salida_anclaje: float = Field(
        description="Precio inicial sugerido para mostrar al público (alto)."
    )
    precio_objetivo_venta_rapida: float = Field(
        description="Precio ideal al que queremos cerrar la transacción hoy."
    )
    limite_negociacion_minimo: float = Field(
        description="El precio más bajo aceptable antes de perder margen operativo."
    )
    canal_recomendado: str = Field(
        description="El mejor lugar para venderlo (ej. eBay, Vitrina, Subasta)."
    )
    tactica_negociacion: str = Field(
        description="Sugerencia de cómo manejar al comprador (ej. resaltar pátina, mencionar escasez)."
    )


# INFORME A DEVOLVER:

# Narrativa de Valor: Devolver una narrativa convincente que resalte los aspectos únicos del objeto.

# Estrategia de Precio:

# - Precio de Salida (Anclaje): $[Valor sugerido]

# - Precio Objetivo (Venta rápida): $[Valor sugerido]

# - Límite de Negociación: $[Mínimo aceptable]

# - Canal Recomendado: [Ej: Subasta especializada, Marketplace local, Vitrina física...]
