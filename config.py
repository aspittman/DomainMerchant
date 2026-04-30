import os
from dotenv import load_dotenv

load_dotenv()

NAMESILO_API_KEY = os.getenv("NAMESILO_API_KEY")
NAMESILO_USE_IP_RESTRICTIONS = False

BUDGET_PER_DOMAIN = 50
MIN_SCORE_THRESHOLD = 70

DATABASE_PATH = "data/domains.db"