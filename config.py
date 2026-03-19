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
RAW_ROUTE_MODERN = RAW_DIR / "Route_A_Modern"
RAW_ROUTE_LEGACY = RAW_DIR / "Route_B_Legacy"

PROCESSED_DIR = BASE_DIR / "data" / "processed"
STRUCTURED_DIR = BASE_DIR / "data" / "structured"
MANIFEST_DIR = BASE_DIR / "data" / "manifests"

# Temporary compatibility constant:
# keep this until all legacy ledger imports are fully removed.
MASTER_LEDGER = MANIFEST_DIR / "jae_master_ledger.csv"

LOG_DIR = BASE_DIR / "logs"

# Testing / Embeddings
TESTING_DIR = BASE_DIR / "data" / "testing"
DOI_TEST_DIR = TESTING_DIR / "doi_abstracts_2021_2026"
DOI_TEST_RAW_DIR = DOI_TEST_DIR / "raw"
DOI_TEST_STRUCTURED_DIR = DOI_TEST_DIR / "structured"
DOI_TEST_EMBEDDINGS_DIR = DOI_TEST_DIR / "embeddings"
DOI_TEST_METRICS_DIR = DOI_TEST_DIR / "metrics"

EMBEDDINGS_DIR = BASE_DIR / "data" / "embeddings"
EMBEDDINGS_ROUTE_MODERN = EMBEDDINGS_DIR / "Route_A_Modern"
EMBEDDINGS_ROUTE_LEGACY = EMBEDDINGS_DIR / "Route_B_Legacy"

LOG_FILE = LOG_DIR / "system.log"

# --- HARDWARE & COMPUTE (M3 MAX 64GB) ---
DEVICE = "mps"
MODEL_ID = "nomic-ai/nomic-embed-text-v1.5"
TOKEN_LIMIT = 8192
MAX_WORKERS = 8

# --- PHASE 2 EXTRACTION SETTINGS ---
MIN_DIGITAL_TEXT_LENGTH = 500
OCR_DPI = 300
TESSERACT_LANG = "eng"
STOP_SECTION_PATTERN = (
    r"\nReferences|\nLiterature Cited|\nAcknowledgements|\nFunding"
)

# --- DATA ARCHITECTURE ---
EPOCH_STEP = 5
START_YEAR = 1960
END_YEAR = 2026

# --- CONFIGURATION INVARIANTS ---
if TOKEN_LIMIT <= 0:
    raise ValueError("TOKEN_LIMIT must be positive.")

if MAX_WORKERS <= 0:
    raise ValueError("MAX_WORKERS must be positive.")

if MIN_DIGITAL_TEXT_LENGTH <= 0:
    raise ValueError("MIN_DIGITAL_TEXT_LENGTH must be positive.")

if OCR_DPI <= 0:
    raise ValueError("OCR_DPI must be positive.")

if EPOCH_STEP <= 0:
    raise ValueError("EPOCH_STEP must be positive.")

if START_YEAR < 1900:
    raise ValueError("START_YEAR appears invalid for this corpus.")

if START_YEAR > END_YEAR:
    raise ValueError("START_YEAR cannot exceed END_YEAR.")

# --- IDEMPOTENCY GUARD ---
REQUIRED_DIRS = (
    BIN_INGEST,
    BIN_PROCESS,
    BIN_ANALYSIS,
    BIN_UTILS,
    RAW_DIR,
    RAW_ROUTE_MODERN,
    RAW_ROUTE_LEGACY,
    PROCESSED_DIR,
    STRUCTURED_DIR,
    MANIFEST_DIR,
    LOG_DIR,
    TESTING_DIR,
    DOI_TEST_DIR,
    DOI_TEST_RAW_DIR,
    DOI_TEST_STRUCTURED_DIR,
    DOI_TEST_EMBEDDINGS_DIR,
    DOI_TEST_METRICS_DIR,
    EMBEDDINGS_DIR,
    EMBEDDINGS_ROUTE_MODERN,
    EMBEDDINGS_ROUTE_LEGACY,
)

for directory in REQUIRED_DIRS:
    directory.mkdir(parents=True, exist_ok=True)

__all__ = [
    "PROJECT_NAME",
    "PROJECT_TITLE",
    "BASE_DIR",
    "BIN_DIR",
    "BIN_INGEST",
    "BIN_PROCESS",
    "BIN_ANALYSIS",
    "BIN_UTILS",
    "RAW_DIR",
    "RAW_ROUTE_MODERN",
    "RAW_ROUTE_LEGACY",
    "PROCESSED_DIR",
    "STRUCTURED_DIR",
    "MANIFEST_DIR",
    "MASTER_LEDGER",
    "LOG_DIR",
    "TESTING_DIR",
    "DOI_TEST_DIR",
    "DOI_TEST_RAW_DIR",
    "DOI_TEST_STRUCTURED_DIR",
    "DOI_TEST_EMBEDDINGS_DIR",
    "DOI_TEST_METRICS_DIR",
    "EMBEDDINGS_DIR",
    "EMBEDDINGS_ROUTE_MODERN",
    "EMBEDDINGS_ROUTE_LEGACY",
    "LOG_FILE",
    "DEVICE",
    "MODEL_ID",
    "TOKEN_LIMIT",
    "MAX_WORKERS",
    "MIN_DIGITAL_TEXT_LENGTH",
    "OCR_DPI",
    "TESSERACT_LANG",
    "STOP_SECTION_PATTERN",
    "EPOCH_STEP",
    "START_YEAR",
    "END_YEAR",
    "REQUIRED_DIRS",
]