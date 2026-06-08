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

def _analizar_fecha(nombre: str, valores: List[Any], nulos: int) -> Dict[str, Any]:
    fechas = [_como_fecha(valor) for valor in valores]
    fechas = [valor for valor in fechas if valor is not None]

    if not fechas:
        return {
            "columna": nombre,
            "tipo": "fecha",
            "min": None,
            "max": None,
            "rango_dias": None,
            "nulos": nulos,
        }

    fecha_min = min(fechas)
    fecha_max = max(fechas)

    return {
        "columna": nombre,
        "tipo": "fecha",
        "min": fecha_min.isoformat(),
        "max": fecha_max.isoformat(),
        "rango_dias": (fecha_max - fecha_min).days,
        "nulos": nulos,
    }


def _analizar_booleana(nombre: str, valores: List[Any], nulos: int) -> Dict[str, Any]:
    verdaderos = sum(1 for valor in valores if bool(valor) is True)
    falsos = sum(1 for valor in valores if bool(valor) is False)

    return {
        "columna": nombre,
        "tipo": "booleana",
        "true": verdaderos,
        "false": falsos,
        "nulos": nulos,
    }


def _como_fecha(valor: Any):
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    try:
        convertido = pd.to_datetime(valor, errors="coerce")
    except Exception:
        return None
    if pd.isna(convertido):
        return None
    return convertido.date()

def obtener_perfil_dual(producto_id: int) -> Dict[str, Any]:
    collection = get_mongo_collection()
    vista_mongo = collection.find_one({"_id": producto_id})

    create_sql_tables()
    with SessionLocal() as session:
        producto_sql = session.get(ProductoSQL, producto_id)

    vista_sql = producto_sql.to_dict() if producto_sql else None

    if vista_mongo is None and vista_sql is None:
        raise HTTPException(
            status_code=404,
            detail=f"No existe el producto {producto_id} en MongoDB ni en MySQL.",
        )

    respuesta = {
        "id": producto_id,
        "vista_mongo": vista_mongo,
        "vista_sql": vista_sql,
    }

    if vista_mongo is None:
        respuesta["warning"] = (
            "Registro existe en MySQL pero no en MongoDB. "
            "Puede haberse borrado staging despues de transformar."
        )
    elif vista_sql is None:
        respuesta["warning"] = (
            "Registro existe en MongoDB pero no en MySQL. "
            "Posiblemente no se ha ejecutado /transformar o fallo la transformacion."
        )

    return respuesta