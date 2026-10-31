import re
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from api.config import MAX_CARACTERES


class ResenaEntrada(BaseModel):
    texto: str = Field(..., max_length=MAX_CARACTERES, examples=["El hotel estaba sucio y NO lo recomiendo para nada"])

    @field_validator('texto')
    @classmethod
    def validar_texto(cls, valor: str) -> str:
        valor = valor.strip()
        if not valor:
            raise ValueError("La reseña no puede estar vacía.")
        if not re.search(r'[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ]', valor):
            raise ValueError("La reseña debe contener al menos una palabra.")
        return valor


class PasosNLP(BaseModel):
    texto_original: str
    paso1_normalizado: str
    paso2_tokens: list[str]
    paso3_sin_stopwords: list[str]
    paso3_stopwords_eliminadas: list[str]
    paso3_negaciones_conservadas: list[str]
    paso4_stemming: list[str]
    paso5_resultado: str


class PrediccionRespuesta(BaseModel):
    sentimiento: str = Field(..., examples=["Negativo"])
    probabilidad: float = Field(..., ge=0, le=1, examples=[0.987])
    porcentaje: str = Field(..., examples=["98.7%"])
    probabilidades: dict[str, float]
    modo: str = Field(..., examples=["real"])
    pasos: PasosNLP


class EstadoRespuesta(BaseModel):
    estado: str
    modelo_cargado: bool
    modo: str
    activo_desde: str


class MetricasRespuesta(BaseModel):
    # metricas.json puede traer más campos (matriz, comparaciones...); se devuelven tal cual
    model_config = ConfigDict(extra='allow')

    modo: str
    modelo: str
    accuracy: float
    f1_weighted: Optional[float] = None
    mensaje: Optional[str] = None
