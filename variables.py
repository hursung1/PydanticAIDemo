from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_COLLECTION_NAME = "demo_collection"
DEFAULT_EMBEDDING_MODEL = "embeddinggemma"
DEFAULT_OLLAMA_HOST = "http://localhost:11434"
DEFAULT_MILVUS_URI = str(PROJECT_ROOT / "pdai.db")