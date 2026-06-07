from typing import Any, Dict, List

from app.database import get_mongo_collection

def obtener_productos_desde_mongo() -> List[Dict[str, Any]]:
    collection = get_mongo_collection()
    return list(collection.find({}).sort("_id", 1))