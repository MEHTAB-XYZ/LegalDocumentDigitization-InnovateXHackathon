from flask import Flask, request, jsonify
from rag import retrieve_cases
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    query = data.get('query', '')
    print(f"Received request with data: {data}")
    if not query:
        print("No query provided in the request.")
        return jsonify({'error': 'No query provided'}), 400
    
    # Retrieve cases using the chatbot functionality
    try:
        retrieved_cases = retrieve_cases(query)
        print(f"Retrieved cases: {retrieved_cases}")
    except Exception as e:
        print(f"Error retrieving cases: {e}")
        return jsonify({'error': 'Error retrieving cases'}), 500
    
    return jsonify({'cases': retrieved_cases})

@app.route('/retrieve-judge', methods=['POST'])
def retrieve_judge_cases():
    data = request.json
    judge = data.get('judge', '')
    print(f"Received request for judge: {judge}")
    
    if not judge:
        return jsonify({'error': 'No judge name provided'}), 400
    
    try:
        # Use the retrieve_cases function with judge filter
        cases = retrieve_cases(query="", judge_name=judge)
        print(f"Retrieved cases for judge {judge}: {cases}")
        return jsonify({'cases': cases})
    except Exception as e:
        print(f"Error retrieving cases for judge {judge}: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 