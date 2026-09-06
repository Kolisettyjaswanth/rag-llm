# RAG Document Intelligence Assistant

An end-to-end Retrieval-Augmented Generation (RAG) application that allows users to ask questions and extract structured information from PDF documents using semantic search and a large language model.

## Overview

This project implements a document-based question answering system using:

- Python
- LangChain
- ChromaDB
- Hugging Face Llama 3.1 8B Instruct
- Sentence Transformers
- Streamlit
- Pydantic
- Docker

The system processes PDF documents, converts their content into semantic vector representations, retrieves relevant document chunks, and provides the retrieved context to an LLM to generate grounded responses.

## Architecture

```text
PDF Documents
      ↓
PyPDFLoader
      ↓
Text Extraction
      ↓
Recursive Character Chunking
      ↓
all-MiniLM-L6-v2 Embeddings
      ↓
ChromaDB Vector Store
      ↓
Semantic Retrieval
      ↓
Relevant Document Chunks
      ↓
Prompt + Context + Question
      ↓
Llama 3.1 8B Instruct
      ↓
Grounded Answer