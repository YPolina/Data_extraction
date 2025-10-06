import pubchempy as pcp
from src.utils.processing import fetch_assays_for_cid
from src.schemas.compound_extraction import CompoundInfo, Assay
from typing import List


def fetch_pubchem_data(compound: str, article_file: str, logger) -> CompoundInfo:
    """
    Fetch PubChem data for a compound.
    Args:
        compound (str): Compound name.
        article_file (str): Source article filename.
        logger (logging.Logger): Logger.
    Returns:
        CompoundInfo: Dictionary of compound data.
    """
    try:
        results = pcp.get_compounds(compound, "name")

        if results:
            c = results[0]
            logp = getattr(c, "xlogp", None)
            tpsa = getattr(c, "tpsa", None)
            molecular_weight = getattr(c, "molecular_weight", None)
            h_bond_donor_count = getattr(c, "h_bond_donor_count", None)
            h_bond_acceptor_count = getattr(c, "h_bond_acceptor_count", None)
            pubchem_cid = getattr(c, "cid")

            # Lipinski's Rule of Five check
            lipinski_pass = None

            try:
                if c.molecular_weight and logp is not None:
                    lipinski_pass = (
                            molecular_weight < 500
                            and logp <= 5
                            and (h_bond_acceptor_count or 0) <= 5
                            and (h_bond_donor_count or 0) <= 10
                    )
            except Exception:
                lipinski_pass = None
            assays: List[Assay] = fetch_assays_for_cid(pubchem_cid)
            compound_info: CompoundInfo = {
                'name': compound,
                'pubchem_cid': pubchem_cid,
                'molecular_formula': c.molecular_formula,
                'molecular_weight': molecular_weight,
                "logp": logp,
                "tpsa": tpsa,
                "lipinski_pass": lipinski_pass,
            }
            return compound_info, assays
        else:
            return None, None
    except Exception as e:
        return None, None





