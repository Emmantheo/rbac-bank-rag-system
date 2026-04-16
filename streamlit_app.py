from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import requests
import streamlit as st


API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000").rstrip("/")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "60"))


st.set_page_config(
    page_title="CBN Policy & Compliance RAG",
    page_icon="📘",
    layout="wide",
)


def api_url(path: str) -> str:
    if not path.startswith("/"):
        path = f"/{path}"
    return f"{API_BASE_URL}{path}"


def get_auth_headers() -> Dict[str, str]:
    token = st.session_state.get("access_token")
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}


def safe_request(
    method: str,
    path: str,
    json: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
) -> tuple[bool, Any]:
    try:
        response = requests.request(
            method=method,
            url=api_url(path),
            json=json,
            params=params,
            headers=get_auth_headers(),
            timeout=REQUEST_TIMEOUT,
        )

        try:
            data = response.json()
        except Exception:
            data = response.text

        if response.ok:
            return True, data

        return False, data

    except requests.RequestException as exc:
        return False, {"detail": f"request failed: {exc}"}


def initialize_state() -> None:
    defaults = {
        "access_token": None,
        "current_user": None,
        "roles": [],
        "chat_history": [],
        "roles_loaded": False,
        "workspace_tab": "chat",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def load_roles() -> List[str]:
    ok, data = safe_request("GET", "/auth/roles")

    if not ok:
        st.session_state["roles"] = []
        return []

    if isinstance(data, list):
        roles = [item.get("name", "") for item in data if item.get("name")]
        st.session_state["roles"] = roles
        return roles

    st.session_state["roles"] = []
    return []


def render_header() -> None:
    st.markdown(
        """
        <div style="padding: 1rem 0 0.5rem 0;">
            <h1 style="margin-bottom: 0.2rem;">CBN Policy & Compliance RAG</h1>
            <p style="margin-top: 0; color: #6b7280;">
                Secure role-based regulatory knowledge assistant
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown("## Navigation")
        st.caption(f"API Base URL: `{API_BASE_URL}`")

        if st.session_state.get("current_user"):
            user = st.session_state["current_user"]
            st.success("Logged in")
            st.markdown(
                f"""
                **Username:** {user.get('username', 'N/A')}  
                **Role:** {user.get('role', 'N/A')}
                """
            )

            st.markdown("---")
            st.markdown("## Workspace")

            if st.button("Chat Assistant", use_container_width=True):
                st.session_state["workspace_tab"] = "chat"
                st.rerun()

            if st.button("Document Ingestion", use_container_width=True):
                st.session_state["workspace_tab"] = "ingestion"
                st.rerun()

            st.markdown("---")

            if st.button("Logout", use_container_width=True):
                st.session_state["access_token"] = None
                st.session_state["current_user"] = None
                st.session_state["chat_history"] = []
                st.session_state["workspace_tab"] = "chat"
                st.rerun()
        else:
            st.info("Not logged in")

        st.markdown("---")
        st.markdown("## Quick Actions")

        if st.button("Refresh Roles", use_container_width=True):
            roles = load_roles()
            st.session_state["roles_loaded"] = True
            if roles:
                st.success("Roles loaded successfully")
            else:
                st.error("Could not load roles from the API")


def render_auth_tabs() -> None:
    st.markdown("## Authentication")

    if not st.session_state.get("roles_loaded"):
        load_roles()
        st.session_state["roles_loaded"] = True

    register_tab, login_tab = st.tabs(["Register", "Login"])

    with register_tab:
        with st.form("register_form", clear_on_submit=False):
            st.markdown("### Create account")
            full_name = st.text_input("Full name", placeholder="enter your full name")
            email = st.text_input("Email", placeholder="enter your email address")
            username = st.text_input("Username", placeholder="enter a username")
            password = st.text_input("Password", type="password")

            roles = st.session_state.get("roles", [])
            role = st.selectbox(
                "Role",
                options=roles if roles else ["No roles available"],
                disabled=not bool(roles),
                help="select one of the predefined system roles",
            )

            register_submitted = st.form_submit_button("Register", use_container_width=True)

            if register_submitted:
                if not roles:
                    st.error("Roles could not be loaded. Check that the API is running and /auth/roles is available.")
                elif not full_name.strip() or not email.strip() or not username.strip() or not password.strip():
                    st.error("Full name, email, username, and password are required.")
                else:
                    payload = {
                        "full_name": full_name.strip(),
                        "email": email.strip(),
                        "username": username.strip(),
                        "password": password.strip(),
                        "role": role,
                    }
                    ok, data = safe_request("POST", "/auth/register", json=payload)

                    if ok:
                        st.session_state["access_token"] = data.get("access_token")
                        user = data.get("user", {})
                        st.session_state["current_user"] = {
                            "full_name": user.get("full_name", full_name.strip()),
                            "email": user.get("email", email.strip()),
                            "username": user.get("username", username.strip()),
                            "role": user.get("role", role),
                        }
                        st.success("Registration successful.")
                        st.rerun()
                    else:
                        detail = data.get("detail") if isinstance(data, dict) else str(data)
                        st.error(detail or "Registration failed.")

    with login_tab:
        with st.form("login_form", clear_on_submit=False):
            st.markdown("### Sign in")
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            login_submitted = st.form_submit_button("Login", use_container_width=True)

            if login_submitted:
                if not username.strip() or not password.strip():
                    st.error("Username and password are required.")
                else:
                    payload = {
                        "username": username.strip(),
                        "password": password.strip(),
                    }
                    ok, data = safe_request("POST", "/auth/login", json=payload)

                    if ok:
                        st.session_state["access_token"] = data.get("access_token")
                        user_data = data.get("user", {}) if isinstance(data, dict) else {}
                        st.session_state["current_user"] = {
                            "full_name": user_data.get("full_name", ""),
                            "email": user_data.get("email", ""),
                            "username": user_data.get("username", username.strip()),
                            "role": user_data.get("role", ""),
                        }
                        st.session_state["workspace_tab"] = "chat"
                        st.success("Login successful.")
                        st.rerun()
                    else:
                        detail = data.get("detail") if isinstance(data, dict) else str(data)
                        st.error(detail or "Login failed.")


def render_ingestion_panel() -> None:
    st.markdown("## Document ingestion")

    current_user = st.session_state.get("current_user")
    if not current_user:
        st.info("Login to ingest documents.")
        return

    current_role = (current_user.get("role") or "").strip().lower()

    st.caption("Documents you upload are automatically restricted to your own role.")

    with st.form("ingestion_form"):
        uploaded_file = st.file_uploader(
            "Upload document",
            type=["pdf", "docx", "txt"],
            help="upload a regulatory document in pdf, docx, or txt format",
        )

        st.text_input(
            "Allowed role",
            value=current_role,
            disabled=True,
        )

        ingest_submitted = st.form_submit_button("Ingest document", use_container_width=True)

        if ingest_submitted:
            if uploaded_file is None:
                st.error("Please upload a document.")
            elif not current_role:
                st.error("Your account role could not be determined.")
            else:
                files = {
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        uploaded_file.type or "application/octet-stream",
                    )
                }

                try:
                    response = requests.post(
                        api_url("/ingestion/upload"),
                        files=files,
                        headers=get_auth_headers(),
                        timeout=REQUEST_TIMEOUT,
                    )

                    try:
                        payload = response.json()
                    except Exception:
                        payload = response.text

                    if response.ok:
                        if isinstance(payload, dict) and payload.get("status") == "duplicate":
                            st.warning(payload.get("message", "Duplicate document"))
                        elif isinstance(payload, dict) and payload.get("status") == "failed":
                            st.error(payload.get("message", "Document ingestion failed"))
                        else:
                            st.success(f"Document ingested successfully for role: {current_role}")
                    else:
                        detail = payload.get("detail") if isinstance(payload, dict) else str(payload)
                        st.error(detail or "Ingestion failed.")

                except requests.RequestException as exc:
                    st.error(f"request failed: {exc}")


def render_chat_interface() -> None:
    st.markdown("## Compliance assistant")

    current_user = st.session_state.get("current_user")
    if not current_user:
        st.info("Please register or login to start chatting.")
        return

    role = current_user.get("role", "")
    st.caption(f"Current role context: **{role}**")

    chat_container = st.container()

    with chat_container:
        for item in st.session_state.get("chat_history", []):
            with st.chat_message(item["role"]):
                st.markdown(item["content"])

    prompt = st.chat_input("Ask a policy or compliance question")

    if prompt:
        st.session_state["chat_history"].append(
            {"role": "user", "content": prompt}
        )

        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    payload = {
                        "query": prompt,
                        "user_role": role,
                    }
                    ok, data = safe_request("POST", "/chat/query", json=payload)

                    if ok:
                        answer = data.get("answer", "No response returned.")
                    else:
                        answer = (
                            data.get("detail", "Request failed.")
                            if isinstance(data, dict)
                            else str(data)
                        )

                    st.markdown(answer)

                    st.session_state["chat_history"].append(
                        {
                            "role": "assistant",
                            "content": answer,
                            "citations": [],
                        }
                    )


def render_status_panel() -> None:
    st.markdown("---")
    ok, data = safe_request("GET", "/api/health")
    if ok:
        st.success("API is healthy")
    else:
        st.error("API health check failed")
        st.json(data)


def render_authenticated_workspace() -> None:
    st.markdown("## Workspace")

    current_tab = st.session_state.get("workspace_tab", "chat")

    if current_tab == "ingestion":
        render_ingestion_panel()
    else:
        render_chat_interface()


def main() -> None:
    initialize_state()
    render_header()
    render_sidebar()

    if not st.session_state.get("current_user"):
        render_auth_tabs()
    else:
        render_authenticated_workspace()

    


if __name__ == "__main__":
    main()