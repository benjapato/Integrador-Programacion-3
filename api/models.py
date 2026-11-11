from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, timezone
from enum import Enum


class FormaPago(str, Enum):
    EFECTIVO = "EFECTIVO"
    TRANSFERENCIA = "TRANSFERENCIA"


class EstadoPedido(str, Enum):
    PENDIENTE = "PENDIENTE"
    EN_PREPARACION = "EN_PREPARACION"
    ENTREGADO = "ENTREGADO"
    CANCELADO = "CANCELADO"

class CategoriaBase(SQLModel):
    nombre: str = Field(min_length=2,max_length=50,unique=True,index=True)
    descripcion: str = Field(default="",max_length=200)


class Categoria(CategoriaBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    activo: bool = Field(default=True)

    productos: list["Producto"] = Relationship(back_populates="categoria")


class ProductoEtiqueta(SQLModel, table=True):
    producto_id: int = Field(foreign_key="producto.id",primary_key=True)
    etiqueta_id: int = Field(foreign_key="etiqueta.id",primary_key=True)


class EtiquetaBase(SQLModel):
    nombre: str = Field(min_length=2,max_length=30,unique=True,index=True)


class Etiqueta(EtiquetaBase, table=True):
    id: int | None = Field(default=None,primary_key=True)

    productos: list["Producto"] = Relationship(back_populates="etiquetas",link_model=ProductoEtiqueta)

class ProductoBase(SQLModel):
    nombre: str = Field(min_length=3,max_length=60,unique=True,index=True)
    descripcion: str = Field(default="", max_length=200)
    precio: float = Field(gt=0)
    stock: int = Field(default=0, ge=0)
    imagen_url: str | None = Field(default=None, max_length=255)

    categoria_id: int = Field(gt=0,foreign_key="categoria.id",index=True)


class Producto(ProductoBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    activo: bool = Field(default=True)

    categoria: Categoria | None = Relationship(back_populates="productos")
    etiquetas: list[Etiqueta] = Relationship(back_populates="productos",link_model=ProductoEtiqueta)
    detalles: list["DetallePedido"] = Relationship(back_populates="producto")


class PedidoBase(SQLModel):
    cliente_nombre: str = Field(min_length=3, max_length=80)
    direccion_entrega: str = Field(min_length=5, max_length=200)
    forma_pago: FormaPago
    notas: str | None = Field(default=None, max_length=200)


class Pedido(PedidoBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    estado: EstadoPedido = Field(default=EstadoPedido.PENDIENTE)
    total: float = Field(default=0.0, ge=0)
    fecha: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    detalles: list["DetallePedido"] = Relationship(back_populates="pedido")


class DetallePedido(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    pedido_id: int = Field(foreign_key="pedido.id")
    producto_id: int = Field(foreign_key="producto.id")

    nombre_producto: str
    precio_unitario: float = Field(gt=0)
    cantidad: int = Field(ge=1)
    subtotal: float = Field(ge=0)

    pedido: Pedido | None = Relationship(back_populates="detalles")
    producto: Producto | None = Relationship(back_populates="detalles")

