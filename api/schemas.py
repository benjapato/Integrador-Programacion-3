from datetime import datetime
from sqlmodel import SQLModel, Field

from models import (CategoriaBase,EtiquetaBase,ProductoBase,PedidoBase,EstadoPedido)


class CategoriaCreate(CategoriaBase):
    pass

class CategoriaPublic(CategoriaBase):
    id: int
    activo: bool

class EtiquetaCreate(EtiquetaBase):
    pass

class EtiquetaPublic(EtiquetaBase):
    id: int


class ProductoCreate(ProductoBase):
    pass

class ProductoPublic(ProductoBase):
    id: int
    activo: bool
    categoria: CategoriaPublic
    etiquetas: list[EtiquetaPublic] = Field(default_factory=list)

class ProductoUpdate(SQLModel):
    nombre: str = Field(default=None, min_length=3, max_length=60)
    descripcion: str = Field(default=None, max_length=200)
    precio: float = Field(default=None, gt=0)
    stock: int = Field(default=None, ge=0)
    imagen_url: str | None = Field(default=None, max_length=255)
    categoria_id: int = Field(default=None, gt=0)

class DetalleCreate(SQLModel):
    producto_id: int = Field(gt=0)
    cantidad: int = Field(ge=1)

class PedidoCreate(PedidoBase):
    detalles: list[DetalleCreate] = Field(min_length=1)

class DetallePublic(SQLModel):
    id: int
    pedido_id: int
    producto_id: int
    nombre_producto: str
    precio_unitario: float
    cantidad: int
    subtotal: float

class PedidoPublic(PedidoBase):
    id: int
    estado: EstadoPedido
    total: float
    fecha: datetime
    detalles: list[DetallePublic] = Field(default_factory=list)

class PedidoEstadoUpdate(SQLModel):
    estado: EstadoPedido

class PedidoResumen(SQLModel):
    pendientes: int
    en_preparacion: int
    entregados: int
    cancelados: int
    ingresos_entregados: float

class CategoriaConProductos(CategoriaPublic):
    productos: list[ProductoPublic] = Field(default_factory=list)

class ProductosPaginados(SQLModel):
    total: int
    items: list[ProductoPublic]

class PedidosPaginados(SQLModel):
    total: int
    items: list[PedidoPublic]
