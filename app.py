from flask import Flask, request, jsonify
from flask_cors import CORS
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import os

app = Flask(__name__)
CORS(app)

# Initialize RAG components
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
try:
    embedding_model = SentenceTransformer(MODEL_NAME)
    index = faiss.read_index("case_embeddings.index")
    cases = np.load("case_ids.npy", allow_pickle=True)
except Exception as e:
    print(f"Error loading RAG components: {str(e)}")

@app.route('/search-cases', methods=['POST'])
def search_cases():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No filters provided"}), 400

        filters = {
            'judge': data.get('judge', ''),
            'caseNo': data.get('caseNo', ''),
            'crimeNo': data.get('crimeNo', ''),
            'keyword': data.get('keyword', ''),
            'petitioner': data.get('petitioner', ''),
            'lawyer': data.get('lawyer', ''),
            'location': data.get('location', ''),
            'timeframe': data.get('timeframe', '')
        }

        # Check if at least one filter is provided
        if not any(filters.values()):
            return jsonify({"status": "error", "message": "At least one filter must be provided"}), 400

        # Construct query from filters
        query_parts = []
        for key, value in filters.items():
            if value:
                query_parts.append(value)
        query = " ".join(query_parts)

        # Use RAG to retrieve cases
        query_embedding = embedding_model.encode([query], convert_to_numpy=True)
        distances, indices = index.search(query_embedding, 10)  # Get top 10 results
        retrieved_cases = [cases[i] for i in indices[0] if i < len(cases)]

        # Apply additional filtering
        filtered_cases = []
        for case in retrieved_cases:
            case_text = str(case).lower()
            matches_all = True
            
            for key, value in filters.items():
                if value and value.lower() not in case_text:
                    matches_all = False
                    break
            
            if matches_all:
                filtered_cases.append(case)

        return jsonify({
            "status": "success",
            "cases": filtered_cases[:10]  # Limit to 10 results
        })

    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Error processing request. Please try again."
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(debug=True, port=5000) 