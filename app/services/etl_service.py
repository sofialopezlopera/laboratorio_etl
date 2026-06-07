from typing import Any, Dict, List

import pandas as pd

from app.database import get_mongo_collection

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