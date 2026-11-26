import os
import re
import base64
import time
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
    fecha: date | None = Field(
        default=None,
        description="Fecha del gasto en formato YYYY-MM-DD, por defecto la fecha actual"
    )
    concepto: Categorias = Field(
        default = Categorias.Otros,
        description="Motivo del gasto"
    )
    monto: float | None = Field(
        default = None,
        ge= 0,
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


