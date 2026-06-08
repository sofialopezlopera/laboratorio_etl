from sqlalchemy import Boolean, Column, Date, Float, Integer, String

from app.database import Base


class ProductoSQL(Base):
    __tablename__ = "productos_master"

    id_producto = Column(Integer, primary_key=True, autoincrement=False)
    titulo = Column(String(255), nullable=False)
    categoria = Column(String(100), nullable=False)
    marca = Column(String(120), nullable=False)
    precio = Column(Float, nullable=False)
    rating = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False)
    estado_disponibilidad = Column(String(80), nullable=False)
    peso = Column(Integer, nullable=False)
    ancho = Column(Float, nullable=False)
    alto = Column(Float, nullable=False)
    profundidad = Column(Float, nullable=False)
    cantidad_reviews = Column(Integer, nullable=False)
    promedio_reviews = Column(Float, nullable=False)
    fecha_creacion = Column(Date, nullable=True)
    tiene_descuento = Column(Boolean, nullable=False)
    stock_bajo = Column(Boolean, nullable=False)

    def to_dict(self):
        return {
            "id_producto": self.id_producto,
            "titulo": self.titulo,
            "categoria": self.categoria,
            "marca": self.marca,
            "precio": self.precio,
            "rating": self.rating,
            "stock": self.stock,
            "estado_disponibilidad": self.estado_disponibilidad,
            "peso": self.peso,
            "ancho": self.ancho,
            "alto": self.alto,
            "profundidad": self.profundidad,
            "cantidad_reviews": self.cantidad_reviews,
            "promedio_reviews": self.promedio_reviews,
            "fecha_creacion": (
                self.fecha_creacion.isoformat() if self.fecha_creacion else None
            ),
            "tiene_descuento": self.tiene_descuento,
            "stock_bajo": self.stock_bajo,
        }