# Laboratorio ETL con FastAPI, MongoDB y MySQL

Proyecto backend que implementa un pipeline ETL usando productos de DummyJSON como única entidad principal.

## Fuente

API: https://dummyjson.com/products

Se usa solo la entidad products. No se mezclan users, carts ni categories.

## Instalación

```bash
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

Crear `.env` desde `.env.example` y ajustar credenciales.

Crear base de datos MySQL:

```sql
CREATE DATABASE laboratorio_etl;
```

Ejecutar:

```bash
uvicorn app.main:app --reload
```

Abrir: http://127.0.0.1:8000/docs

## Endpoints

- POST /api/v1/etl/extraer
- POST /api/v1/etl/transformar
- DELETE /api/v1/etl/reset
- GET /api/v1/analitica/columna/{nombre}
- GET /api/v1/perfil/{id}

## Responsabilidades

**Sofia:** Infraestructura, configuración, conexiones, extracción desde DummyJSON, upsert en MongoDB.

**Felipe:** Modelo SQL, transformación con Pandas, aplanamiento de JSON, carga idempotente en MySQL.

**Elizabeth:** Schemas, Reset, Analítica dinámica, Perfil dual, Documentación.