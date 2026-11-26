import os
import re
import base64
import time
from typing import Any, Dict, Optional
from datetime import date
from enum import Enum
from pydantic import BaseModel, Field, ValidationError, field_validator, model_validator

## Entrada
class FormatoImg(str,Enum):
    JPEG = "image/jpeg"
    PNG= "image/png"
    WEBP= "image/webp"
    PDF ="application/pdf"


class Entrada(BaseModel):
    mime_type: FormatoImg = Field(
        ...,
        description="MIME type recibido"
    )
    size: int = Field(
        ...,
        ge=10_000,
        le=15_000_000,
        description="Tamaño del archivo"
    )
    nombre_archivo: str = Field(...,
        max_length=255,
        min_length=3,
        description="Nombre del archivo"
    )
    @model_validator(mode="after")
    def validar_archivo(self) ->"Entrada":
        #re para capturar la extension
        match = re.search(r"\.([a-zA-Z0-9]+)$", self.nombre_archivo)
        if not match:
            raise ValueError(f"El archivo {self.nombre_archivo} no tiene una extension valida")

        extension = match.group(1).lower()

        #mapeo de MIME Type
        extensionesValidas = {
            FormatoImg.JPEG: {"jpg","jpeg"},
            FormatoImg.PNG: {"png"},
            FormatoImg.WEBP: {"webp"},
            FormatoImg.PDF: {"pdf"}
        }
        permitidas = extensionesValidas.get(self.mime_type, set())
        if extension not in permitidas:
            raise ValueError(f"Extension inconsistente")
        
        return self

## Salida
class Categorias(str, Enum):
    Almuerzo = "Almuerzo"
    Combustible = "Combustible"
    Hospedaje = "Hospedaje"
    Otros = "Otros"

class Salida(BaseModel):
    fecha: date = Field(
        default_factory=date.today(),
        description="Fecha del gasto en formato YYYY-MM-DD, por defecto la fecha actual"
    )
    concepto: Categorias = Field(
        default = Categorias.Otros,
        description="Motivo del gasto"
    )
    monto: float | None = Field(
        default = None,
        gt= 0,
        description="Monto del gasto"
    )
    observaciones: str | None = Field(
        default=None,
        min_length = 3,
        max_length = 100,
        description= "Detalles o aclaraciones"
    )
    confirmacion: str = Field(
        description= "Pedido de confirmacion para el usuario"
    )

    @field_validator("fecha")
    @classmethod
    def ValidarFecha(cls,v: date) -> date:
        if(v > date.today()):
            raise ValueError("La fecha del comprobante no puede ser futura")
        return v


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

    