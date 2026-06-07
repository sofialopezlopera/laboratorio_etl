from typing import Any, Dict, List

import pandas as pd

from app.database import get_mongo_collection

def obtener_productos_desde_mongo() -> List[Dict[str, Any]]:
    collection = get_mongo_collection()
    return list(collection.find({}).sort("_id", 1))

def transformar_productos(documentos: List[Dict[str, Any]]) -> pd.DataFrame:
    df = pd.json_normalize(documentos)
    df_sql = pd.DataFrame()
    return df_sql
