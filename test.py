import os
import easyocr
import fitz  # PyMuPDF

# Initialize the easyocr reader
reader = easyocr.Reader(['en'])  # Supports English

def pdf_to_text(pdf_path):
    """Extract text from a scanned PDF using EasyOCR."""
    text = ""
    try:
        # Open the PDF using PyMuPDF
        doc = fitz.open(pdf_path)
        
        # Iterate through each page
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            
            # Get the image of the page
            pix = page.get_pixmap()
            img_bytes = pix.tobytes()  # Convert image to bytes
            
            # Perform OCR on the image
            result = reader.readtext(img_bytes)
            for detection in result:
                text += detection[1] + " "  # Append the detected text
        
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
    return text

def process_document(file_path):
    """Process a single document and return extracted text."""
    if file_path.endswith(".pdf"):
        return pdf_to_text(file_path)
    elif file_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    else:
        print(f"Unsupported file format: {file_path}")
        return ""

def process_all_documents(input_dir, output_file):
    """Extract text from all documents and save to a single text file."""
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    document_paths = [
        os.path.join(input_dir, file_name)
        for file_name in os.listdir(input_dir)
        if file_name.endswith(".pdf") or file_name.endswith(".txt")
    ]

    with open(output_file, "w", encoding="utf-8") as output:
        for file_path in document_paths:
            extracted_text = process_document(file_path)
            if extracted_text.strip():
                output.write(f"\n--- Extracted Text from: {file_path} ---\n")
                output.write(extracted_text + "\n")

    print(f"All extracted text saved to: {output_file}")

if __name__ == "__main__":
    input_dir = "C:\\Users\\mehta\\Downloads\\dataset-innovatex-test-input"
    output_file = "C:\\Users\\mehta\\Downloads\\dataset-innovatex-test-output\\extracted_text.txt"
    process_all_documents(input_dir, output_file)
