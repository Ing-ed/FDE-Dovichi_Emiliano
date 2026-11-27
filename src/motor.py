import os
import time
import base64
import cv2 as cv
from src.contrato import Entrada, Salida, FormatoImg
from typing import Any, Dict, Optional
from pydantic import ValidationError
from google import genai
from google.genai import types
from google.genai.errors import ServerError
from dotenv import load_dotenv
from openai import OpenAI, APIError

load_dotenv()

PROMPT = """sos un asistente de extraccion estructurada de comprobantes de gastos.
Analiza la imagen provista y extraé con precision:
fecha: fecha del comprobante(YYYY-MM-DD). Si no esta o no es legible, usa None.
hora: la hora del comprobante (HH:MM), figura al lado de la fecha normalmente, si no la encontras, usa None
concepto: De acuerdo al detalle del ticket, clasificalo estrictamente en Almuerzo, Desayuno, Cena teniendo en cuenta la hora siguiendo esta regla:
0:00 a 11:00 -> Desayuno
11:01 a 16:00 -> Almuerzo
16:01 a 19:00 -> Merienda
19:01 a 23:59 -> Cena

Ademas, estan las siguientes categorias que no dependen del horario: Combustible, Hospedaje, Otros.
monto: total numerico del gasto redondeado, si no se distingue, usa None.
"""


## codificar imagen
def CodificarImagen(rutaImagen:str) -> str:
    im = cv.imread(rutaImagen,cv.IMREAD_GRAYSCALE)
    if im is None:
        raise ValueError(f"No se pudo leer la imagen{rutaImagen}")
    im2 = cv.resize(im,(380,240),interpolation=cv.INTER_AREA)
    ok, buffer = cv.imencode(".jpg",im2,[int(cv.IMWRITE_JPEG_QUALITY), 85])
    if not ok:
        raise ValueError(f"No se pudo codificar la imagen")
    return base64.b64encode(buffer.tobytes()).decode("ascii")
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
                            "image_url":{"url":f"data:{entrada.mime_type.value};base64,{im64}"}, "detail":"low"
                        }
                    ]
                }
            ],
            response_format=Salida,
            temperature=0.1
        )
        latencia_ms = round((time.time() -inicio)*1000, 2)
        salida: Salida = response.choices[0].message.parsed
        in_tok = response.usage.prompt_tokens if response.usage else 0
        out_tok = response.usage.completion_tokens if response.usage else 0
        total_tok = response.usage.total_tokens if response.usage else (in_tok + out_tok)
        costo = (in_tok * 0.15 + out_tok * 0.6)/1_000_000

        return {
            "status":"OK",
            "salida":salida,
            "latencia_ms":latencia_ms,
            "in_tok":in_tok,
            "out_tok":out_tok,
            "total_tokens":total_tok,
            "costo":costo
        }
    except APIError as err:
        print("Error", err)

    