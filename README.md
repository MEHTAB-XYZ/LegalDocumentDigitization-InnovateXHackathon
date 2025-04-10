# Legal Judgment Explorer — AI-Powered Search Engine for Court Cases

**Hackathon Project | DUK Hackathon (March 15–16, 2025)**  
**Problem Statement:** Build a scalable, intuitive system to digitize and semantically explore legal judgments using AI.

---

## Overview

This project is a comprehensive solution designed to digitize, organize, and intelligently search a large dataset of court judgments using modern NLP and vector search techniques. Built during a 36-hour hackathon, the goal was to make complex legal documents easily explorable through an AI-powered interface.

---

## Features

- Digitization of unstructured court judgment text files
- Semantic search using Sentence Transformers and FAISS
- Metadata-based filtering (judge name, date, etc.)
- Fuzzy string matching for robust query handling
- Chatbot interface for conversational access to judgments
- Scalable architecture designed for continuous addition of new documents

---

## Technical Stack

- Python, FAISS, Sentence Transformers
- Fuzzy Matching (SequenceMatcher)
- Streamlit for the UI
- OpenAI (optional, for chatbot prototype)

---

## How It Works

1. **Data Preprocessing**  
   Legal case documents are split using a custom delimiter and cleaned to remove noise.

2. **Embedding Generation**  
   Sentence embeddings are generated using `all-MiniLM-L6-v2` to capture semantic meaning.

3. **Index Creation with FAISS**  
   Vector embeddings are indexed with FAISS for fast similarity searches.

4. **Filtering and Matching**  
   Exact and fuzzy matching are used to filter cases by judge name and other metadata.

5. **Retrieval Function**  
   A combined semantic + metadata search returns the most relevant cases to a query.

6. **Saving and Reuse**  
   The FAISS index and cleaned case data are stored for quick future access.

---

## Future Improvements

- Add support for court-specific metadata (respondent, case number, etc.)
- Improve chatbot capabilities with RAG or custom fine-tuned models
- Deploy a full-stack version with database support and authentication

---

## Contribution

This project was developed as part of a team effort during the DUK Hackathon. Contributions are welcome for improvements, refactoring, or deploying to production.

