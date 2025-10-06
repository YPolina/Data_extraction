from src.storage.database import sync_engine, Base, session_local
from src.storage.models import Articles, Compounds, ArticleCompound, Assays
from src.schemas.compound_extraction import ArticleRecord, CompoundInfo, Assay
from sqlalchemy import select, insert
from sqlalchemy.dialects.postgresql import insert as pg_insert
from src.core import settings
from dataclasses import asdict
from sqlalchemy.exc import IntegrityError
import logging

logging.basicConfig(
    level=settings.LOG_LEVEL,
    format=settings.LOG_FORMAT,
)

logger = logging.getLogger("pubchem_db")


class Queries:
    @staticmethod
    def create_tables():
        Base.metadata.drop_all(sync_engine)
        Base.metadata.create_all(sync_engine)

    @staticmethod
    def insert_article(article: ArticleRecord) -> int:
        with session_local() as session:
            try:
                insert_article = insert(Articles).values(article).returning(Articles.id)
                result = session.execute(insert_article)
                article_id = result.scalar()
                session.commit()
                return article_id
            except IntegrityError:
                session.rollback()
                article_id = session.execute(
                    select(Articles.id).where(Articles.pmid == article['pmid'])
                ).scalar()
                return article_id

    @staticmethod
    def insert_compound(compound: CompoundInfo, article_id: int, context: str = None) -> int:
        """Insert compound and link to article with context."""
        with session_local() as session:
            # Insert compound
            try:
                stmt = insert(Compounds).values(compound).returning(Compounds.id)
                result = session.execute(stmt)
                compound_id = result.scalar()
                session.commit()
            except IntegrityError:
                session.rollback()
                # compound already exists, fetch its id
                compound_id = session.execute(
                    select(Compounds.id).where(Compounds.pubchem_cid == compound["pubchem_cid"])
                ).scalar()
                logger.error(f"Compound already exists pubchem_cid={compound['pubchem_cid']}")

            # Add relationship with context
            stmt_assoc = pg_insert(ArticleCompound).values(
                article_id=article_id,
                compound_id=compound_id,
                context=context,
            ).on_conflict_do_nothing()
            session.execute(stmt_assoc)
            session.commit()
            return compound_id

    @staticmethod
    def insert_assay(assay: Assay, compound_id: int):
        with session_local() as session:
            try:
                data = asdict(assay)
                data["compound_id"] = compound_id
                stmt = insert(Assays).values(data)
                session.execute(stmt)
                session.commit()
            except Exception as e:
                logger.error(e)


