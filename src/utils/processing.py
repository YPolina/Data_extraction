import re
import requests
from typing import List
from src.schemas.compound_extraction import Assay

BIOLOGIC_SUFFIXES = ("mab", "cept", "kinra")
CYTOKINE_PREFIXES = ("IL-", "TNF-")
STOPLIST = {"EGFR", "KRAS", "ctDNA", "mRNA", "DNA", "RNA"}


def extract_json_block(raw_text: str) -> str:
    """
    Extract JSON block from raw text.
    Args:
        raw_text (str): Raw text.
    Returns:
        str: Extracted JSON block.
    """
    match = re.search(r"\{.*\}", raw_text, re.DOTALL)
    if match:
        return match.group(0)
    return raw_text

def fetch_assays_for_cid(cid: int) -> list[Assay]:
    """
    Fetch assay summary data for a given PubChem Compound ID (CID).

    Args:
        cid (int): PubChem Compound ID.

    Returns:
        List[Assay]: A list of Assay objects containing assay details.
    """
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/assaysummary/JSON"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    data = r.json()

    table = data.get("Table", {})
    columns = table.get("Columns", {}).get("Column", [])
    rows = table.get("Row", [])

    # Map column name → index
    col_index = {col: i for i, col in enumerate(columns)}

    assays: List[Assay] = []
    for row in rows:
        cells = row.get("Cell", [])

        try:
            assay_id = int(cells[col_index["AID"]])
        except Exception:
            assay_id = None

        activity_outcome = cells[col_index.get("Activity Outcome", -1)] or None
        assay_type = cells[col_index.get("Assay Type", -1)] or None
        target_name = cells[col_index.get("Target Accession", -1)] or None
        potency_type = cells[col_index.get("Activity Name", -1)] or None

        potency_value = None
        potency_unit = None
        if "Activity Value [uM]" in col_index:
            val = cells[col_index["Activity Value [uM]"]]
            if val:
                try:
                    potency_value = float(val)
                    potency_unit = "uM"
                except ValueError:
                    pass

        reference = cells[col_index.get("PubMed ID", -1)] or None

        assays.append(
            Assay(
                assay_id=assay_id,
                assay_type=assay_type,
                target_name=target_name,
                activity_outcome=activity_outcome.lower(),
                potency_type=potency_type,
                potency_value=potency_value,
                potency_unit=potency_unit,
                reference=reference,
            )
        )

    return assays



def is_pubchem_candidate(name: str) -> bool:
    """
    Determine if a given name is a valid PubChem candidate.

    Args:
        name (str): Name of the compound.

    Returns:
        bool: True if the name is a valid candidate, False otherwise.
    """
    n = name.strip()
    # Exclude biologics by suffix
    if any(n.lower().endswith(suf) for suf in BIOLOGIC_SUFFIXES):
        return False
    # Exclude cytokines by prefix
    if any(n.startswith(pref) for pref in CYTOKINE_PREFIXES):
        return False
    # Exclude stoplist terms
    if n in STOPLIST:
        return False
    # Exclude broad classes
    if n.lower().endswith(("oids", "ines", "anes", "chemotherapy")):
        return False
    return True