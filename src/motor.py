import os
import time
import base64
from src.contrato import Entrada, Salida, FormatoImg
from typing import Any, Dict, Optional
from pydantic import ValidationError
from google import genai
from google.genai import types
from google.genai.errors import ServerError
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

PROMPT = """sos un asistente de extraccion estructurada de comprobantes de gastos.
Analiza la imagen provista y extraé con precision:
fecha: fecha del comprobante(YYYY-MM-DD). Si no esta o no es legible, usa la fecha de hoy
concepto: De acuerdo al detalle del ticket, clasificalo estrictamente en Almuerzo, Combustible, Hospedaje, Otros
monto: total numerico del gasto, si no se distingue, usa null.
observaciones: Detalles escritos a mano en el ticket/factura"""


## codificar imagen
def CodificarImagen(rutaImagen:str) -> str:
    with open(rutaImagen, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


## Procesamiento de datos
def ProcesarComprobante(rutaArchivo: str, mime_type: str = "image/jpeg") -> Dict[str, Any]:
    """Envia la imagen a Gemini"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("No se encontro la API_KEY")
    
    try:
        entrada = Entrada(
            mime_type=FormatoImg(mime_type),
            size=os.path.getsize(rutaArchivo),
            nombre_archivo=os.path.basename(rutaArchivo)
        )
    except (ValidationError, ValueError) as e:
        return {"status": "ERROR_VALIDACION_ENTRADA", "detalles": str(e)}

    # client = genai.Client(api_key = api_key)
    client = OpenAI(api_key=api_key)
    im64 = CodificarImagen(rutaArchivo)
    with open(rutaArchivo, "rb") as f:
        image_bytes = f.read()
    
    inicio = time.time()
    try:
        # response = client.models.generate_content(
        response = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role":"system","content":PROMPT},
                {
                    "role":"user",
                    "content":[
                        {"type":"text", "text":"Extrae los datos estructurados del comprobante:"},
                        {
                            "type":"image_url",
                            "image_url":{"url":f"data:{entrada.mime_type.value};base64,{im64}"}
                        }
                    ]
                }
            ],
            response_format=Salida,
            temperature=0.1
        )
        latencia_ms = round((time.time() -inicio)*1000, 2)
        salida: Salida = response.choices[0].message.parsed
        return salida
    except ServerError as err:
        print("Error", err)

    