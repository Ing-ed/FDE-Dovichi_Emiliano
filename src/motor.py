from datetime import date
from enum import Enum
from pydantic import BaseModel, Field

## Salida
class Categorias(str, Enum):
    Almuerzo = "Almuerzo"
    Combustible = "Combustible"
    Hospedaje = "Hospedaje"
    Otros = "Otros"

class SalidaGastos(BaseModel):
    fecha: date | None = Field(
        default:None,
        descriptcion="Fecha del gasto en formato DD-MM-YYYY"
    )
    Concepto: Categorias = Field(
        descriptcion="Motivo del gasto"
    )
    Monto: float | None = Field(
        default = None,
        gt= 0,
        descriptcion="Monto del gasto"
    )
    observaciones: str | None = Field(
        default=None,
        max_length = 100,
        descriptcion= "Detalles o aclaraciones"
    )
    Confirmacion: str = Field(
        descriptcion= "Pedido de confirmacion para el usuario"
    )

class FormatoImg(str,enum):
    JPEG = "image/jpeg
    PNG= "image/png"
    WEBP= "image/webp"
    PDF ="application/pdf"

class Comprobante(BaseModel):
    mime_type: FormatoImg = Field(
        ...,
        descriptcion="MIME type recibido"
    )
    Size: int = Field(
        ...,
        ge=10_000,
        le=15_000_000,
        descriptcion="Tamaño del archivo"
    )
    nombre_archivo: str = Field(..., max_length=255)