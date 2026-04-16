from pathlib import Path
from openai import OpenAI
from core.config import settings


client = OpenAI(api_key=settings.openai_api_key)


def generate_embedding(text: str) -> list[float]:
    response = client.embeddings.create(
        model=settings.embedding_model,
        input=text,
    )
    return response.data[0].embedding


def generate_answer(prompt: str, system_prompt: str) -> str:
    response = client.chat.completions.create(
        model=settings.chat_model,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content or ""


def load_prompt(filename: str) -> str:
    base = Path(__file__).resolve().parent / "prompts"
    path = (base / filename).resolve()
    return path.read_text(encoding="utf-8")