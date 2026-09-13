import os
import json
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import (
    RunnablePassthrough,
    RunnableLambda
)

from pydantic import BaseModel, Field


# ---------------------------------------------------------
# PROJECT PATHS
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

VECTORSTORE_PATH = BASE_DIR / "vectorstore"
ENV_FILE = BASE_DIR / ".env"


# ---------------------------------------------------------
# LOAD ENVIRONMENT VARIABLES
# ---------------------------------------------------------

load_dotenv(ENV_FILE)


HF_TOKEN = os.getenv("HF_TOKEN")

if not HF_TOKEN:
    raise ValueError(
        "HF_TOKEN was not found. Please check your .env file."
    )


# ---------------------------------------------------------
# HUGGING FACE LLAMA
# ---------------------------------------------------------

client = InferenceClient(
    model="meta-llama/Llama-3.1-8B-Instruct",
    api_key=HF_TOKEN
)


# ---------------------------------------------------------
# EMBEDDING MODEL
# ---------------------------------------------------------

def get_embedding_function():

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    return embeddings


embedding_function = get_embedding_function()


# ---------------------------------------------------------
# LOAD CHROMA VECTORSTORE
# ---------------------------------------------------------

vectorstore = Chroma(
    persist_directory=str(VECTORSTORE_PATH),
    embedding_function=embedding_function
)


# ---------------------------------------------------------
# RETRIEVER
# ---------------------------------------------------------

retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 4}
)


# ---------------------------------------------------------
# FORMAT DOCUMENTS
# ---------------------------------------------------------

def format_docs(docs):

    return "\n\n".join(
        doc.page_content
        for doc in docs
    )


# ---------------------------------------------------------
# NORMAL RAG PROMPT
# ---------------------------------------------------------

QA_PROMPT = """
You are a precise document question-answering assistant.

Answer the user's question using ONLY the information contained
in the provided context.

Rules:

1. Do not use outside knowledge.
2. Do not guess or invent information.
3. If the answer cannot be found in the context, say:
   "I don't know based on the provided documents."
4. Preserve important numbers, dates, percentages, names,
   and financial figures exactly as stated.
5. Give a concise and direct answer.
6. Do not provide hidden chain-of-thought or internal reasoning.

Context:
{context}

Question:
{question}

Answer:
"""


qa_prompt_template = ChatPromptTemplate.from_template(QA_PROMPT)


# ---------------------------------------------------------
# CALL LLAMA
# ---------------------------------------------------------

def call_llama(prompt_value):

    response = client.chat_completion(
        messages=[
            {
                "role": "user",
                "content": prompt_value.to_string()
            }
        ],
        max_tokens=300
    )

    return response.choices[0].message.content


# ---------------------------------------------------------
# RAG CHAIN
# ---------------------------------------------------------

rag_chain = (
    {
        "context": retriever | format_docs,
        "question": RunnablePassthrough()
    }
    | qa_prompt_template
    | RunnableLambda(call_llama)
)


# ---------------------------------------------------------
# ASK QUESTION
# ---------------------------------------------------------

def ask_question(question):

    return rag_chain.invoke(question)


# ---------------------------------------------------------
# STRUCTURED EXTRACTION MODEL
# ---------------------------------------------------------

class ExtractedInfo(BaseModel):

    document_title: Optional[str] = Field(
        description="Title of the document"
    )

    document_title_evidence: Optional[str] = Field(
        description="Brief evidence supporting the document title"
    )

    company_name: Optional[str] = Field(
        description="Name of the company"
    )

    company_name_evidence: Optional[str] = Field(
        description="Brief evidence supporting the company name"
    )

    fiscal_year_end: Optional[str] = Field(
        description="End date of the fiscal year"
    )

    fiscal_year_end_evidence: Optional[str] = Field(
        description="Brief evidence supporting the fiscal year end"
    )

    headquarters: Optional[str] = Field(
        description="Company headquarters or principal executive office"
    )

    headquarters_evidence: Optional[str] = Field(
        description="Brief evidence supporting the headquarters"
    )

    total_net_sales: Optional[str] = Field(
        description="Total net sales for the fiscal year"
    )

    total_net_sales_evidence: Optional[str] = Field(
        description="Brief evidence supporting total net sales"
    )

    net_income: Optional[str] = Field(
        description="Net income for the fiscal year"
    )

    net_income_evidence: Optional[str] = Field(
        description="Brief evidence supporting net income"
    )

    total_assets: Optional[str] = Field(
        description="Total assets at the end of the fiscal year"
    )

    total_assets_evidence: Optional[str] = Field(
        description="Brief evidence supporting total assets"
    )

    total_liabilities: Optional[str] = Field(
        description="Total liabilities at the end of the fiscal year"
    )

    total_liabilities_evidence: Optional[str] = Field(
        description="Brief evidence supporting total liabilities"
    )

    business_description: Optional[str] = Field(
        description="Brief description of the company's business"
    )

    business_description_evidence: Optional[str] = Field(
        description="Brief evidence supporting the business description"
    )


# ---------------------------------------------------------
# STRUCTURED EXTRACTION PROMPT
# ---------------------------------------------------------

EXTRACTION_PROMPT = """
You are a precise document information extraction assistant.

Extract information ONLY from the provided context.

Rules:

1. Do not use outside knowledge.
2. Do not guess or invent information.
3. If a field cannot be found in the context,
   return null for both the field and its evidence.
4. Preserve numbers, dates, currencies, and units exactly
   as they appear.
5. For every extracted field, provide brief evidence
   directly supported by the context.
6. Do not provide hidden chain-of-thought or internal reasoning.
7. Evidence should be a short factual explanation or relevant
   text from the context.
8. Return ONLY valid JSON.
9. Do not include markdown or ```json code fences.

Return JSON using exactly these fields:

{{
    "document_title": null,
    "document_title_evidence": null,

    "company_name": null,
    "company_name_evidence": null,

    "fiscal_year_end": null,
    "fiscal_year_end_evidence": null,

    "headquarters": null,
    "headquarters_evidence": null,

    "total_net_sales": null,
    "total_net_sales_evidence": null,

    "net_income": null,
    "net_income_evidence": null,

    "total_assets": null,
    "total_assets_evidence": null,

    "total_liabilities": null,
    "total_liabilities_evidence": null,

    "business_description": null,
    "business_description_evidence": null
}}

Context:
{context}

Question:
{question}
"""


# ---------------------------------------------------------
# STRUCTURED EXTRACTION
# ---------------------------------------------------------

def extract_structured_info(question):

    relevant_chunks = retriever.invoke(question)

    context_text = "\n\n---\n\n".join(
        chunk.page_content
        for chunk in relevant_chunks
    )

    prompt = EXTRACTION_PROMPT.format(
        context=context_text,
        question=question
    )

    response = client.chat_completion(
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_tokens=700
    )

    raw_output = response.choices[0].message.content

    data = json.loads(raw_output)

    extracted_info = ExtractedInfo(**data)

    return extracted_info


# ---------------------------------------------------------
# CONVERT STRUCTURED RESULT TO TABLE
# ---------------------------------------------------------

def structured_info_to_dataframe(result):

    import pandas as pd

    structured_response = result.model_dump()

    rows = []

    for field, value in structured_response.items():

        if field.endswith("_evidence"):
            continue

        evidence = structured_response.get(
            f"{field}_evidence"
        )

        field_name = field.replace(
            "_", " "
        ).title()

        rows.append({
            "Field": field_name,
            "Value": value,
            "Evidence": evidence
        })

    return pd.DataFrame(rows)

def get_retrieved_chunks(question):
    return retriever.invoke(question)
def get_knowledge_base_info():
    """
    Return basic information about the documents
    currently stored in the Chroma vectorstore.
    """

    data = vectorstore.get()

    metadatas = data.get("metadatas", [])

    documents = set()

    for metadata in metadatas:

        if not metadata:
            continue

        source = metadata.get("source")

        if source:
            documents.add(
                os.path.basename(source)
            )

    return {
        "total_chunks": len(metadatas),
        "documents": sorted(documents)
    }