from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlmodel import Session

from database import get_session
from schemas import (CategoriaCreate,CategoriaPublic,CategoriaConProductos)
from service import NoEncontradoError, ConflictoError
import service


router = APIRouter(prefix="/categorias",tags=["Categorias"])

CategoriaId = Annotated[int, Path(gt=0)]


@router.get("/", response_model=list[CategoriaPublic])
def listar_categorias(session: Session = Depends(get_session)):
    return service.listar_categorias(session)


@router.get("/{categoria_id}", response_model=CategoriaConProductos)
def obtener_categoria(categoria_id: CategoriaId,session: Session = Depends(get_session)):
    try:
        return service.obtener_categoria_con_productos(session, categoria_id)
    except NoEncontradoError as error:
        raise HTTPException(status_code=404,detail=str(error))



@router.post("/",response_model=CategoriaPublic,status_code=status.HTTP_201_CREATED)
def crear_categoria(datos: CategoriaCreate,session: Session = Depends(get_session)):
    try:
        return service.crear_categoria(session, datos)
    except ConflictoError as error:
        raise HTTPException(status_code=409,detail=str(error))


@router.put("/{categoria_id}", response_model=CategoriaPublic)
def actualizar_categoria(categoria_id: CategoriaId,datos: CategoriaCreate,session: Session = Depends(get_session)):
    try:
        return service.actualizar_categoria(session, categoria_id, datos)
    except NoEncontradoError as error:
        raise HTTPException(status_code=404, detail=str(error))
    except ConflictoError as error:
        raise HTTPException(status_code=409, detail=str(error))


@router.delete("/{categoria_id}", response_model=CategoriaPublic)
def desactivar_categoria(categoria_id: CategoriaId,session: Session = Depends(get_session)):
    try:
        return service.desactivar_categoria(session, categoria_id)
    except NoEncontradoError as error:
        raise HTTPException(status_code=404, detail=str(error))
    except ConflictoError as error:
        raise HTTPException(status_code=409, detail=str(error))
