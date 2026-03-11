from pathlib import Path

# --- PROJECT IDENTITY ---
PROJECT_NAME = "A Semantic MRI of Agricultural Education"
PROJECT_TITLE = (
    "A Semantic MRI of Agricultural Education: A Longitudinal Audit of "
    "Evolutionary Maturation, Methodological Friction, and Innovation Velocity "
    "(1960–2026) via High-Dimensional Vector Embeddings"
)

# --- PATH ARCHITECTURE ---
BASE_DIR = Path(__file__).resolve().parent

# Code Bins
BIN_DIR = BASE_DIR / "bins"
BIN_INGEST = BIN_DIR / "s01_ingest"
BIN_PROCESS = BIN_DIR / "s02_processor"
BIN_ANALYSIS = BIN_DIR / "s03_analysis"
BIN_UTILS = BIN_DIR / "s04_utils"

# Data Silos
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
MANIFEST_DIR = BASE_DIR / "data" / "manifests"
LOG_DIR = BASE_DIR / "logs"

MASTER_LEDGER = MANIFEST_DIR / "jae_master_ledger.csv"
LOG_FILE = LOG_DIR / "system.log"

# --- HARDWARE & COMPUTE (M3 MAX 64GB) ---
DEVICE = "mps"
MODEL_ID = "nomic-ai/nomic-embed-text-v1.5"
TOKEN_LIMIT = 8192
MAX_WORKERS = 8

# --- DATA ARCHITECTURE ---
EPOCH_STEP = 5
START_YEAR = 1960
END_YEAR = 2026

# --- CONFIGURATION INVARIANTS ---
if TOKEN_LIMIT <= 0:
    raise ValueError("TOKEN_LIMIT must be positive.")

if MAX_WORKERS <= 0:
    raise ValueError("MAX_WORKERS must be positive.")

if EPOCH_STEP <= 0:
    raise ValueError("EPOCH_STEP must be positive.")

if START_YEAR > END_YEAR:
    raise ValueError("START_YEAR cannot exceed END_YEAR.")

# --- IDEMPOTENCY GUARD ---
REQUIRED_DIRS = (
    BIN_INGEST,
    BIN_PROCESS,
    BIN_ANALYSIS,
    BIN_UTILS,
    RAW_DIR,
    PROCESSED_DIR,
    MANIFEST_DIR,
    LOG_DIR,
)

for directory in REQUIRED_DIRS:
    directory.mkdir(parents=True, exist_ok=True)