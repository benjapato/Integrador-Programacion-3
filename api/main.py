
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session

from database import crear_tablas, engine
from service import cargar_datos_de_ejemplo

from router_categorias import router as categorias_router
from router_etiquetas import router as etiquetas_router
from router_productos import router as productos_router
from router_pedidos import router as pedidos_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    crear_tablas()
    with Session(engine) as session:
        cargar_datos_de_ejemplo(session)
    yield

app = FastAPI(title="Food Store API",description="API REST de un negocio de comidas",version="1.0.0",lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500", "http://127.0.0.1:5500"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(categorias_router)
app.include_router(etiquetas_router)
app.include_router(productos_router)
app.include_router(pedidos_router)


@app.get("/", tags=["Estado"])
def raiz():
    return {"mensaje": "Food Store API funcionando","documentacion": "/docs"}
