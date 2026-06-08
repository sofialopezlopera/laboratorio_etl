from datetime import date, datetime
from typing import Any, Dict, List

import pandas as pd
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.sql.sqltypes import Boolean, Date, DateTime, Float, Integer, Numeric

from app.database import SessionLocal, create_sql_tables, get_mongo_collection
from app.models.productos_sql import ProductoSQL


def analizar_columna(nombre: str) -> Dict[str, Any]:
    create_sql_tables()
    columnas_validas = list(ProductoSQL.__table__.columns.keys())

    if nombre not in columnas_validas:
        raise HTTPException(
            status_code=400,
            detail={
                "mensaje": f"La columna '{nombre}' no existe en productos_master.",
                "columnas_validas": columnas_validas,
            },
        )

    columna = ProductoSQL.__table__.columns[nombre]
    with SessionLocal() as session:
        valores = session.execute(select(columna)).scalars().all()

    nulos = sum(1 for valor in valores if valor is None)
    valores_validos = [valor for valor in valores if valor is not None]

    if isinstance(columna.type, Boolean):
        return _analizar_booleana(nombre, valores_validos, nulos)
    if isinstance(columna.type, (Date, DateTime)):
        return _analizar_fecha(nombre, valores_validos, nulos)
    if isinstance(columna.type, (Integer, Float, Numeric)):
        return _analizar_numerica(nombre, valores_validos, nulos)
    return _analizar_categorica(nombre, valores_validos, nulos)