from typing import Sequence

from integrations.langfuse_client import langfuse_client
from integrations.llm_client import generate_answer, load_prompt
from models.chunk import Chunk
from core.config import settings


system_prompt = load_prompt("system_prompts.md")


def _source_label(chunk: Chunk) -> str:
    title = "Untitled document"
    if chunk.document and chunk.document.title:
        title = chunk.document.title
    return f"{title} (section {chunk.chunk_index + 1})"


def _build_context(chunks: Sequence[Chunk]) -> str:
    parts: list[str] = []

    for chunk in chunks:
        source_label = _source_label(chunk)
        parts.append(f"[source: {source_label}]\n{chunk.content}")

    return "\n\n".join(parts)


def generate_rag_answer(
    query: str,
    chunks: Sequence[Chunk],
    *,
    trace=None,
    username: str | None = None,
    role_name: str | None = None,
) -> str:
    if not chunks:
        return "no authorized data found for your role."

    context = _build_context(chunks)

    prompt = f"""
user question:
{query}

authorized context:
{context}

instructions:
- answer only from the authorized context
- if the context is not enough, say so clearly
- cite only when the answer is supported by the authorized context
- if the context does not answer the question, do not invent a citation
- include a final line starting with: citation: only when there is real supporting context
- do not invent citations
""".strip()

    if not trace:
        return generate_answer(
            prompt=prompt,
            system_prompt=system_prompt,
        )

    with langfuse_client.generation(
        trace,
        name="chat_generation",
        model=settings.chat_model,
        input_payload={
            "query": query,
            "role_name": role_name,
            "retrieved_chunk_count": len(chunks),
            "sources": [_source_label(chunk) for chunk in chunks],
        },
        metadata={
            "feature": "rag_answer",
            "username": username,
            "role_name": role_name,
        },
    ) as generation:
        answer = generate_answer(
            prompt=prompt,
            system_prompt=system_prompt,
        )

        if generation:
            generation.update(output=answer)

        return answer