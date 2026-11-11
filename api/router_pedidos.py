from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlmodel import Session

from database import get_session
from models import EstadoPedido
from schemas import (PedidoCreate,PedidoPublic,PedidoEstadoUpdate,PedidoResumen,PedidosPaginados)
from service import NoEncontradoError, ConflictoError
import service


router = APIRouter(prefix="/pedidos",tags=["Pedidos"])
PedidoId = Annotated[int, Path(gt=0)]

@router.post("/",response_model=PedidoPublic,status_code=status.HTTP_201_CREATED)
def crear_pedido(datos: PedidoCreate,session: Session = Depends(get_session)):
    try:
        return service.crear_pedido(session, datos)
    except NoEncontradoError as error:
        raise HTTPException(status_code=404, detail=str(error))
    except ConflictoError as error:
        raise HTTPException(status_code=409, detail=str(error))

@router.get("/", response_model=PedidosPaginados)
def listar_pedidos(estado: EstadoPedido | None = Query(default=None),skip: int = Query(default=0, ge=0),limit: int = Query(default=10, ge=1, le=50),session: Session = Depends(get_session)):
    return service.listar_pedidos(session, estado, skip, limit)

@router.get("/resumen", response_model=PedidoResumen)
def resumen_pedidos(session: Session = Depends(get_session)):
    return service.resumen_pedidos(session)

@router.get("/{pedido_id}", response_model=PedidoPublic)
def obtener_pedido(pedido_id: PedidoId,session: Session = Depends(get_session)):
    try:
        return service.obtener_pedido(session, pedido_id)
    except NoEncontradoError as error:
        raise HTTPException(status_code=404, detail=str(error))

@router.patch("/{pedido_id}/estado",response_model=PedidoPublic)
def cambiar_estado_pedido(pedido_id: PedidoId,datos: PedidoEstadoUpdate,session: Session = Depends(get_session)):
    try:
        return service.cambiar_estado_pedido(session, pedido_id, datos.estado)
    except NoEncontradoError as error:
        raise HTTPException(status_code=404, detail=str(error))
    except ConflictoError as error:
        raise HTTPException(status_code=409, detail=str(error))
