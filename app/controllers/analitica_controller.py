from typing import Any, Dict

from fastapi import APIRouter

from app.services.analitica_service import analizar_columna, obtener_perfil_dual
from app.views.schemas import PerfilDualResponse


router = APIRouter()


@router.get("/analitica/columna/{nombre}", response_model=Dict[str, Any])
def analizar(nombre: str):
    return analizar_columna(nombre)

@router.get("/perfil/{id}", response_model=PerfilDualResponse)
def perfil(id: int):
    return obtener_perfil_dual(id)