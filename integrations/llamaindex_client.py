import tempfile
from pathlib import Path

from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter


def parse_document_bytes(file_bytes: bytes, file_name: str) -> str:
    suffix = Path(file_name).suffix or ".txt"

    with tempfile.TemporaryDirectory() as tmp_dir:
        temp_path = Path(tmp_dir) / f"input{suffix}"
        temp_path.write_bytes(file_bytes)

        documents = SimpleDirectoryReader(input_files=[str(temp_path)]).load_data()
        return "".join(doc.text for doc in documents if doc.text).strip()


def split_text_into_chunks(
    text: str,
    chunk_size: int = 700,
    chunk_overlap: int = 100,
) -> list[str]:
    splitter = SentenceSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return [chunk.strip() for chunk in splitter.split_text(text) if chunk and chunk.strip()]