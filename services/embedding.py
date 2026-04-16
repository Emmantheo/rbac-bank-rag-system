from integrations.llm_client import generate_embedding


def embed_text(text: str) -> list[float]:
    return generate_embedding(text)
