import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import json

# Load the extracted text
EXTRACTED_TEXT_FILE = r"C:\Users\mehta\Downloads\dataset-innovatex-test-output\extracted_text.txt"
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

# Print the first few cases to verify content
print("Sample cases:")
for i, case in enumerate(cases[:3]):
    print(f"Case {i+1}: {case[:100]}...")  # Print the first 100 characters of each case

# Create embeddings
case_embeddings = embedding_model.encode(cases, convert_to_numpy=True)

# Create FAISS index
d = case_embeddings.shape[1]  # Embedding dimensionality
index = faiss.IndexFlatL2(d)
index.add(case_embeddings)

# Check the number of entries in the FAISS index
print(f"Number of entries in FAISS index: {index.ntotal}")

# Function to get the most relevant cases
def retrieve_cases(query, top_k=3):
    query_embedding = embedding_model.encode([query], convert_to_numpy=True)
    print(f"Query Embedding: {query_embedding}")
    distances, indices = index.search(query_embedding, top_k)
    print(f"Distances: {distances}, Indices: {indices}")
    retrieved_cases = [cases[i] for i in indices[0] if i < len(cases)]
    if not retrieved_cases:
        print("No matching cases found.")
    return retrieved_cases

# Save index
faiss.write_index(index, "case_embeddings.index")
np.save("case_ids.npy", cases)

print("✅ Embeddings created & saved!")

import json
import numpy as np

def search_cases(query, top_k=3):
    query_embedding = embedding_model.encode([query], convert_to_numpy=True)
    D, I = index.search(query_embedding, top_k)  # Get top-k results
    
    # Load stored case IDs
    case_ids = np.load("case_ids.npy")

    # Load the JSON file containing case data
    with open(r"C:/Users/mehta/Downloads/dataset-innovatex-test-output/all_extracted_cases.json", "r", encoding="utf-8") as f:
        case_data = json.load(f)
    
    # Retrieve and print case content
    results = []
    for i in I[0]:
        case_id = case_ids[i]
        if case_id in case_data:
            results.append(case_data[case_id]["text"])  # Print full case text instead of filename
    
    return results

# Example: Search for cases on "17 May"
query ='HARUN-UL-RASHID'

matching_cases = search_cases(query)

print("🔍 Top matching case contents:")
for idx, case in enumerate(matching_cases, 1):
    print(f"\n--- Case {idx} ---\n{case}\n")
