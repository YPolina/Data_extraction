from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from src.core import settings

sync_engine = create_engine(
    url=settings.DATABASE_URL_psycopg,
    echo=False
)
session_local = sessionmaker(sync_engine)

class Base(DeclarativeBase):

    repr_col_num=3
    repr_col=tuple()
    def __repr__(self) -> str:
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_col or idx < self.repr_col_num:
                cols.append(f"{col}={getattr(self, col)}")
        return f"<{self.__class__.__name__}{', '.join(cols)}>"