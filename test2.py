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
