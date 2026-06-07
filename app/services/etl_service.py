from typing import Any, Dict, List

import pandas as pd

from app.database import get_mongo_collection

def obtener_productos_desde_mongo() -> List[Dict[str, Any]]:
    collection = get_mongo_collection()
    return list(collection.find({}).sort("_id", 1))


def transformar_productos(documentos: List[Dict[str, Any]]) -> pd.DataFrame:
    df = pd.json_normalize(documentos)
    df_sql = pd.DataFrame()
    
    df_sql["ancho"] = _numero(df, "dimensions.width", float)
    df_sql["alto"] = _numero(df, "dimensions.height", float)
    df_sql["profundidad"] = _numero(df, "dimensions.depth", float)
    
    return df_sql


def _serie(df: pd.DataFrame, columna: str, valor_por_defecto: Any) -> pd.Series:
    if columna in df.columns:
        return df[columna]
    return pd.Series([valor_por_defecto] * len(df))

def _numero(df: pd.DataFrame, columna: str, tipo):
    serie = pd.to_numeric(_serie(df, columna, 0), errors="coerce").fillna(0)
    return serie.astype(tipo)
