
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlmodel import Session

from database import get_session
from schemas import EtiquetaCreate, EtiquetaPublic
from service import NoEncontradoError, ConflictoError
import service


router = APIRouter(prefix="/etiquetas",tags=["Etiquetas"])

EtiquetaId = Annotated[int, Path(gt=0)]



@router.get("/", response_model=list[EtiquetaPublic])
def listar_etiquetas(session: Session = Depends(get_session)):
    return service.listar_etiquetas(session)



@router.post("/",response_model=EtiquetaPublic,status_code=status.HTTP_201_CREATED)
def crear_etiqueta(datos: EtiquetaCreate,session: Session = Depends(get_session)):
    try:
        return service.crear_etiqueta(session, datos)
    except ConflictoError as error:
        raise HTTPException(status_code=409,detail=str(error))


@router.delete("/{etiqueta_id}",status_code=status.HTTP_204_NO_CONTENT)
def eliminar_etiqueta(etiqueta_id: EtiquetaId,session: Session = Depends(get_session)):
    try:
        service.eliminar_etiqueta(session, etiqueta_id)
    except NoEncontradoError as error:
        raise HTTPException(status_code=404,detail=str(error))
    except ConflictoError as error:
        raise HTTPException(status_code=409,detail=str(error))
