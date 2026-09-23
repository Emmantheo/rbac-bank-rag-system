# Demo
https://github.com/user-attachments/assets/406d8edc-3888-40b6-a567-587e7003373c


# XYZ Bank Internal RBAC RAG System

A role-based internal retrieval-augmented generation system for secure document ingestion, semantic retrieval, and question answering across regulated business functions.

This application allows internal users to register under a predefined role, upload documents restricted to their own role, and query only the knowledge they are authorized to access.

## Overview

The system is designed for controlled internal knowledge access in banking and regulated environments. It combines document ingestion, embedding generation, pgvector-based retrieval, role-based access control, and LLM answer generation.

Each user is assigned a role such as:

- admin
- auditor
- compliance
- legal
- risk

Uploaded documents are automatically restricted to the uploader's role. During retrieval, the system filters results so users only receive knowledge from documents authorized for their role.

## Core Features

### role-based access control
- users register with a predefined role
- role is stored with the user profile
- users can only upload documents into their own role
- users can only retrieve and query documents within their own role

### document ingestion
- upload supported for pdf, docx, and txt files
- uploaded files are stored in Azure Blob Storage
- extracted text is parsed with LlamaIndex readers
- documents are chunked before embedding
- duplicate files are prevented using SHA-256 hashing

### vector retrieval
- embeddings are generated with OpenAI embeddings
- embeddings are stored in PostgreSQL using pgvector
- retrieval is performed from pgvector using semantic similarity
- retrieved results are restricted by role

### answer generation
- chat responses are generated using OpenAI chat completions
- answers are grounded only in authorized retrieved context
- unauthorized users receive no protected content
- citations are human readable using document title and section label

### observability
- Langfuse is integrated for tracing ingestion and chat flows
- retrieval and generation spans are captured
- useful for evaluation, debugging, and monitoring

### streamlit interface
- user registration and login
- side navigation for workspace switching
- separate workspace areas for:
  - document ingestion
  - chat assistant

## High Level Architecture

```text
web ui
    |
    v
fastapi backend
    |
    +--> auth and rbac
    +--> ingestion service
    |       |
    |       +--> azure blob storage
    |       +--> llamaindex parsing
    |       +--> hashing
    |       +--> openai embeddings
    |       +--> postgresql + pgvector
    |
    +--> retrieval service
    |       |
    |       +--> role-filtered pgvector similarity search
    |
    +--> generation service
            |
            +--> openai chat completion
            +--> langfuse tracing







