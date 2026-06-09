# Laboratorio ETL con FastAPI, MongoDB y MySQL

Proyecto backend que implementa un pipeline ETL usando productos de DummyJSON como única entidad principal.

## Fuente de Datos

- API: https://dummyjson.com/products
- Se usa solo la entidad `products`. No se mezclan `users`, `carts` ni `categories`.

## Instalación

**1. Crear y activar el entorno virtual:**

```bash
python -m venv venv
.\venv\Scripts\activate
```

**2. Instalar dependencias:**

```bash
pip install -r requirements.txt
```

**3. Configurar variables de entorno:**

```bash
copy .env.example .env
```

Abrir el `.env` y ajustar las credenciales de MongoDB y MySQL.

**4. Crear la base de datos en MySQL:**

```sql
CREATE DATABASE laboratorio_etl;
```

**5. Ejecutar el servidor:**

```bash
uvicorn app.main:app --reload
```

**6. Abrir la documentación interactiva:**

```text
http://127.0.0.1:8000/docs
```

## Flujo ETL

```text
DummyJSON Products
       ↓
MongoDB  →  staging (datos crudos)
       ↓
Pandas   →  transformación y limpieza
       ↓
MySQL    →  warehouse (datos limpios)
```

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

## Uso con Postman

Este proyecto incluye una colección de Postman para probar los endpoints del laboratorio ETL de forma más rápida, sin escribir las rutas manualmente.

### 1. Levantar el servidor de FastAPI

Antes de usar Postman, asegúrate de tener MongoDB y MySQL configurados, el archivo `.env` completo y el servidor corriendo:

```bash
uvicorn app.main:app --reload
```

El servidor debe quedar disponible en:

```text
http://localhost:8000
```

También puedes revisar la documentación automática en:

```text
http://127.0.0.1:8000/docs
```

### 2. Importar la colección en Postman

1. Abrir Postman.
2. Hacer clic en **Import**.
3. Seleccionar el archivo de la colección:

```text
Laboratorio_ETL.postman_collection (3).json
```

4. Confirmar la importación.
5. Postman creará una colección llamada **Laboratorio ETL**.

### 3. Verificar la variable `base_url`

La colección usa una variable llamada `base_url` para no repetir la URL del servidor en cada endpoint.

Valor configurado:

```text
http://localhost:8000
```

Si el servidor se está ejecutando en otro puerto, se debe cambiar esta variable en Postman. Por ejemplo:

```text
http://127.0.0.1:8000
```

### 4. Orden recomendado para probar el flujo ETL

Para validar el pipeline completo, ejecutar las peticiones en este orden:

| Orden | Carpeta | Petición | Método | Ruta | Descripción |
|------:|---------|----------|--------|------|-------------|
| 1 | ETL | Reset | DELETE | `/api/v1/etl/reset` | Limpia MongoDB y MySQL para iniciar desde cero. |
| 2 | ETL | Extraer | POST | `/api/v1/etl/extraer` | Descarga productos desde DummyJSON y los guarda en MongoDB. |
| 3 | ETL | Transformar | POST | `/api/v1/etl/transformar` | Lee los datos desde MongoDB, los transforma con Pandas y los carga en MySQL. |
| 4 | Analisis por columnas | Analisis Precio | GET | `/api/v1/analitica/columna/precio` | Calcula métricas numéricas para la columna precio. |
| 5 | Analisis por columnas | Analisis Categoria | GET | `/api/v1/analitica/columna/categoria` | Muestra análisis de una columna tipo texto. |
| 6 | Analisis por columnas | Analisis Fecha | GET | `/api/v1/analitica/columna/fecha_creacion` | Muestra mínimo, máximo y rango de fechas. |
| 7 | Analisis por columnas | Analisis Stock Bajo | GET | `/api/v1/analitica/columna/stock_bajo` | Muestra conteo de valores booleanos. |
| 8 | Perfil Dual | Perfil ID 1 | GET | `/api/v1/perfil/1` | Compara el producto con ID 1 en MongoDB y MySQL. |
| 9 | Perfil Dual | Perfil ID 10 | GET | `/api/v1/perfil/10` | Compara el producto con ID 10 en MongoDB y MySQL. |

### 5. Petición `Extraer`

La petición **Extraer** usa el método `POST` y envía un cuerpo JSON indicando cuántos productos se desean descargar.

Ruta:

```text
POST {{base_url}}/api/v1/etl/extraer
```

Body:

```json
{
  "cantidad": 50
}
```

Este endpoint consulta la API de DummyJSON y guarda los productos en MongoDB usando el ID original como `_id`.

### 6. Petición `Transformar`

Ruta:

```text
POST {{base_url}}/api/v1/etl/transformar
```

Esta petición toma los datos almacenados en MongoDB, los limpia y aplana con Pandas, calcula campos derivados y los carga en la tabla `productos_master` de MySQL.

### 7. Petición `Reset`

Ruta:

```text
DELETE {{base_url}}/api/v1/etl/reset
```

Esta petición limpia los datos de MongoDB y MySQL para poder volver a ejecutar el pipeline desde cero. No elimina la estructura de la tabla SQL, solamente reinicia los datos.

### 8. Pruebas de analítica

Después de ejecutar `Extraer` y `Transformar`, se pueden probar los endpoints de analítica dinámica:

```text
GET {{base_url}}/api/v1/analitica/columna/precio
GET {{base_url}}/api/v1/analitica/columna/categoria
GET {{base_url}}/api/v1/analitica/columna/fecha_creacion
GET {{base_url}}/api/v1/analitica/columna/stock_bajo
```

Estos endpoints detectan automáticamente el tipo de columna y devuelven métricas según corresponda: numéricas, texto, fechas o booleanos.

### 9. Pruebas de perfil dual

La colección también permite consultar el mismo producto en MongoDB y MySQL:

```text
GET {{base_url}}/api/v1/perfil/1
GET {{base_url}}/api/v1/perfil/10
```

Este endpoint sirve para comprobar que el producto existe en ambas bases y comparar la vista cruda de MongoDB con la vista transformada de MySQL.

### 10. Errores comunes

| Problema | Posible causa | Solución |
|----------|---------------|----------|
| `Connection refused` | El servidor de FastAPI no está corriendo. | Ejecutar `uvicorn app.main:app --reload`. |
| `404 Not Found` | La ruta no coincide con la definida en el backend. | Revisar que se esté usando `/api/v1/...`. |
| Error de conexión a MongoDB | MongoDB no está activo o las credenciales del `.env` están mal. | Revisar la conexión y las variables de entorno. |
| Error de conexión a MySQL | MySQL no está activo, la base no existe o las credenciales son incorrectas. | Crear la base `laboratorio_etl` y revisar el `.env`. |
| Analítica sin resultados | No se ha ejecutado el flujo completo. | Ejecutar primero `Extraer` y luego `Transformar`. |

### 11. Flujo resumido en Postman

```text
Reset -> Extraer -> Transformar -> Analítica -> Perfil Dual
```

Con este orden se valida todo el laboratorio: extracción desde DummyJSON, almacenamiento en MongoDB, transformación con Pandas, carga en MySQL y consulta final mediante endpoints de análisis.

## Estructura del Proyecto

```text
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
```

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

- MongoDB: Se usa `replace_one` con `upsert=True`. Si el producto ya existe se reemplaza, si no se inserta. No genera duplicados.
- MySQL: Se usa `INSERT ... ON DUPLICATE KEY UPDATE`. Ejecutar el pipeline varias veces no genera duplicados.
- Reset: Usa `TRUNCATE TABLE`, no `DROP`. La tabla permanece disponible para la siguiente ejecución.

## Analítica Dinámica

El endpoint `/api/v1/analitica/columna/{nombre}` detecta el tipo de columna automáticamente desde SQLAlchemy, sin hardcodear nombres:

| Tipo detectado    | Retorna                                            |
|-------------------|----------------------------------------------------|
| Boolean           | Conteo de true / false                             |
| Date / DateTime   | Fecha mínima, máxima y rango en días               |
| Integer / Float   | Min, max, promedio, mediana y desviación estándar  |
| String            | Valores únicos, distribución y valor más común     |

Si la columna no existe retorna `400 Bad Request` con la lista de columnas válidas.

## Perfil Dual

El endpoint `/api/v1/perfil/{id}` consulta el mismo ID en MongoDB y MySQL:

| Caso                    | Respuesta                                          |
|-------------------------|----------------------------------------------------|
| Existe en ambas bases   | 200 OK con vista_mongo y vista_sql                 |
| Existe solo en una      | 200 OK con la vista disponible y un warning        |
| No existe en ninguna    | 404 Not Found                                      |

## Responsabilidades

**Sofia:**
Infraestructura, configuración, conexiones a MongoDB y MySQL, cliente DummyJSON, paginación, upsert idempotente en MongoDB, endpoint `/extraer`.

**Felipe:**
Modelo SQL `productos_master`, lectura desde MongoDB, transformación con Pandas, aplanamiento de JSON anidado, métricas derivadas, carga idempotente en MySQL, endpoint `/transformar`.

**Elizabeth:**
Schemas Pydantic de entrada y salida, endpoint `/reset`, servicio de analítica dinámica por columna, perfil dual MongoDB/MySQL, README y documentación del código.