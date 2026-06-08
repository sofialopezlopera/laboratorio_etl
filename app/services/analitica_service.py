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

def _analizar_categorica(nombre: str, valores: List[Any], nulos: int) -> Dict[str, Any]:
    serie = pd.Series([str(valor) for valor in valores])
    distribucion = serie.value_counts().to_dict()

    return {
        "columna": nombre,
        "tipo": "categorica",
        "valores_unicos": int(serie.nunique()) if not serie.empty else 0,
        "distribucion": distribucion,
        "valor_mas_comun": serie.mode().iloc[0] if not serie.empty else None,
        "nulos": nulos,
    }

def _analizar_numerica(nombre: str, valores: List[Any], nulos: int) -> Dict[str, Any]:
    serie = pd.Series(valores, dtype="float64")

    if serie.empty:
        return {
            "columna": nombre,
            "tipo": "numerica",
            "min": None,
            "max": None,
            "promedio": None,
            "mediana": None,
            "desviacion_std": None,
            "nulos": nulos,
        }

    return {
        "columna": nombre,
        "tipo": "numerica",
        "min": round(float(serie.min()), 2),
        "max": round(float(serie.max()), 2),
        "promedio": round(float(serie.mean()), 2),
        "mediana": round(float(serie.median()), 2),
        "desviacion_std": round(float(serie.std(ddof=0)), 2),
        "nulos": nulos,
    }