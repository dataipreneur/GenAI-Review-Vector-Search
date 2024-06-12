from flask import Flask, request, jsonify
from pymongo import MongoClient
import openai
import numpy as np
from scipy.spatial.distance import cosine
import asyncio

app = Flask(__name__)

# OpenAI API key
openai.api_key = 'key'
print(openai.api_key)

# MongoDB configuration
mongo_uri = "mongo_uri"
db_name = "sample_mflix"
collection_name = "movies"
print(mongo_uri)
# Connect to MongoDB
client = MongoClient(mongo_uri)
db = client[db_name]
collection = db[collection_name]
print(db)

def get_openai_embedding(text):
    try:

        print("Open AI success")
        response = openai.Embed.create(model="text-davinci-003", documents=[text])
        return np.array(response['data'][0]['embedding'])
    
    except openai.error.OpenAIError as e:
        print(f"Error getting embedding: {e}")
        raise


@app.route('/search', methods=['POST'])
def search_vector():
    print("2")
    try:
        # Get input text from the request
        input_text = request.json['text']

        # Get OpenAI embedding for the input text
        input_vector = get_openai_embedding(input_text)

        # Fetch all documents from the MongoDB collection
        documents = collection.find()

        # Calculate cosine similarity for each document
        results = []
        for document in documents:
            stored_vector = np.array(document['embedding'])
            similarity = 1 - cosine(input_vector, stored_vector)
            results.append({'document_id': str(document['_id']), 'similarity': similarity})

        # Sort the results by similarity (higher similarity first)
        results = sorted(results, key=lambda x: x['similarity'], reverse=True)

        return jsonify({'results': results})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("main")
    app.run()