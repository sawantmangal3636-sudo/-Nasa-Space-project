import json
import faiss
import numpy as np
import os
import sys
from sentence_transformers import SentenceTransformer
#from google.generativeai import genai  # ❌ Gemini import commented out
#from google.genai.errors import APIError
#from google.api_core.exceptions import GoogleAPIError
from typing import List, Dict, Any, Optional

# --- Configuration & Initialization ---
KNOWLEDGE_BASE_PATH = "knowledge_base.json"
FAISS_INDEX_PATH = "faiss_index.index"
LOGGING_PATH = "external_texts.json"  # Used for Step 3 logging
# EXTERNAL_INDEX_FILE = "external_faiss_index.index"  # ❌ External FAISS commented out

# --- Helper Functions ---
def _load_json(file_path: str) -> List[Dict[str, Any]]:
    """Loads JSON data safely."""
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        return []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Error decoding JSON file {file_path}: {e}")
        return []

def _save_json(file_path: str, data: Any):
    """Saves data to JSON file."""
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def log_new_qa(query: str, answer: str, file_path: str = LOGGING_PATH):
    """
    Step 3 logging: For Gemini answers (commented out now)
    """
    # ❌ Gemini logging disabled
    pass

# --- Chatbot Class ---
class Chatbot:
    def __init__(self, 
                 knowledge_file: str = KNOWLEDGE_BASE_PATH,
                 index_file: str = FAISS_INDEX_PATH):
                 # external_text_file: str = LOGGING_PATH,
                 # external_index_file: str = EXTERNAL_INDEX_FILE):
        
        try:
            self.model = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception as e:
            print(f"❌ Error initializing SentenceTransformer: {e}")
            self.model = None
            sys.exit(1)

        # --- Knowledge Base (Step 1) ---
        self.knowledge_base = _load_json(knowledge_file)
        try:
            self.index = faiss.read_index(index_file)
        except Exception:
            print(f"⚠️ Warning: Could not load primary FAISS index {index_file}. KB search disabled.")
            self.index = None

        # ❌ External QA / FAISS index commented out
        # self.external_qa = _load_json(external_text_file)
        # try:
        #     self.external_index = faiss.read_index(external_index_file)
        # except Exception:
        #     self.external_index = None

    def get_embedding(self, text: str) -> np.ndarray:
        if not self.model: 
            return np.array([0]*384).astype("float32")
        return self.model.encode([text], convert_to_numpy=True, normalize_embeddings=True).astype("float32")

    def search(self, query: str, top_k: int = 1) -> List[Dict[str, Any]]:
        """Performs vector search on the primary FAISS index only."""
        if not self.index:
            return []
        
        vector = self.get_embedding(query)
        distances, indices = self.index.search(vector, top_k)

        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx < len(self.knowledge_base):
                item = self.knowledge_base[idx]
                results.append({
                    "question": item.get("question", ""),
                    "answer": item.get("answer", ""),
                    "score": float(dist)
                })
        return results

    def ask(self, query: str) -> str:
        """Search KB, if not found return 'question out of scope'."""
        FAISS_THRESHOLD = 0.5
        results = self.search(query, top_k=1)
        if results and results[0]["score"] < FAISS_THRESHOLD:
            return f"**[KB HIT]** {results[0]['answer']}"
        
        # ❌ Step 2 Gemini API call commented out
        # ❌ Step 3 logging commented out
        return "question out of scope"

# --- Global Initialization ---
try:
    hybrid_chatbot_instance = Chatbot() 
except Exception as e:
    print(f"Fatal Error during Chatbot initialization: {e}")
    hybrid_chatbot_instance = None 

def get_chatbot_response(query: str) -> str:
    if hybrid_chatbot_instance:
        return hybrid_chatbot_instance.ask(query)
    else:
        return "🚨Chatbot service is unavailable due to initialization error."