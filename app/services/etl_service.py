from typing import Any, Dict, List

import pandas as pd
import requests
from fastapi import HTTPException
from sqlalchemy import func, select, text
from sqlalchemy.dialects.mysql import insert as mysql_insert

from app.config import settings
from app.database import SessionLocal, create_sql_tables, get_mongo_collection
from app.models.productos_sql import ProductoSQL


FUENTE = "DummyJSON Products API"
TABLA_DESTINO = ProductoSQL.__tablename__


def extraer_productos(cantidad: int) -> Dict[str, Any]:
    if cantidad <= 0:
        raise HTTPException(
            status_code=400,
            detail="La cantidad debe ser un numero entero mayor que cero.",
        )

    productos = _descargar_productos(cantidad)
    collection = get_mongo_collection()

    for producto in productos:
        producto_id = producto.get("id")
        if producto_id is None:
            continue
        documento = dict(producto)
        documento["_id"] = int(producto_id)
        collection.replace_one({"_id": int(producto_id)}, documento, upsert=True)

    return {
        "mensaje": "Datos extraidos exitosamente",
        "registros_guardados": len(productos),
        "fuente": FUENTE,
        "status": 201,
    }


def transformar_y_cargar() -> Dict[str, Any]:
    documentos = obtener_productos_desde_mongo()
    if not documentos:
        raise HTTPException(
            status_code=400,
            detail="No hay productos en MongoDB. Ejecute primero /api/v1/etl/extraer.",
        )

    try:
        dataframe = transformar_productos(documentos)
        registros = cargar_productos_en_mysql(dataframe)
    except Exception as e:
        # Esto es lo que hace que el commit sea "bueno"
        raise HTTPException(
            status_code=500,
            detail=f"Error crítico durante la transformación o carga: {str(e)}"
        )

    return {
        "mensaje": "Pipeline finalizado",
        "registros_procesados": registros,
        "tabla_destino": TABLA_DESTINO,
        "status": 200,
    }


def resetear_sistema() -> Dict[str, Any]:
    collection = get_mongo_collection()
    mongo_docs_eliminados = collection.count_documents({})
    collection.delete_many({})

    create_sql_tables()
    with SessionLocal() as session:
        mysql_rows_eliminadas = session.execute(
            select(func.count()).select_from(ProductoSQL)
        ).scalar_one()
        session.execute(text(f"TRUNCATE TABLE {TABLA_DESTINO}"))
        session.commit()

    return {
        "mensaje": "Sistema reseteado correctamente",
        "mongo_docs_eliminados": int(mongo_docs_eliminados),
        "mysql_rows_eliminadas": int(mysql_rows_eliminadas),
        "status": 200,
    }


def obtener_productos_desde_mongo() -> List[Dict[str, Any]]:
    collection = get_mongo_collection()
    return list(collection.find({}).sort("_id", 1))


def transformar_productos(documentos: List[Dict[str, Any]]) -> pd.DataFrame:
    df = pd.json_normalize(documentos)
    df_sql = pd.DataFrame()

    id_series = _serie_id(df)
    df_sql["id_producto"] = pd.to_numeric(id_series, errors="coerce").fillna(0).astype(int)
    df_sql["titulo"] = _texto(df, "title", 255)
    df_sql["categoria"] = _texto(df, "category", 100)
    df_sql["marca"] = _texto(df, "brand", 120)
    df_sql["precio"] = _numero(df, "price", float)
    df_sql["rating"] = _numero(df, "rating", float)
    df_sql["stock"] = _numero(df, "stock", int)
    df_sql["estado_disponibilidad"] = _texto(df, "availabilityStatus", 80)
    df_sql["peso"] = _numero(df, "weight", int)
    df_sql["ancho"] = _numero(df, "dimensions.width", float)
    df_sql["alto"] = _numero(df, "dimensions.height", float)
    df_sql["profundidad"] = _numero(df, "dimensions.depth", float)

    reviews = _serie(df, "reviews", [])
    df_sql["cantidad_reviews"] = reviews.apply(_cantidad_reviews).astype(int)
    df_sql["promedio_reviews"] = reviews.apply(_promedio_reviews).astype(float)

    fechas = pd.to_datetime(_serie(df, "meta.createdAt", None), errors="coerce", utc=True)
    df_sql["fecha_creacion"] = fechas.dt.date.where(fechas.notna(), None)

    descuento = pd.to_numeric(
        _serie(df, "discountPercentage", 0), errors="coerce"
    ).fillna(0)
    stock = pd.to_numeric(_serie(df, "stock", 0), errors="coerce").fillna(0)
    df_sql["tiene_descuento"] = descuento.gt(0)
    df_sql["stock_bajo"] = stock.lt(10)

    return df_sql


def cargar_productos_en_mysql(dataframe: pd.DataFrame) -> int:
    create_sql_tables()
    registros = [_normalizar_registro(registro) for registro in dataframe.to_dict("records")]

    if not registros:
        return 0

    insert_stmt = mysql_insert(ProductoSQL).values(registros)
    update_columns = {
        column.name: insert_stmt.inserted[column.name]
        for column in ProductoSQL.__table__.columns
        if column.name != "id_producto"
    }
    upsert_stmt = insert_stmt.on_duplicate_key_update(**update_columns)

    with SessionLocal() as session:
        session.execute(upsert_stmt)
        session.commit()

    return len(registros)


def _descargar_productos(cantidad: int) -> List[Dict[str, Any]]:
    productos: List[Dict[str, Any]] = []
    skip = 0
    total = None

    while len(productos) < cantidad:
        limite = min(100, cantidad - len(productos))

# Implementación de paginación para evitar errores de memoria
        params = {"limit": limite, "skip": skip}

        try:
            response = requests.get(
                settings.dummyjson_products_url,
                params=params,
                timeout=settings.dummyjson_timeout_seconds,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise HTTPException(
                status_code=502,
                detail=f"No fue posible consultar DummyJSON: {exc}",
            ) from exc

        payload = response.json()
        lote = payload.get("products", [])
        total = payload.get("total", total)

        if not lote:
            break

        productos.extend(lote)
        skip += len(lote)

        if total is not None and skip >= int(total):
            break

    return productos[:cantidad]


def _serie(df: pd.DataFrame, columna: str, valor_por_defecto: Any) -> pd.Series:
    if columna in df.columns:
        return df[columna]
    return pd.Series([valor_por_defecto] * len(df))


def _serie_id(df: pd.DataFrame) -> pd.Series:
    if "_id" in df.columns:
        return df["_id"]
    if "id" in df.columns:
        return df["id"]
    return pd.Series([0] * len(df))


def _texto(df: pd.DataFrame, columna: str, longitud: int) -> pd.Series:
    return _serie(df, columna, "N/A").fillna("N/A").astype(str).str.slice(0, longitud)


def _numero(df: pd.DataFrame, columna: str, tipo):
    serie = pd.to_numeric(_serie(df, columna, 0), errors="coerce").fillna(0)
    return serie.astype(tipo)


def _cantidad_reviews(valor: Any) -> int:
    return len(valor) if isinstance(valor, list) else 0


def _promedio_reviews(valor: Any) -> float:
    if not isinstance(valor, list):
        return 0.0

    ratings = [
        review.get("rating")
        for review in valor
        if isinstance(review, dict) and review.get("rating") is not None
    ]
    if not ratings:
        return 0.0
    return round(sum(ratings) / len(ratings), 2)


def _normalizar_registro(registro: Dict[str, Any]) -> Dict[str, Any]:
    limpio = {}
    for clave, valor in registro.items():
        if pd.isna(valor):
            limpio[clave] = None
        elif hasattr(valor, "item"):
            limpio[clave] = valor.item()
        else:
            limpio[clave] = valor
    return limpio