# Laboratorio ETL con FastAPI, MongoDB y MySQL

Proyecto backend que implementa un pipeline ETL usando productos de DummyJSON como única entidad principal.

## Fuente de Datos

- API: https://dummyjson.com/products
- Se usa solo la entidad `products`. No se mezclan `users`, `carts` ni `categories`.

## Instalación

**1. Crear y activar el entorno virtual:**

    python -m venv venv
    .\venv\Scripts\activate

**2. Instalar dependencias:**

    pip install -r requirements.txt

**3. Configurar variables de entorno:**

    copy .env.example .env

Abrir el `.env` y ajustar las credenciales de MongoDB y MySQL.

**4. Crear la base de datos en MySQL:**

    CREATE DATABASE laboratorio_etl;

**5. Ejecutar el servidor:**

    uvicorn app.main:app --reload

**6. Abrir la documentación interactiva:**

    http://127.0.0.1:8000/docs

## Flujo ETL

    DummyJSON Products
           ↓
    MongoDB  →  staging (datos crudos)
           ↓
    Pandas   →  transformación y limpieza
           ↓
    MySQL    →  warehouse (datos limpios)

1. `/extraer` descarga productos de DummyJSON y los guarda en MongoDB con su ID original como `_id`.
2. `/transformar` lee esos documentos, los aplana con Pandas y los carga en MySQL.
3. `/reset` limpia ambas bases para reiniciar el pipeline.

## Endpoints

| Método   | Ruta                                 | Descripción                                        |
|----------|--------------------------------------|----------------------------------------------------|
| POST     | /api/v1/etl/extraer                  | Extrae productos de DummyJSON y guarda en MongoDB  |
| POST     | /api/v1/etl/transformar              | Transforma datos de MongoDB y carga en MySQL       |
| DELETE   | /api/v1/etl/reset                    | Limpia MongoDB y MySQL                             |
| GET      | /api/v1/analitica/columna/{nombre}   | Analiza una columna de la tabla SQL dinámicamente  |
| GET      | /api/v1/perfil/{id}                  | Muestra el mismo producto en MongoDB y MySQL       |

## Estructura del Proyecto

    laboratorio_etl/
    ├── app/
    │   ├── controllers/
    │   │   ├── etl_controller.py        → Endpoints de extracción, transformación y reset
    │   │   └── analitica_controller.py  → Endpoints de analítica y perfil dual
    │   ├── models/
    │   │   └── productos_sql.py         → Modelo SQLAlchemy de la tabla productos_master
    │   ├── services/
    │   │   ├── etl_service.py           → Lógica de extracción, transformación y carga
    │   │   └── analitica_service.py     → Lógica de analítica dinámica y perfil dual
    │   ├── views/
    │   │   └── schemas.py               → Schemas Pydantic de entrada y salida
    │   ├── config.py                    → Variables de entorno
    │   ├── database.py                  → Conexiones a MongoDB y MySQL
    │   └── main.py                      → App FastAPI y registro de routers
    ├── .env.example                     → Plantilla de variables de entorno
    ├── .gitignore                       → Excluye .env y venv del repositorio
    └── requirements.txt                 → Dependencias del proyecto

## Tabla SQL — productos_master

| Columna                 | Tipo    | Descripción                                           |
|-------------------------|---------|-------------------------------------------------------|
| id_producto             | Integer | Primary key, igual al ID de DummyJSON y _id de Mongo |
| titulo                  | String  | Nombre del producto                                   |
| categoria               | String  | Categoría del producto                                |
| marca                   | String  | Marca del producto                                    |
| precio                  | Float   | Precio en dólares                                     |
| rating                  | Float   | Calificación promedio                                 |
| stock                   | Integer | Unidades disponibles                                  |
| estado_disponibilidad   | String  | Estado de disponibilidad                              |
| peso                    | Integer | Peso del producto                                     |
| ancho                   | Float   | Ancho en cm                                           |
| alto                    | Float   | Alto en cm                                            |
| profundidad             | Float   | Profundidad en cm                                     |
| cantidad_reviews        | Integer | Número de reseñas                                     |
| promedio_reviews        | Float   | Promedio de calificaciones de reseñas                 |
| fecha_creacion          | Date    | Fecha de creación del producto                        |
| tiene_descuento         | Boolean | True si tiene descuento                               |
| stock_bajo              | Boolean | True si el stock es menor a 10                        |

## Idempotencia

- MongoDB: Se usa replace_one con upsert=True. Si el producto ya existe se reemplaza, si no se inserta. No genera duplicados.
- MySQL: Se usa INSERT ... ON DUPLICATE KEY UPDATE. Ejecutar el pipeline varias veces no genera duplicados.
- Reset: Usa TRUNCATE TABLE, no DROP. La tabla permanece disponible para la siguiente ejecución.

## Analítica Dinámica

El endpoint /api/v1/analitica/columna/{nombre} detecta el tipo de columna automáticamente desde SQLAlchemy, sin hardcodear nombres:

| Tipo detectado    | Retorna                                            |
|-------------------|----------------------------------------------------|
| Boolean           | Conteo de true / false                             |
| Date / DateTime   | Fecha mínima, máxima y rango en días               |
| Integer / Float   | Min, max, promedio, mediana y desviación estándar  |
| String            | Valores únicos, distribución y valor más común     |

Si la columna no existe retorna 400 Bad Request con la lista de columnas válidas.

## Perfil Dual

El endpoint /api/v1/perfil/{id} consulta el mismo ID en MongoDB y MySQL:

| Caso                    | Respuesta                                          |
|-------------------------|----------------------------------------------------|
| Existe en ambas bases   | 200 OK con vista_mongo y vista_sql                 |
| Existe solo en una      | 200 OK con la vista disponible y un warning        |
| No existe en ninguna    | 404 Not Found                                      |

## Responsabilidades

**Sofia**
Infraestructura, configuración, conexiones a MongoDB y MySQL, cliente DummyJSON, paginación, upsert idempotente en MongoDB, endpoint /extraer.

**Felipe **
Modelo SQL productos_master, lectura desde MongoDB, transformación con Pandas, aplanamiento de JSON anidado, métricas derivadas, carga idempotente en MySQL, endpoint /transformar.

**Elizabeth**
Schemas Pydantic de entrada y salida, endpoint /reset, servicio de analítica dinámica por columna, perfil dual MongoDB/MySQL, README y documentación del código.