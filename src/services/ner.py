import json
from src.utils.processing import extract_json_block
from src.core import settings
from src.utils.prompt import PROMPT_TEMPLATE

def extract_compounds_and_context(text:str, client, model, logger) -> dict:
    """
    Extract metadata and compounds from text using LLM.

    Args:
        text (str): The text to extract metadata from.
        client (boto3.client): AWS boto3 client.
        model (ModelID): AWS model ID.
        logger (logging.Logger): Logger.
    Returns:
        dict: The extracted metadata.
    """
    prompt = PROMPT_TEMPLATE.format(text=text)

    conversation = [{
        "role": "user",
        "content": [{"text": prompt}]
    }]


    response = client.converse(
        modelId=model,
        messages=conversation,
        inferenceConfig={"maxTokens": settings.PROMPT_MAX_TOKENS, "temperature": settings.PROMPT_TEMPERATURE}
    )
    logger.debug("Received response from model")

    raw_text = response["output"]["message"]["content"][0].get("text", "").strip()
    cleaned = extract_json_block(raw_text)

    try:
        parsed = json.loads(cleaned)
        return parsed
        logger.info("Successfully parsed JSON response")
    except Exception as e:
        logger.error(f"Parse error: {e}")
        logger.debug(f"RAW OUTPUT:\n{raw_text}")
        parsed = {}
        return parsed