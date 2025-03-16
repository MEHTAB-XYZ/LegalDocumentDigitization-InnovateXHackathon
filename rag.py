import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Load the extracted text
EXTRACTED_TEXT_FILE = "C:\\Users\\mehta\\Downloads\\dataset-innovatex-test-output\\extracted_text.txt"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"  # Lightweight, fast, and free

# Load embedding model
embedding_model = SentenceTransformer(MODEL_NAME)

# Read and logically separate cases
def load_cases(file_path):
    cases = []
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
    
    # Assuming cases are separated by "--- Extracted Text from:"
    raw_cases = text.split("--- Extracted Text from:")[1:]
    for case in raw_cases:
        case = case.strip()
        if case:
            cases.append(case)
    return cases

cases = load_cases(EXTRACTED_TEXT_FILE)

# Ensure cases were extracted
if not cases:
    print("Error: No cases were extracted. Check the extracted_text.txt format.")
    exit()

print(f"Number of cases loaded: {len(cases)}")

# Create embeddings
case_embeddings = embedding_model.encode(cases, convert_to_numpy=True)

# Create FAISS index
d = case_embeddings.shape[1]  # Embedding dimensionality
index = faiss.IndexFlatL2(d)
index.add(case_embeddings)

# Check the number of entries in the FAISS index
print(f"Number of entries in FAISS index: {index.ntotal}")

# Function to get the most relevant cases
def retrieve_cases(query, top_k=3, judge_name=None, date=None):
    query_embedding = embedding_model.encode([query], convert_to_numpy=True)
    distances, indices = index.search(query_embedding, top_k)
    retrieved_cases = [cases[i] for i in indices[0] if i < len(cases)]

    # Apply filters
    if judge_name:
        retrieved_cases = [case for case in retrieved_cases if judge_name.lower() in case.lower()]
    if date:
        retrieved_cases = [case for case in retrieved_cases if date in case]

    return retrieved_cases

# Save index
faiss.write_index(index, "case_embeddings.index")
np.save("case_ids.npy", cases)

print("✅ Embeddings created & saved!")
