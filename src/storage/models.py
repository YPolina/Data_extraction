from typing import Annotated, Optional
from sqlalchemy import ForeignKey,text
from sqlalchemy.orm import Mapped, mapped_column, relationship
import datetime
import enum
from src.storage.database import Base

intpk = Annotated[int, mapped_column(primary_key=True)]
created_at = Annotated[datetime.datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]
str256 = Annotated[str, 256]
str512 = Annotated[str, 512]

class Articles(Base):
    __tablename__ = "articles"
    id: Mapped[intpk]
    pmid: Mapped[Optional[str256]]
    doi: Mapped[Optional[str256]]
    title: Mapped[str512]
    abstract: Mapped[str]
    journal: Mapped[Optional[str256]]
    authors: Mapped[Optional[str]]
    pdf_url: Mapped[Optional[str512]]
    disease_area: Mapped[Optional[str256]]
    created_at: Mapped[created_at]

    compounds_in_article:Mapped[list['Compounds']] = relationship(
        back_populates="article_with_compounds",
        secondary='article_compound',
    )


class Compounds(Base):
    __tablename__ = "compounds"

    id: Mapped[intpk]
    name: Mapped[str]
    pubchem_cid: Mapped[int] = mapped_column(unique=True)
    molecular_formula: Mapped[Optional[str]]
    molecular_weight: Mapped[Optional[float]]
    logp: Mapped[Optional[float]]
    tpsa: Mapped[Optional[float]]
    lipinski_pass: Mapped[Optional[bool]]

    article_with_compounds: Mapped[list["Articles"]] = relationship(
        back_populates="compounds_in_article",
        secondary='article_compound',
    )
    assays: Mapped[list["Assays"]] = relationship(
        back_populates="compound"
    )


class ArticleCompound(Base):
    __tablename__ = "article_compound"
    compound_id: Mapped[int] = mapped_column(
        ForeignKey("compounds.id", ondelete='CASCADE'),
        primary_key=True
    )
    article_id: Mapped[int] = mapped_column(
        ForeignKey("articles.id", ondelete='CASCADE'),
        primary_key=True
    )
    context: Mapped[Optional[str512]]

class ActivityOutcome(enum.Enum):
    active = "active"
    inactive = "inactive"
    inconclusive = "inconclusive"
    unspecified = "unspecified"
    probe = "probe"

class Assays(Base):
    __tablename__ = "assays"
    id: Mapped[intpk]
    assay_id: Mapped[int]
    compound_id: Mapped[int] = mapped_column(ForeignKey("compounds.id", ondelete="CASCADE"))

    assay_type: Mapped[str]
    target_name: Mapped[Optional[str]] = mapped_column(nullable=True)
    activity_outcome: Mapped[Optional[ActivityOutcome]] = mapped_column(nullable=True)
    potency_type: Mapped[Optional[str]] = mapped_column(nullable=True)
    potency_value: Mapped[Optional[float]] = mapped_column(nullable=True)
    potency_unit: Mapped[Optional[str]] = mapped_column(nullable=True)
    reference: Mapped[Optional[str]] = mapped_column(nullable=True)

    compound: Mapped["Compounds"] = relationship(
        back_populates="assays"
    )

