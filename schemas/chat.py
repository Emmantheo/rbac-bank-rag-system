from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    query: str


class ChatResponse(BaseModel):
    answer: str
    citations: list[str] = Field(default_factory=list)
