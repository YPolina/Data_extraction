from pathlib import Path
from src.services.ner import extract_compounds_and_context
from src.schemas.compound_extraction import ArticleRecord
from src.services.pubchem import fetch_pubchem_data
from src.storage.queries import Queries
from src.utils.pdf_utils import extract_text_from_pdf, chunk_text
from src.utils.processing import is_pubchem_candidate
import json


def process_articles(raw_dir: Path, client, model, logger):
    """
    Process article data from PubMed.

    Args:
        raw_dir (Path): Path to the directory containing the raw data.
        client (boto3.client): AWS boto3 client.
        model (ModelID): AWS model ID.
        logger (logging.Logger): Logger.
    """
    metadata_path = raw_dir / "metadata.json"
    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata_records = {rec["PMID"]: rec for rec in json.load(f)}

    for pdf_file in raw_dir.glob("*.pdf"):
        pmid = pdf_file.stem
        meta = metadata_records.get(pmid)
        if not meta:
            logger.warning(f"No metadata found for {pdf_file.name}, skipping.")
            continue

        logger.info(f"Processing file: {pdf_file.name}")
        text = extract_text_from_pdf(pdf_file)
        chunks = chunk_text(text)
        logger.debug(f"Split into {len(chunks)} chunks")

        compounds_with_context = []
        disease_area = None

        for i, chunk in enumerate(chunks):
            logger.debug(f"Sending chunk {i + 1}/{len(chunks)} to model")
            parsed = extract_compounds_and_context(chunk, client, model, logger)

            # Collect compounds + context
            for comp in parsed.get("compounds", []):
                if is_pubchem_candidate(comp["name"]):
                    compounds_with_context.append(comp)

            # Disease area
            if disease_area is None and "disease_area" in parsed:
                disease_area = parsed["disease_area"]

        # Insert article once per file
        article: ArticleRecord = {
            "pmid": meta.get("PMID"),
            "doi": meta.get("DOI"),
            "title": meta.get("Title"),
            "abstract": meta.get("Abstract"),
            "journal": meta.get("Journal"),
            "authors": "; ".join(meta.get("Authors", [])),
            "pdf_url": meta.get("pdf_url"),
            "disease_area": disease_area
        }
        article_id = Queries.insert_article(article)

        # Insert compounds + link with context
        for comp in compounds_with_context:
            compound_name = comp["name"]
            context = comp.get("context")

            # Enrich with PubChem
            compound_data, assays = fetch_pubchem_data(
                compound=compound_name,
                article_file=pdf_file.name,
                logger=logger
            )

            if compound_data:
                compound_id = Queries.insert_compound(compound_data, article_id, context)
                if assays:
                    for assay in assays:

                        Queries.insert_assay(assay, compound_id)

            else:
                logger.info(f"Skipping insert for {compound_name}, no valid PubChem CID")