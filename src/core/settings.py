from dotenv import load_dotenv
import os

load_dotenv()

# ==== BEDROCK Settings ====
MODEL_ID = os.getenv("MODEL_ID", "us.meta.llama3-3-70b-instruct-v1:0")
DEFAULT_TEMPERATURE = float(os.getenv("DEFAULT_TEMPERATURE", "0.3"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "3000"))
BEDROCK_ROLE_ARN = os.getenv("BEDROCK_ROLE_ARN", "arn:aws:iam::338861521122:role/BedrockBatchExecutionRole-us-east-1")

# ==== Prompt building ====
PROMPT_TEMPERATURE = 0.3
PROMPT_TOP_P = 0.7
PROMPT_MAX_TOKENS = 3000

# ==== AWS Settings ====
AWS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")


# ==== Logging ====
LOG_FORMAT = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# ==== Storage ====
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DATABASE_URL_psycopg = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


EMAIL = os.getenv("EMAIL_ADDRESS")

#VANNA RAG SYSTEM
VANNA_MODEL_NAME = os.getenv("VANNA_MODEL_NAME")
VANNA_API_KEY = os.getenv("VANNA_API_KEY")