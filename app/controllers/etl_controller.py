from fastapi import APIRouter, status

from app.services.etl_service import extraer_productos, resetear_sistema, transformar_y_cargar
from app.views.schemas import ExtraccionRequest, ExtraccionResponse, ResetResponse, TransformacionResponse


router = APIRouter()


@router.post(
    "/extraer",
    response_model=ExtraccionResponse,
    status_code=status.HTTP_201_CREATED,
)
def extraer(request: ExtraccionRequest):
    return extraer_productos(request.cantidad)


@router.post("/transformar", response_model=TransformacionResponse)
def transformar():
    return transformar_y_cargar()


@router.delete("/reset", response_model=ResetResponse)
def reset():
    return resetear_sistema()