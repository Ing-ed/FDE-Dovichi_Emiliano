import os
from src.contrato import Entrada, Salida, FormatoImg
from typing import Any, Dict, Optional
from pydantic import ValidationError


## codificar imagen
def CodificarImagen(rutaImagen:str) -> str:
    with open(rutaImagen, "rb") as f:
        return base64.b64Encode(f.read()).decode("utf-8")


## Procesamiento de datos
def ProcesarComprobante(rutaArchivo: str, mime_type: str = "image/jpeg") -> Dict[str, Any]:
    if(not os.path.exists(rutaArchivo)):
        return {
            "status":"ERROR",
            "msg": f'El archivo no existe en la ruta especifica'
        }
    try:
        tamañoBytes = os.path.getsize(rutaArchivo)
        nombre = os.path.basename(rutaArchivo)
        entrada = Entrada(
            mime_type=FormatoImg(mime_type),
            size = tamañoBytes,
            nombre_archivo = nombre
        )
    except (ValidationError,ValueError) as e:
        return {
            "status": "ERROR",
            "msg": e.errors() if isinstance(e,ValidationError) else str(e)
        }
    
    return{
        "status": "OK",
        "msg": "Archivos validados correctamente",
        "entrada":entrada.model_dump()
    }
    # img64 = CodificarImagen(rutaArchivo)
    # max_intentos = 2
    # inicio = time.time()

    