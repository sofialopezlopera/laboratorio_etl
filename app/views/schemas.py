from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ExtraccionRequest(BaseModel):
    cantidad: int = Field(..., description="Cantidad de productos a extraer.")


class ExtraccionResponse(BaseModel):
    mensaje: str
    registros_guardados: int
    fuente: str
    status: int


class TransformacionResponse(BaseModel):
    mensaje: str
    registros_procesados: int
    tabla_destino: str
    status: int


class ResetResponse(BaseModel):
    mensaje: str
    mongo_docs_eliminados: int
    mysql_rows_eliminadas: int
    status: int


class PerfilDualResponse(BaseModel):
    id: int
    vista_mongo: Optional[Dict[str, Any]]
    vista_sql: Optional[Dict[str, Any]]
    warning: Optional[str] = None