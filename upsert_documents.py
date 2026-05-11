from __future__ import annotations

import argparse
import hashlib
import os
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import ollama
from pymilvus import DataType, MilvusClient


warnings.filterwarnings(
    "ignore",
    message="pkg_resources is deprecated as an API.*",
    category=UserWarning,
    module=r"milvus_lite.*",
)

PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_DOCUMENTS_DIR = PROJECT_ROOT / "documents"
DEFAULT_COLLECTION_NAME = "demo_collection"
DEFAULT_EMBEDDING_MODEL = "embeddinggemma"
DEFAULT_OLLAMA_HOST = "http://localhost:11434"
DEFAULT_MILVUS_URI = str(PROJECT_ROOT / "pdai.db")

SUPPORTED_EXTENSIONS = {
    ".csv",
    ".html",
    ".htm",
    ".json",
    ".jsonl",
    ".md",
    ".markdown",
    ".rst",
    ".tsv",
    ".txt",
    ".yaml",
    ".yml",
}


@dataclass(frozen=True)
class DocumentChunk:
    id: str
    source: str
    chunk_index: int
    text: str


@dataclass(frozen=True)
class UpsertResult:
    collection_name: str
    document_count: int
    chunk_count: int
    upsert_count: int


def iter_document_paths(documents_dir: Path) -> list[Path]:
    if not documents_dir.exists():
        raise FileNotFoundError(f"documents directory does not exist: {documents_dir}")
    if not documents_dir.is_dir():
        raise NotADirectoryError(f"documents path is not a directory: {documents_dir}")

    paths = [
        path
        for path in documents_dir.rglob("*")
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    ]
    return sorted(paths)


def read_document(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace").strip()


def split_text(text: str, chunk_size: int = 1600, chunk_overlap: int = 200) -> list[str]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")
    if chunk_overlap < 0:
        raise ValueError("chunk_overlap must be greater than or equal to 0")
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    normalized = "\n".join(line.rstrip() for line in text.replace("\r\n", "\n").splitlines()).strip()
    if not normalized:
        return []

    chunks: list[str] = []
    start = 0
    while start < len(normalized):
        end = min(start + chunk_size, len(normalized))
        if end < len(normalized):
            boundary = max(
                normalized.rfind("\n\n", start, end),
                normalized.rfind("\n", start, end),
                normalized.rfind(" ", start, end),
            )
            if boundary > start + (chunk_size // 2):
                end = boundary

        chunk = normalized[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end >= len(normalized):
            break
        start = max(end - chunk_overlap, 0)

    return chunks


def build_chunks(
    documents_dir: Path = DEFAULT_DOCUMENTS_DIR,
    chunk_size: int = 1600,
    chunk_overlap: int = 200,
) -> list[DocumentChunk]:
    chunks: list[DocumentChunk] = []
    for path in iter_document_paths(documents_dir):
        text = read_document(path)
        relative_source = path.relative_to(documents_dir).as_posix()
        for chunk_index, chunk_text in enumerate(split_text(text, chunk_size, chunk_overlap)):
            chunks.append(
                DocumentChunk(
                    id=stable_chunk_id(relative_source, chunk_index),
                    source=relative_source,
                    chunk_index=chunk_index,
                    text=chunk_text,
                )
            )
    return chunks


def stable_chunk_id(source: str, chunk_index: int) -> str:
    payload = f"{source}:{chunk_index}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:32]


def embed_texts(
    texts: Sequence[str],
    model: str = DEFAULT_EMBEDDING_MODEL,
    ollama_host: str | None = None,
    batch_size: int = 16,
) -> list[list[float]]:
    if not texts:
        return []
    if batch_size <= 0:
        raise ValueError("batch_size must be greater than 0")

    client = ollama.Client(host=ollama_host or os.getenv("OLLAMA_HOST") or DEFAULT_OLLAMA_HOST)
    embeddings: list[list[float]] = []

    for start in range(0, len(texts), batch_size):
        batch = texts[start : start + batch_size]
        try:
            response = client.embed(model=model, input=list(batch))
        except Exception as exc:
            raise RuntimeError(
                "failed to create embeddings with Ollama. "
                f"Check that Ollama is running and the model is available: {model}"
            ) from exc

        batch_embeddings = _response_value(response, "embeddings")
        embeddings.extend([list(vector) for vector in batch_embeddings])

    if len(embeddings) != len(texts):
        raise RuntimeError(f"embedding count mismatch: expected {len(texts)}, got {len(embeddings)}")

    return embeddings


def ensure_collection(
    client: MilvusClient,
    collection_name: str,
    dimension: int,
) -> None:
    if dimension <= 0:
        raise ValueError("dimension must be greater than 0")

    if client.has_collection(collection_name=collection_name):
        validate_existing_collection(client, collection_name, dimension)
        return

    schema = MilvusClient.create_schema(auto_id=False, enable_dynamic_field=False)
    schema.add_field("id", DataType.VARCHAR, is_primary=True, max_length=64)
    schema.add_field("vector", DataType.FLOAT_VECTOR, dim=dimension)
    schema.add_field("text", DataType.VARCHAR, max_length=65535)
    schema.add_field("source", DataType.VARCHAR, max_length=1024)
    schema.add_field("chunk_index", DataType.INT64)

    index_params = MilvusClient.prepare_index_params()
    index_params.add_index(field_name="vector", index_type="AUTOINDEX", metric_type="COSINE")

    client.create_collection(
        collection_name=collection_name,
        schema=schema,
        index_params=index_params,
    )


def validate_existing_collection(
    client: MilvusClient,
    collection_name: str,
    dimension: int,
) -> None:
    description = client.describe_collection(collection_name=collection_name)
    fields = {field.get("name"): field for field in description.get("fields", [])}
    required_types = {
        "id": DataType.VARCHAR,
        "vector": DataType.FLOAT_VECTOR,
        "text": DataType.VARCHAR,
        "source": DataType.VARCHAR,
        "chunk_index": DataType.INT64,
    }

    missing_fields = [name for name in required_types if name not in fields]
    if missing_fields:
        raise ValueError(
            f"collection {collection_name!r} is missing required fields: {', '.join(missing_fields)}"
        )

    mismatched_fields = [
        name
        for name, expected_type in required_types.items()
        if fields[name].get("type") != expected_type
    ]
    if mismatched_fields:
        raise ValueError(
            f"collection {collection_name!r} has incompatible field types: {', '.join(mismatched_fields)}"
        )

    existing_dimension = vector_dimension_from_fields(fields)
    if existing_dimension is not None and existing_dimension != dimension:
        raise ValueError(
            f"collection {collection_name!r} has vector dimension {existing_dimension}, "
            f"but generated embeddings have dimension {dimension}"
        )


def vector_dimension_from_fields(fields: dict[object, object]) -> int | None:
    vector_field = fields.get("vector")
    if not isinstance(vector_field, dict):
        return None

    params = vector_field.get("params", {})
    dimension = params.get("dim") if isinstance(params, dict) else None
    return int(dimension) if dimension is not None else None



def upsert_records(
    client: MilvusClient,
    collection_name: str,
    chunks: Sequence[DocumentChunk],
    embeddings: Sequence[Sequence[float]],
    replace_existing: bool = True,
    batch_size: int = 100,
) -> int:
    if len(chunks) != len(embeddings):
        raise ValueError(f"chunk/vector count mismatch: {len(chunks)} chunks, {len(embeddings)} vectors")
    if batch_size <= 0:
        raise ValueError("batch_size must be greater than 0")

    if replace_existing:
        for source in sorted({chunk.source for chunk in chunks}):
            client.delete(collection_name=collection_name, filter=f'source == "{escape_filter_string(source)}"')

    upsert_count = 0
    for start in range(0, len(chunks), batch_size):
        batch_chunks = chunks[start : start + batch_size]
        batch_embeddings = embeddings[start : start + batch_size]
        records = [
            {
                "id": chunk.id,
                "vector": list(vector),
                "text": chunk.text,
                "source": chunk.source,
                "chunk_index": chunk.chunk_index,
            }
            for chunk, vector in zip(batch_chunks, batch_embeddings, strict=True)
        ]
        result = client.upsert(collection_name=collection_name, data=records)
        upsert_count += int(result.get("upsert_count", len(records)))

    return upsert_count


def upsert_documents(
    documents_dir: Path = DEFAULT_DOCUMENTS_DIR,
    milvus_uri: str = DEFAULT_MILVUS_URI,
    collection_name: str = DEFAULT_COLLECTION_NAME,
    embedding_model: str = DEFAULT_EMBEDDING_MODEL,
    ollama_host: str | None = None,
    chunk_size: int = 1600,
    chunk_overlap: int = 200,
    embedding_batch_size: int = 16,
    upsert_batch_size: int = 100,
    replace_existing: bool = True,
) -> UpsertResult:
    chunks = build_chunks(documents_dir, chunk_size, chunk_overlap)
    if not chunks:
        raise ValueError(f"no supported non-empty documents found in {documents_dir}")

    embeddings = embed_texts(
        [chunk.text for chunk in chunks],
        model=embedding_model,
        ollama_host=ollama_host,
        batch_size=embedding_batch_size,
    )
    dimension = len(embeddings[0])

    client = MilvusClient(milvus_uri)
    ensure_collection(client, collection_name, dimension)
    upsert_count = upsert_records(
        client,
        collection_name,
        chunks,
        embeddings,
        replace_existing=replace_existing,
        batch_size=upsert_batch_size,
    )

    return UpsertResult(
        collection_name=collection_name,
        document_count=len({chunk.source for chunk in chunks}),
        chunk_count=len(chunks),
        upsert_count=upsert_count,
    )


def escape_filter_string(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def _response_value(response: object, key: str) -> object:
    if isinstance(response, dict):
        return response[key]
    return getattr(response, key)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Upsert local documents into Milvus using Ollama embeddings.")
    parser.add_argument("--documents-dir", type=Path, default=DEFAULT_DOCUMENTS_DIR)
    parser.add_argument("--milvus-uri", default=os.getenv("MILVUS_URI", DEFAULT_MILVUS_URI))
    parser.add_argument("--collection-name", default=DEFAULT_COLLECTION_NAME)
    parser.add_argument("--embedding-model", default=DEFAULT_EMBEDDING_MODEL)
    parser.add_argument("--ollama-host", default=os.getenv("OLLAMA_HOST", DEFAULT_OLLAMA_HOST))
    parser.add_argument("--chunk-size", type=int, default=1600)
    parser.add_argument("--chunk-overlap", type=int, default=200)
    parser.add_argument("--embedding-batch-size", type=int, default=16)
    parser.add_argument("--upsert-batch-size", type=int, default=100)
    parser.add_argument("--no-replace-existing", action="store_true")
    parser.add_argument("--dry-run", action="store_true", help="Read and chunk documents without calling Ollama or Milvus.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.dry_run:
        chunks = build_chunks(args.documents_dir, args.chunk_size, args.chunk_overlap)
        document_count = len({chunk.source for chunk in chunks})
        print(f"dry run: {document_count} documents, {len(chunks)} chunks")
        return

    result = upsert_documents(
        documents_dir=args.documents_dir,
        milvus_uri=args.milvus_uri,
        collection_name=args.collection_name,
        embedding_model=args.embedding_model,
        ollama_host=args.ollama_host,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        embedding_batch_size=args.embedding_batch_size,
        upsert_batch_size=args.upsert_batch_size,
        replace_existing=not args.no_replace_existing,
    )
    print(
        f"upserted {result.upsert_count} chunks from {result.document_count} documents "
        f"into {result.collection_name}"
    )


if __name__ == "__main__":
    main()
