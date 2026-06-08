from fastapi import FastAPI

from app.controllers import analitica_controller, etl_controller


app = FastAPI(
    title="Laboratorio ETL - DummyJSON Products",
    description="Pipeline ETL con FastAPI, MongoDB, MySQL y analitica dinamica.",
    version="1.0.0",
)

app.include_router(etl_controller.router, prefix="/api/v1/etl", tags=["ETL"])
app.include_router(analitica_controller.router, prefix="/api/v1", tags=["Analitica"])


@app.get("/")
def inicio():
    return {
        "mensaje": "API del Laboratorio ETL activa",
        "endpoints": [
            "POST /api/v1/etl/extraer",
            "POST /api/v1/etl/transformar",
            "DELETE /api/v1/etl/reset",
            "GET /api/v1/analitica/columna/{nombre}",
            "GET /api/v1/perfil/{id}",
        ],
    }