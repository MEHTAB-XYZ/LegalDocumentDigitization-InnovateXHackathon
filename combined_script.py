import os
import json
import fitz  # PyMuPDF for reading PDFs
import easyocr
import numpy as np
import cv2

# Input and Output Directories
INPUT_DIR = "C:/Users/mehta/Downloads/dataset-innovatex-test-input"
OUTPUT_DIR = "C:/Users/mehta/Downloads/dataset-innovatex-test-output"
TEXT_FILE = os.path.join(OUTPUT_DIR, "extracted_text.txt")
JSON_FILE = os.path.join(OUTPUT_DIR, "all_extracted_cases.json")

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'])

# Dictionary to store all extracted cases
all_cases = {}

# Function to preprocess text
def preprocess_text(text):
    """Cleans up the extracted text."""
    text = text.replace("\n", " ").replace("_", " ")
    text = " ".join(text.split())  # Remove extra spaces
    return text

# Function to convert PDF page to image (NumPy array)
def pdf_page_to_image(pdf_page):
    """Converts a PDF page to an image for OCR processing."""
    pixmap = pdf_page.get_pixmap()
    img = np.frombuffer(pixmap.samples, dtype=np.uint8).reshape((pixmap.h, pixmap.w, pixmap.n))
    return cv2.cvtColor(img, cv2.COLOR_RGB2BGR)  # Convert to BGR for OpenCV

# Process each PDF in the input directory
for filename in os.listdir(INPUT_DIR):
    if filename.lower().endswith(".pdf"):
        pdf_path = os.path.join(INPUT_DIR, filename)
        case_id = os.path.splitext(filename)[0]  # Extract case ID from filename

        print(f"Processing: {filename}...")

        try:
            # Open the PDF
            extracted_text = ""
            doc = fitz.open(pdf_path)

            for page in doc:
                img = pdf_page_to_image(page)  # Convert page to image
                text = reader.readtext(img, detail=0)  # Extract text using EasyOCR
                text = " ".join(text)
                extracted_text += preprocess_text(text) + "\n"

            # Save extracted text to a common text file
            with open(TEXT_FILE, "a", encoding="utf-8") as f:
                f.write(f"--- Extracted Text from: {filename} ---\n")
                f.write(extracted_text + "\n\n")

            # Create structured data for JSON output
            case_data = {
                "case_id": case_id,
                "court_name": None,
                "judge_name": None,
                "case_number": None,
                "date": None,
                "petitioner": None,
                "accused": None,
                "respondent": None,
                "text": extracted_text
            }

            # Store in combined dictionary
            all_cases[case_id] = case_data

            # Save extracted data as an individual JSON file
            json_path = os.path.join(OUTPUT_DIR, f"{case_id}.json")
            with open(json_path, "w", encoding="utf-8") as json_file:
                json.dump(case_data, json_file, ensure_ascii=False, indent=4)

        except Exception as e:
            print(f"❌ Error processing {filename}: {e}")
            continue

# Save all extracted cases into a single JSON file
with open(JSON_FILE, "w", encoding="utf-8") as json_file:
    json.dump(all_cases, json_file, ensure_ascii=False, indent=4)

print("✅ OCR processing completed successfully!")



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

# Create embeddings
case_embeddings = embedding_model.encode(cases, convert_to_numpy=True)

# Create FAISS index
d = case_embeddings.shape[1]  # Embedding dimensionality
index = faiss.IndexFlatL2(d)
index.add(case_embeddings)

# Function to get the most relevant cases
def retrieve_cases(query, top_k=3):
    query_embedding = embedding_model.encode([query], convert_to_numpy=True)
    distances, indices = index.search(query_embedding, top_k)
    retrieved_cases = [cases[i] for i in indices[0]]
    return retrieved_cases

# Chatbot loop
def chat():
    print("Legal Case Retrieval System is ready! Type 'exit' to stop.")
    while True:
        query = input("You: ")
        if query.lower() == "exit":
            break
        retrieved_cases = retrieve_cases(query)
        print("\n📌 **Top Matching Cases:**\n")
        for i, case in enumerate(retrieved_cases, 1):
            print(f"🔹 **Case {i}:**\n{case[:1000]}...")  # Show first 1000 characters
            print("\n" + "-"*80 + "\n")

# Start chatbot
chat()

# Add a function to process documents and create embeddings on demand
'''def process_and_create_embeddings():
    # Process documents to extract text
    process_all_documents(INPUT_DIR, TEXT_FILE)

    # Load cases from JSON
    cases = load_cases(JSON_FILE)

    # Create embeddings for the cases
    create_embeddings(cases)

# Remove the automatic processing on startup
# if __name__ == "__main__":
#     process_and_create_embeddings()'''
