import os
import sys
import logging
from dotenv import load_dotenv
load_dotenv()

# Set up basic logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

current_file_path = os.path.abspath(__file__)
parent_directory = os.path.dirname(current_file_path)
root_directory = os.path.abspath(os.path.join(parent_directory, ".."))

# Existing config variables
ALLOW_ORIGINS = os.getenv("ALLOW_ORIGINS", "*").split(",")
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/sandbox")

# New config variables for Clicktromics APIs
RCSB_URL = os.getenv("RCSB_URL", "https://files.rcsb.org/download/")
DEFAULT_BUCKET_NAME = os.getenv("DEFAULT_BUCKET_NAME", "bioinformatics-sandbox")
USE_LOCAL_STORAGE = os.getenv("USE_LOCAL_STORAGE", "true")
LOCAL_STORAGE_PATH = os.getenv("LOCAL_STORAGE_PATH", "./data")
root_directory = os.getenv("ROOT_DIRECTORY", ".")

# AWS Configuration
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# System thresholds
CPU_THRESHOLD = int(os.getenv("CPU_THRESHOLD", "80"))
RAM_THRESHOLD = int(os.getenv("RAM_THRESHOLD", "80"))

# Default sequences and SMILES
DEFAULT_SEQUENCE = os.getenv("DEFAULT_SEQUENCE", "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG")
DEFAULT_SMILES = os.getenv("DEFAULT_SMILES", "O(c1ccc(cc1)CCOC)CC(O)CNC(C)C")

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

# Only create Redis URLs if Redis is configured
if REDIS_HOST and REDIS_PORT:
    if REDIS_PASSWORD:
        REDIS_URL_BROKER = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/0"
        REDIS_URL_BACKEND = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/1"
    else:
        REDIS_URL_BROKER = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
        REDIS_URL_BACKEND = f"redis://{REDIS_HOST}:{REDIS_PORT}/1"
else:
    REDIS_URL_BROKER = None
    REDIS_URL_BACKEND = None

MONGO_DATABASE = os.getenv("MONGO_DATABASE", "prepaire-lab")

USE_AWS=os.getenv("USE_AWS", "False").lower() in ['true', '1', 'yes']

ENV=os.getenv("ENV", "LOCAL")

missing_vars = []

# Check for critical missing variables but don't exit
if not MONGO_URL:
    missing_vars.append("MONGO_URL")
    log.warning("MONGO_URL is not set - MongoDB operations will fail")

if missing_vars:
    log.warning(f"Missing environment variables: {', '.join(missing_vars)}")

if ENV not in ["LOCAL", "DEV", "PROD", "STAGE", "DEVLOPMENT"]:
    log.warning(f"Invalid ENV value: {ENV}. Must be one of ['LOCAL', 'DEV', 'PROD', 'STAGE', 'DEVLOPMENT'].")

log.info("Configuration loaded successfully.")