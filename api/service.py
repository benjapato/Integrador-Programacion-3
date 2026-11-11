from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select, func
from sqlalchemy import or_


from models import Categoria, Producto, Etiqueta, ProductoEtiqueta, Pedido, DetallePedido, EstadoPedido
from schemas import CategoriaCreate, EtiquetaCreate, ProductoCreate, ProductoUpdate, PedidoCreate


class NoEncontradoError(Exception):
    pass

class ConflictoError(Exception):
    pass

def _guardar(session: Session, entidad, mensaje: str):
    session.add(entidad)

    try:
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise ConflictoError(mensaje) from error

    session.refresh(entidad)
    return entidad


def _existe_categoria(session: Session, nombre: str,excluir_id: int | None = None) -> bool:

    consulta = select(Categoria.id).where(func.lower(Categoria.nombre) == nombre.lower())

    if excluir_id is not None:
        consulta = consulta.where(Categoria.id != excluir_id)

    return session.exec(consulta).first() is not None


def listar_categorias(session: Session) -> list[Categoria]:
    consulta = (select(Categoria).where(Categoria.activo == True).order_by(Categoria.id))
    return list(session.exec(consulta).all())


def obtener_categoria(session: Session, categoria_id: int) -> Categoria:
    categoria = session.get(Categoria, categoria_id)

    if categoria is None:
        raise NoEncontradoError(f"No existe una categoria con id {categoria_id}")

    return categoria


def obtener_categoria_con_productos(
    session: Session, categoria_id: int) -> Categoria:

    
    consulta = (select(Categoria).where(Categoria.id == categoria_id).options(selectinload(Categoria.productos).selectinload(Producto.categoria),selectinload(Categoria.productos).selectinload(Producto.etiquetas)))

    categoria = session.exec(consulta).first()

    if categoria is None:
        raise NoEncontradoError(f"No existe una categoria con id {categoria_id}")

    return categoria


def crear_categoria(session: Session, datos: CategoriaCreate) -> Categoria:

    if _existe_categoria(session, datos.nombre):
        raise ConflictoError(f"Ya existe la categoria '{datos.nombre}'")

    categoria = Categoria.model_validate(datos)

    return _guardar(session,categoria,f"Ya existe la categoria '{datos.nombre}'")


def actualizar_categoria(
    session: Session, categoria_id: int, datos: CategoriaCreate) -> Categoria:

    categoria = obtener_categoria(session, categoria_id)

    if _existe_categoria(session, datos.nombre, excluir_id=categoria_id):
        raise ConflictoError(f"Ya existe la categoria '{datos.nombre}'")

    categoria.nombre = datos.nombre
    categoria.descripcion = datos.descripcion

    return _guardar(session,categoria,"No se pudo actualizar la categoria")


def desactivar_categoria(session: Session, categoria_id: int) -> Categoria:

    categoria = obtener_categoria(session, categoria_id)

    if not categoria.activo:
        raise ConflictoError("La categoria ya esta dada de baja")

    consulta = select(Producto.id).where( Producto.categoria_id == categoria_id,Producto.activo == True)

    if session.exec(consulta).first() is not None:
        raise ConflictoError("La categoria tiene productos activos")
    
    categoria.activo = False
    return _guardar(session,categoria,"No se pudo dar de baja la categoria")



def listar_etiquetas(session: Session) -> list[Etiqueta]:
    consulta = select(Etiqueta).order_by(Etiqueta.id)
    return list(session.exec(consulta).all())


def obtener_etiqueta(session: Session, etiqueta_id: int) -> Etiqueta:
    etiqueta = session.get(Etiqueta, etiqueta_id)

    if etiqueta is None:
        raise NoEncontradoError(f"No existe una etiqueta con id {etiqueta_id}")

    return etiqueta


def crear_etiqueta(session: Session, datos: EtiquetaCreate) -> Etiqueta:

    consulta = select(Etiqueta).where(func.lower(Etiqueta.nombre) == datos.nombre.lower())

    if session.exec(consulta).first() is not None:
        raise ConflictoError(f"Ya existe la etiqueta '{datos.nombre}'")

    etiqueta = Etiqueta.model_validate(datos)

    return _guardar(session,etiqueta,f"Ya existe la etiqueta '{datos.nombre}'")


def eliminar_etiqueta(session: Session, etiqueta_id: int) -> None:

    etiqueta = obtener_etiqueta(session, etiqueta_id)

    consulta = select(ProductoEtiqueta).where(ProductoEtiqueta.etiqueta_id == etiqueta_id)

    if session.exec(consulta).first() is not None:
        raise ConflictoError("La etiqueta esta asociada a un producto")

    session.delete(etiqueta)

    try:
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise ConflictoError("No se puede eliminar la etiqueta") from error


def _existe_producto(session: Session,nombre: str,excluir_id: int | None = None) -> bool:

    consulta = select(Producto.id).where(func.lower(Producto.nombre) == nombre.lower())

    if excluir_id is not None:
        consulta = consulta.where(Producto.id != excluir_id)

    return session.exec(consulta).first() is not None


def obtener_producto(session: Session, producto_id: int) -> Producto:

    consulta = (select(Producto).where(Producto.id == producto_id).options(selectinload(Producto.categoria),selectinload(Producto.etiquetas)))

    producto = session.exec(consulta).first()

    if producto is None:
        raise NoEncontradoError(f"No existe un producto con id {producto_id}")

    return producto


def crear_producto(session: Session,datos: ProductoCreate) -> Producto:

    categoria = session.get(Categoria, datos.categoria_id)

    if categoria is None or not categoria.activo:
        raise NoEncontradoError("La categoria no existe o esta dada de baja")

    if _existe_producto(session, datos.nombre):
        raise ConflictoError(f"Ya existe el producto '{datos.nombre}'")

    producto = Producto.model_validate(datos)

    producto = _guardar(session,producto,"No se pudo crear el producto")

    return obtener_producto(session, producto.id)


def actualizar_producto(session: Session,producto_id: int,datos: ProductoUpdate) -> Producto:

    producto = obtener_producto(session, producto_id)

    cambios = datos.model_dump(exclude_unset=True)

    if "nombre" in cambios:  # noqa: SIM102
        if _existe_producto(session, cambios["nombre"], excluir_id=producto_id):
            raise ConflictoError("Ya existe un producto con ese nombre")

    if "categoria_id" in cambios:
        categoria = session.get(Categoria, cambios["categoria_id"])

        if categoria is None or not categoria.activo:
            raise NoEncontradoError("La categoria no existe o esta dada de baja")

    for campo, valor in cambios.items():
        setattr(producto, campo, valor)

    _guardar(session, producto, "No se pudo actualizar el producto")

    return obtener_producto(session, producto_id)


def desactivar_producto(session: Session,producto_id: int) -> Producto:

    producto = obtener_producto(session, producto_id)

    if not producto.activo:
        raise ConflictoError("El producto ya esta dado de baja")

    producto.activo = False
    _guardar(session,producto,"No se pudo dar de baja el producto")
    return obtener_producto(session, producto_id)


def listar_productos(session: Session,q: str | None = None,categoria_id: int | None = None,etiqueta_id: int | None = None,solo_con_stock: bool = False,skip: int = 0,limit: int = 10) -> dict:

    filtros = [Producto.activo == True]

    if q is not None:
        filtros.append(or_(Producto.nombre.ilike(f"%{q}%"),Producto.descripcion.ilike(f"%{q}%")))

    if categoria_id is not None:
        filtros.append(Producto.categoria_id == categoria_id)

    if etiqueta_id is not None:
        subconsulta = select(ProductoEtiqueta.producto_id).where(ProductoEtiqueta.etiqueta_id == etiqueta_id)

        filtros.append(Producto.id.in_(subconsulta))

    if solo_con_stock:
        filtros.append(Producto.stock > 0)

    consulta_total = (select(func.count(Producto.id)).where(*filtros))
    total = session.exec(consulta_total).one()
    consulta = (select(Producto).where(*filtros).options(selectinload(Producto.categoria),selectinload(Producto.etiquetas)).order_by(Producto.id).offset(skip).limit(limit))
    productos = session.exec(consulta).all()

    return {"total": total,"items": list(productos)}


def agregar_etiqueta_producto(session: Session,producto_id: int,etiqueta_id: int) -> Producto:

    obtener_producto(session, producto_id)
    etiqueta = session.get(Etiqueta, etiqueta_id)

    if etiqueta is None:
        raise NoEncontradoError("La etiqueta no existe")

    relacion = session.get(ProductoEtiqueta,(producto_id, etiqueta_id))

    if relacion is not None:
        raise ConflictoError("El producto ya tiene esta etiqueta")

    nueva_relacion = ProductoEtiqueta(producto_id=producto_id,etiqueta_id=etiqueta_id)
    session.add(nueva_relacion)

    try:
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise ConflictoError("No se pudo asociar la etiqueta") from error

    return obtener_producto(session, producto_id)


def quitar_etiqueta_producto(session: Session,producto_id: int,etiqueta_id: int) -> None:

    obtener_producto(session, producto_id)

    relacion = session.get(ProductoEtiqueta,(producto_id, etiqueta_id))

    if relacion is None:
        raise NoEncontradoError("El producto no tiene esta etiqueta")

    session.delete(relacion)

    try:
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise ConflictoError("No se pudo quitar la etiqueta") from error


def crear_pedido(session: Session,datos: PedidoCreate) -> Pedido:

    productos_validados = []
    ids_utilizados = set()

    
    for detalle in datos.detalles:

        if detalle.producto_id in ids_utilizados:
            raise ConflictoError("No se puede repetir un producto en el pedido")

        ids_utilizados.add(detalle.producto_id)

        producto = session.get(Producto, detalle.producto_id)

        if producto is None or not producto.activo:
            raise NoEncontradoError(f"El producto {detalle.producto_id} no existe o esta inactivo")

        if producto.stock < detalle.cantidad:
            raise ConflictoError(f"Stock insuficiente para {producto.nombre}")

        productos_validados.append((producto, detalle.cantidad))

    pedido = Pedido(cliente_nombre=datos.cliente_nombre,direccion_entrega=datos.direccion_entrega,forma_pago=datos.forma_pago,notas=datos.notas,total=0)

    total = 0.0

    try:
        for producto, cantidad in productos_validados:
            subtotal = round(producto.precio * cantidad, 2)
            total += subtotal
            detalle_pedido = DetallePedido(producto_id=producto.id,nombre_producto=producto.nombre,precio_unitario=producto.precio,cantidad=cantidad,subtotal=subtotal)

            pedido.detalles.append(detalle_pedido)

            producto.stock -= cantidad
            session.add(producto)

        pedido.total = round(total, 2)

        session.add(pedido)
        session.commit()
        session.refresh(pedido)

    except Exception:
        session.rollback()
        raise
    return pedido


def obtener_pedido(session: Session,pedido_id: int) -> Pedido:

    consulta = (select(Pedido).where(Pedido.id == pedido_id).options(selectinload(Pedido.detalles)))
    pedido = session.exec(consulta).first()

    if pedido is None:
        raise NoEncontradoError(f"No existe un pedido con id {pedido_id}")
    return pedido


def listar_pedidos(session: Session,estado: EstadoPedido | None = None,skip: int = 0,limit: int = 10) -> dict:

    filtros = []

    if estado is not None:
        filtros.append(Pedido.estado == estado)

    consulta_total = (select(func.count(Pedido.id)).where(*filtros))

    total = session.exec(consulta_total).one()

    consulta = (select(Pedido).where(*filtros).options(selectinload(Pedido.detalles)).order_by(Pedido.id.desc()).offset(skip).limit(limit))

    pedidos = session.exec(consulta).all()

    return {"total": total,"items": list(pedidos)}



def cambiar_estado_pedido(session: Session,pedido_id: int,nuevo_estado: EstadoPedido) -> Pedido:

    pedido = obtener_pedido(session, pedido_id)

    
    transiciones = {EstadoPedido.PENDIENTE: {EstadoPedido.EN_PREPARACION,EstadoPedido.CANCELADO},EstadoPedido.EN_PREPARACION: {EstadoPedido.ENTREGADO,EstadoPedido.CANCELADO},EstadoPedido.ENTREGADO: set(),EstadoPedido.CANCELADO: set()}

    if nuevo_estado not in transiciones[pedido.estado]:
        raise ConflictoError("No se permite cambiar a ese estado")

    try:
        if nuevo_estado == EstadoPedido.CANCELADO:

            for detalle in pedido.detalles:
                producto = session.get(Producto, detalle.producto_id)

                if producto is None:
                    raise ConflictoError("No se encontro un producto del pedido")

                producto.stock += detalle.cantidad
                session.add(producto)

        pedido.estado = nuevo_estado
        session.add(pedido)
        session.commit()

    except Exception:
        session.rollback()
        raise

    return obtener_pedido(session, pedido_id)


def resumen_pedidos(session: Session) -> dict:

    def contar(estado: EstadoPedido) -> int:
        consulta = select(func.count(Pedido.id)).where(Pedido.estado == estado)
        return session.exec(consulta).one()

    consulta_ingresos = select(func.coalesce(func.sum(Pedido.total), 0.0)).where(Pedido.estado == EstadoPedido.ENTREGADO)

    ingresos = session.exec(consulta_ingresos).one()

    return {"pendientes": contar(EstadoPedido.PENDIENTE),
        "en_preparacion": contar(EstadoPedido.EN_PREPARACION),
        "entregados": contar(EstadoPedido.ENTREGADO),
        "cancelados": contar(EstadoPedido.CANCELADO),
        "ingresos_entregados": float(ingresos)
    }


def cargar_datos_de_ejemplo(session: Session) -> None:

    existe = session.exec(select(Categoria.id)).first()

    if existe is not None:
        return

    try:
        categorias = [
            Categoria(nombre="Pizzas", descripcion="Pizzas caseras"),
            Categoria(nombre="Hamburguesas", descripcion="Hamburguesas artesanales"),
            Categoria(nombre="Ensaladas", descripcion="Ensaladas frescas"),
            Categoria(nombre="Bebidas", descripcion="Bebidas frías"),
            Categoria(nombre="Acompañamientos", descripcion="Porciones para compartir"),
        ]

        etiquetas = [
            Etiqueta(nombre="Vegetariano"),
            Etiqueta(nombre="Sin TACC"),
            Etiqueta(nombre="Vegano")
        ]

        session.add_all(categorias)
        session.add_all(etiquetas)
        session.flush()

        # Los primeros doce conservan el orden de las relaciones de etiquetas.
        # Las imágenes se sirven desde web/img en el frontend.
        datos = [
            ("Pizza Muzzarella", "Salsa de tomate, muzzarella fundida y orégano.", 9000, 15, 0, "catalogo/pizza-muzzarella.jpg"),
            ("Pizza Napolitana", "Tomate fresco, ajo y albahaca sobre muzzarella.", 10000, 10, 0, "catalogo/pizza-napolitana.jpg"),
            ("Pizza Fugazzeta", "Masa rellena de queso y cubierta de cebolla.", 11000, 8, 0, "catalogo/pizza-fugazzeta.jpg"),
            ("Hamburguesa Clásica", "Medallón a la plancha, lechuga y salsa de la casa.", 7500, 20, 1, "catalogo/hamburguesa-clasica.jpg"),
            ("Hamburguesa Doble", "Dos medallones, cheddar y pan tostado.", 9500, 12, 1, "catalogo/hamburguesa-doble.jpg"),
            ("Hamburguesa Vegetariana", "Medallón de lentejas con vegetales frescos.", 8000, 6, 1, "catalogo/hamburguesa-vegetariana.jpg"),
            ("Ensalada Mixta", "Hojas verdes, tomate y cebolla morada.", 4500, 10, 2, "catalogo/ensalada-mixta.jpg"),
            ("Ensalada César", "Lechuga, pollo grillado, crutones y aderezo César.", 6500, 7, 2, "catalogo/ensalada-cesar.jpg"),
            ("Ensalada Vegana", "Garbanzos, pepino, zanahoria y vinagreta.", 5500, 0, 2, "catalogo/ensalada-vegana.jpg"),
            ("Agua Mineral", "Botella de agua mineral sin gas de 500 ml.", 2000, 30, 3, "catalogo/agua-mineral.jpg"),
            ("Limonada", "Limón exprimido, hielo y hojas de menta.", 3500, 15, 3, "catalogo/limonada.jpg"),
            ("Jugo de Naranja", "Jugo de naranja recién exprimido.", 4000, 10, 3, "catalogo/jugo-naranja.jpg"),
            ("Pizza de Albahaca", "Muzzarella, tomates y albahaca fresca.", 10800, 8, 0, "catalogo/pizza-albahaca.jpg"),
            ("Pizza de Cuatro Quesos", "Muzzarella, provolone, parmesano y queso azul.", 12800, 9, 0, "catalogo/pizza-cuatro-quesos.jpg"),
            ("Pizza de Champiñones", "Muzzarella y champiñones salteados.", 11700, 5, 0, "catalogo/pizza-champinones.jpg"),
            ("Hamburguesa Cheddar", "Medallón, cheddar fundido y pepinillos.", 8700, 11, 1, "catalogo/hamburguesa-cheddar.jpg"),
            ("Hamburguesa Criolla", "Medallón a la plancha y salsa criolla.", 9100, 8, 1, "catalogo/hamburguesa-criolla.jpg"),
            ("Hamburguesa de Pollo", "Pechuga grillada, lechuga y mayonesa de limón.", 8900, 6, 1, "catalogo/hamburguesa-pollo.jpg"),
            ("Ensalada Mediterránea", "Pepino, aceitunas, tomate y queso.", 6900, 7, 2, "catalogo/ensalada-mediterranea.jpg"),
            ("Ensalada de Estación", "Hojas y verduras de estación con vinagreta.", 5200, 8, 2, "catalogo/ensalada-estacion.jpg"),
            ("Gaseosa Cola", "Lata de gaseosa cola de 354 ml.", 2700, 18, 3, "catalogo/gaseosa-cola.jpg"),
            ("Limonada con Jengibre", "Limón, jengibre y menta con hielo.", 3900, 10, 3, "catalogo/limonada-jengibre.jpg"),
            ("Agua con Gas", "Botella de agua mineral con gas de 500 ml.", 2200, 18, 3, "catalogo/agua-gas.jpg"),
            ("Papas Clásicas", "Papas fritas doradas con sal.", 3900, 20, 4, "catalogo/papas-clasicas.jpg"),
            ("Papas Rústicas", "Papas con piel, hierbas y un toque de ajo.", 4800, 12, 4, "catalogo/papas-rusticas.jpg"),
            ("Papas para Compartir", "Porción grande de papas crocantes.", 5900, 10, 4, "catalogo/papas-compartir.jpg"),
        ]
        productos = [
            Producto(
                nombre=nombre, descripcion=descripcion, precio=precio, stock=stock,
                categoria_id=categorias[categoria].id,
                imagen_url=f"img/{imagen}" if imagen else None,
            )
            for nombre, descripcion, precio, stock, categoria, imagen in datos
        ]

        session.add_all(productos)
        session.flush()

        relaciones = [
            (0, 0),
            (1, 0),
            (5, 0),
            (6, 0),
            (6, 1),
            (8, 2),
            (9, 1),
            (10, 2)
        ]

        for indice_producto, indice_etiqueta in relaciones:
            relacion = ProductoEtiqueta(producto_id=productos[indice_producto].id,etiqueta_id=etiquetas[indice_etiqueta].id)
            session.add(relacion)
        session.commit()
    except Exception:
        session.rollback()
        raise

