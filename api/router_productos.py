from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlmodel import Session

from database import get_session
from schemas import (ProductoCreate,ProductoPublic,ProductoUpdate,ProductosPaginados)
from service import NoEncontradoError, ConflictoError
import service


router = APIRouter(prefix="/productos",tags=["Productos"])

ProductoId = Annotated[int, Path(gt=0)]
EtiquetaId = Annotated[int, Path(gt=0)]


@router.get("/", response_model=ProductosPaginados)
def listar_productos(q: str | None = Query(default=None, min_length=1, max_length=50),categoria_id: int | None = Query(default=None, gt=0),etiqueta_id: int | None = Query(default=None, gt=0),solo_con_stock: bool = False,skip: int = Query(default=0, ge=0),limit: int = Query(default=10, ge=1, le=50),session: Session = Depends(get_session)):
    return service.listar_productos(session,q,categoria_id,etiqueta_id,solo_con_stock,skip,limit)


@router.get("/{producto_id}", response_model=ProductoPublic)
def obtener_producto(producto_id: ProductoId,session: Session = Depends(get_session)):
    try:
        return service.obtener_producto(session, producto_id)
    except NoEncontradoError as error:
        raise HTTPException(status_code=404, detail=str(error))


@router.post("/",response_model=ProductoPublic,status_code=status.HTTP_201_CREATED)
def crear_producto(datos: ProductoCreate,session: Session = Depends(get_session)):
    try:
        return service.crear_producto(session, datos)
    except NoEncontradoError as error:
        raise HTTPException(status_code=404, detail=str(error))
    except ConflictoError as error:
        raise HTTPException(status_code=409, detail=str(error))


@router.patch("/{producto_id}", response_model=ProductoPublic)
def actualizar_producto(producto_id: ProductoId,datos: ProductoUpdate,session: Session = Depends(get_session)):
    try:
        return service.actualizar_producto(session, producto_id, datos)
    except NoEncontradoError as error:
        raise HTTPException(status_code=404, detail=str(error))
    except ConflictoError as error:
        raise HTTPException(status_code=409, detail=str(error))


@router.delete("/{producto_id}", response_model=ProductoPublic)
def desactivar_producto(producto_id: ProductoId,session: Session = Depends(get_session)):
    try:
        return service.desactivar_producto(session, producto_id)
    except NoEncontradoError as error:
        raise HTTPException(status_code=404, detail=str(error))
    except ConflictoError as error:
        raise HTTPException(status_code=409, detail=str(error))


@router.post("/{producto_id}/etiquetas/{etiqueta_id}",response_model=ProductoPublic,status_code=status.HTTP_201_CREATED)
def agregar_etiqueta(producto_id: ProductoId,etiqueta_id: EtiquetaId,session: Session = Depends(get_session)):
    try:
        return service.agregar_etiqueta_producto(session, producto_id, etiqueta_id)
    except NoEncontradoError as error:
        raise HTTPException(status_code=404, detail=str(error))
    except ConflictoError as error:
        raise HTTPException(status_code=409, detail=str(error))


@router.delete("/{producto_id}/etiquetas/{etiqueta_id}",status_code=status.HTTP_204_NO_CONTENT)
def quitar_etiqueta(producto_id: ProductoId,etiqueta_id: EtiquetaId,session: Session = Depends(get_session)):
    try:
        return service.quitar_etiqueta_producto(session, producto_id, etiqueta_id)
    except NoEncontradoError as error:
        raise HTTPException(status_code=404, detail=str(error))
    except ConflictoError as error:
        raise HTTPException(status_code=409, detail=str(error))
