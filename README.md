# 🔍 Fake2Fact — AI-Powered Fact-Checking System

> An AI-powered fact-checking application that uses **Retrieval-Augmented Generation (RAG)**, **semantic search**, **vector embeddings**, and **Large Language Models (LLMs)** to retrieve relevant fact-checking evidence and generate concise, evidence-based explanations for user claims.

---

## 📌 Overview

**Fake2Fact** is an AI-powered fact-checking platform designed to help users investigate potentially misleading or false claims.

Instead of relying only on an LLM's internal knowledge, Fake2Fact follows a **Retrieval-Augmented Generation (RAG)** approach:

1. The user submits a claim.
2. The claim is converted into a vector embedding.
3. Relevant articles are retrieved from a PostgreSQL vector database.
4. The retrieved article URLs are processed to extract their original content.
5. The relevant evidence is provided to an LLM.
6. The LLM generates a concise explanation based on the retrieved information.

The main goal is to combine **semantic retrieval + external evidence + LLM generation** to provide more grounded fact-checking responses.

---

##  Key Features

-  **Semantic Search**
  - Converts user claims into vector embeddings.
  - Finds semantically similar fact-checking/news articles.

-  **Vector Database**
  - Uses PostgreSQL with `pgvector`.
  - Performs similarity search using vector distance.

-  **LLM-Powered Explanation**
  - Uses Google Gemini to generate explanations from retrieved evidence.

-  **Article Extraction**
  - Uses `newspaper3k` to extract article content from URLs.

- 🔗 **Evidence-Based Responses**
  - Retrieves relevant articles before generating the final response.

-  **Web Application**
  - Built using Flask.
  - Provides a simple interface for submitting claims.

- 🗄️ **PostgreSQL Database**
  - Stores news articles, metadata, and vector embeddings.

- 📊 **Similarity Scores**
  - Returns similarity information for retrieved articles.

## Application File System Architecture

```text
fake2fact.ai
│
├── Presentation Layer
│   ├── templates/
│   │   ├── index.html
│   │   └── about.html
│   │
│   └── static/
│       ├── css/
│       │   └── style.css
│       ├── js/
│       │   └── interaction.js
│       └── images/
│
├── Application Layer
│   └── app.py
│       ├── Flask Routes
│       ├── Request Handling
│       ├── Query Embedding
│       ├── Semantic Search
│       ├── Article Extraction
│       └── Gemini LLM Integration
│
├── Data Layer
│   ├── data_preprocessing&vector_database_format.py
│   ├── vector_database_create.py
│   └── full_article_store_in_postgres.py
│
├── Configuration
│   ├── requirements.txt
│   └── .gitignore
│
└── Documentation
    └── README.md
---

#  System Architecture

```text
                    ┌─────────────────────┐
                    │       User          │
                    │   Enters a Claim    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    Flask Backend    │
                    │   /claim_checking   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ SentenceTransformer │
                    │  all-MiniLM-L6-v2   │
                    └──────────┬──────────┘
                               │
                        Query Embedding
                               │
                               ▼
             ┌─────────────────────────────────┐
             │       PostgreSQL + pgvector     │
             │                                 │
             │  Semantic Similarity Search     │
             │  using Vector Embeddings       │
             └───────────────┬─────────────────┘
                             │
                    Relevant Articles
                             │
                             ▼
             ┌─────────────────────────────────┐
             │          newspaper3k            │
             │                                 │
             │     Extract Original Article    │
             │           Content               │
             └───────────────┬─────────────────┘
                             │
                       Retrieved Evidence
                             │
                             ▼
             ┌─────────────────────────────────┐
             │          Google Gemini          │
             │             LLM                 │
             │                                 │
             │  Analyze + Explain Evidence     │
             └───────────────┬─────────────────┘
                             │
                             ▼
                    ┌─────────────────────┐
                    │    Final Result     │
                    │ Evidence-Based      │
                    │ Explanation         │
                    └─────────────────────┘
