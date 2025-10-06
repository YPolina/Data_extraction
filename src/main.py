import os
import sys
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from pathlib import Path
from src.services.article_service import process_articles
from src.services.pubmed_articles import article_collection
import argparse
import boto3
from src.core import settings
from src.storage.queries import Queries
import logging

logging.basicConfig(
    level=settings.LOG_LEVEL,
    format=settings.LOG_FORMAT,
)

logger = logging.getLogger("pubchem_db")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Article processing pipeline")
    parser.add_argument("--article_dir", type=Path, default=Path("data/raw"))
    parser.add_argument("--query", type=str, required=True, help="PubMed search query")
    parser.add_argument("--retmax", type=int, default=30, help="Number of PubMed results")
    parser.add_argument("--data_collection", type=bool, default=False, help="Whether to collect data")

    args = parser.parse_args()
    article_dir = args.article_dir

    if args.data_collection:
        logger.info("Starting article download pipeline")
        retmax = args.retmax
        query = args.query
        article_collection(
            query=query,
            email=settings.EMAIL,
            retmax=retmax,
            output_dir=article_dir
        )
    logger.info("Starting article processing pipeline")

    session = boto3.Session(
        aws_access_key_id=settings.AWS_KEY,
        aws_secret_access_key=settings.AWS_SECRET,
        region_name=settings.AWS_REGION,
    )
    logger.info("AWS session initialized")

    client = session.client("bedrock-runtime")
    logger.info("Bedrock client created")

    Queries.create_tables()
    logger.info("DB tables created")

    process_articles(article_dir, client, settings.MODEL_ID, logger=logger)
    logger.info("Finished processing articles")
