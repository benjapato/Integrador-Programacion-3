import os
import sqlite3

from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlmodel import SQLModel, Session, create_engine


@event.listens_for(Engine, "connect")
def _configurar_minusculas_sqlite(conexion, _registro):
    if isinstance(conexion, sqlite3.Connection):
        conexion.create_function(
            "lower",
            1,
            lambda texto: texto.lower() if texto is not None else None,
            deterministic=True,
        )


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///foodstore.db")

connect_args = ({"check_same_thread": False}
    if DATABASE_URL.startswith("sqlite")
    else {}
)

engine = create_engine(DATABASE_URL,connect_args=connect_args)


def crear_tablas():
    import models
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
