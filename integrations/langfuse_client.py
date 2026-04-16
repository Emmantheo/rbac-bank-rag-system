import os
from contextlib import contextmanager

from core.config import settings

try:
    from langfuse import get_client, propagate_attributes
except Exception:
    get_client = None
    propagate_attributes = None


class LangfuseClient:
    def __init__(self) -> None:
        self.client = None

        if (
            get_client
            and settings.langfuse_secret_key
            and settings.langfuse_public_key
        ):
            os.environ["LANGFUSE_SECRET_KEY"] = settings.langfuse_secret_key
            os.environ["LANGFUSE_PUBLIC_KEY"] = settings.langfuse_public_key
            os.environ["LANGFUSE_BASE_URL"] = settings.langfuse_host

            self.client = get_client()

    @property
    def enabled(self) -> bool:
        return self.client is not None

    def auth_check(self) -> bool:
        if not self.client:
            return False
        try:
            return bool(self.client.auth_check())
        except Exception:
            return False

    @contextmanager
    def trace(
        self,
        name: str,
        user_id: str | None = None,
        input_payload: dict | None = None,
        metadata: dict | None = None,
    ):
        if not self.client:
            yield None
            return

        with self.client.start_as_current_observation(
            as_type="span",
            name=name,
            input=input_payload,
            metadata=metadata or {},
        ) as root_span:
            if propagate_attributes:
                with propagate_attributes(
                    user_id=user_id,
                    session_id=user_id,
                    metadata=metadata or {},
                    trace_name=name,
                ):
                    yield root_span
            else:
                yield root_span

    @contextmanager
    def generation(
        self,
        parent,
        *,
        name: str,
        model: str,
        input_payload: dict | str,
        metadata: dict | None = None,
    ):
        if not parent:
            yield None
            return

        with parent.start_as_current_observation(
            as_type="generation",
            name=name,
            model=model,
            input=input_payload,
            metadata=metadata or {},
        ) as generation:
            yield generation

    @contextmanager
    def span(
        self,
        parent,
        *,
        name: str,
        input_payload: dict | None = None,
        metadata: dict | None = None,
    ):
        if not parent:
            yield None
            return

        with parent.start_as_current_observation(
            as_type="span",
            name=name,
            input=input_payload,
            metadata=metadata or {},
        ) as span:
            yield span

    def flush(self) -> None:
        if self.client:
            try:
                self.client.flush()
            except Exception:
                pass


langfuse_client = LangfuseClient()