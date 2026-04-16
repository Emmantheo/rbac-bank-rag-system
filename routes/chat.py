# routes/chat.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from deps import get_current_user
from db.session import get_db
from integrations.langfuse_client import langfuse_client
from models.user import User
from schemas.chat import ChatRequest, ChatResponse
from services.audit import log_action
from services.generation import generate_rag_answer
from services.retrieval import build_citations, retrieve_chunks

router = APIRouter()


@router.post("/query", response_model=ChatResponse)
def query_rag(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ChatResponse:
    with langfuse_client.trace(
        name="chat_query",
        user_id=current_user.username,
        input_payload={
            "query": payload.query,
            "role_name": current_user.role_name,
        },
        metadata={
            "feature": "chat",
        },
    ) as trace:
        with langfuse_client.span(
            trace,
            name="retrieval",
            input_payload={
                "query": payload.query,
                "role_name": current_user.role_name,
            },
            metadata={"feature": "retrieval"},
        ) as retrieval_span:
            chunks = retrieve_chunks(
                db=db,
                query=payload.query,
                user_role=current_user.role_name,
            )

            if retrieval_span:
                retrieval_span.update(
                    output={
                        "retrieved_chunk_count": len(chunks),
                        "citations_preview": build_citations(chunks) if chunks else [],
                    }
                )

        if not chunks:
            answer = "no authorized data found for your role."
            citations: list[str] = []
        else:
            answer = generate_rag_answer(
                query=payload.query,
                chunks=chunks,
                trace=trace,
                username=current_user.username,
                role_name=current_user.role_name,
            )

            lowered_answer = answer.lower()
            if (
                "no authorized data found for your role" in lowered_answer
                or "does not answer the question" in lowered_answer
                or "does not fully answer" in lowered_answer
                or "insufficient" in lowered_answer
                or "cannot answer" in lowered_answer
            ):
                citations = []
            else:
                citations = build_citations(chunks)

        with langfuse_client.span(
            trace,
            name="chat_response",
            input_payload={"query": payload.query},
            metadata={
                "feature": "response",
                "role_name": current_user.role_name,
            },
        ) as response_span:
            if response_span:
                response_span.update(
                    output={
                        "answer": answer,
                        "citations": citations,
                    }
                )

    log_action(
        db=db,
        username=current_user.username,
        role_name=current_user.role_name,
        action="rag_query",
        detail=payload.query,
    )

    return ChatResponse(answer=answer, citations=citations)