import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
# Load environment variables from the .env file
load_dotenv(BASE_DIR / '.env')

DATABASE_URL = os.getenv("DATABASE_URL")
GRAPH_QUERY_URL = os.getenv("GRAPH_QUERY_URL")
