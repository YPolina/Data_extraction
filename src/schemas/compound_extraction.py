from typing import Union, TypedDict, Optional
from dataclasses import dataclass


class CompoundInfo(TypedDict, total=False):
    name: str
    pubchem_id: Union[int, str]
    molecular_formula: str = None
    molecular_weight: float = None
    logp: float = None
    tpsa: float = None
    lipinski_pass: bool = None

@dataclass
class ArticleRecord:
    pmid: int
    doi: str
    title: str
    abstract: str
    journal: str
    authors: str
    pdf_url: str
    disease_area: str

@dataclass
class Assay:
    assay_id: int
    assay_type: Optional[str]
    target_name: Optional[str]
    activity_outcome: Optional[str]
    potency_type: Optional[str]
    potency_value: Optional[float]
    potency_unit: Optional[str]
    reference: Optional[str]
