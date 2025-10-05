from flask import Flask, request, jsonify
import json
import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
# import google.generativeai as genai  # ❌ Commented Gemini import

# ----------------- CONFIG -----------------
FAISS_INDEX_PATH = "faiss_index.index"                # Knowledge Base
EXTERNAL_FAISS_PATH = "external_faiss_index.index"   # External Sources
KNOWLEDGE_JSON = "knowledge_base.json"
EXTERNAL_LOG = "external_texts.json"
HUGGINGFACE_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
# -----------------------------------------

app = Flask(__name__)

# ----------------- INITIALIZE -----------------
embeddings = HuggingFaceEmbeddings(model_name=HUGGINGFACE_MODEL)

# Load Knowledge Base FAISS index
if os.path.exists(FAISS_INDEX_PATH):
    faiss_index = FAISS.load_local(
        FAISS_INDEX_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )
else:
    faiss_index = None
    print("⚠️ Knowledge FAISS index not found. Run ingest.py first.")

# Load External FAISS index
if os.path.exists(EXTERNAL_FAISS_PATH):
    external_faiss_index = FAISS.load_local(
        EXTERNAL_FAISS_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )
else:
    external_faiss_index = None
    print("⚠️ External FAISS index not found. Run ingest.py first.")

# Load knowledge base JSON
if os.path.exists(KNOWLEDGE_JSON):
    with open(KNOWLEDGE_JSON, "r", encoding="utf-8") as f:
        knowledge_data = json.load(f)
else:
    knowledge_data = []

# Ensure external log exists
if not os.path.exists(EXTERNAL_LOG):
    with open(EXTERNAL_LOG, "w", encoding="utf-8") as f:
        json.dump([], f)


# ----------------- FAISS SEARCH -----------------
def search_faiss(query, k=3):
    if not query or query.strip() == "":
        return []

    results = []

    if faiss_index:
        kb_results = faiss_index.similarity_search(query, k=k)
        results.extend(kb_results)

    if external_faiss_index:
        ext_results = external_faiss_index.similarity_search(query, k=k)
        results.extend(ext_results)

    return [doc.page_content for doc in results]


# ----------------- LOGGING -----------------
def log_external_qa(question, answer):
    with open(EXTERNAL_LOG, "r+", encoding="utf-8") as f:
        data = json.load(f)
        data.append({"question": question, "answer": answer})
        f.seek(0)
        json.dump(data, f, indent=2)
        f.truncate()


# ----------------- GEMINI FALLBACK (Commented Out) -----------------
"""
# Configure Gemini API
GEN_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GEN_API_KEY:
    GEN_API_KEY = "AIzaSyAX9Ni8hj84V0OOwhsf7buKYLTTLcuShYc"
genai.configure(api_key=GEN_API_KEY)

# Example Gemini model
GEMINI_MODEL = "models/gemini-2.5-t"

def ask_gemini(question, context_docs):
    context_text = "\n\n".join(context_docs) if context_docs else ""
    prompt = (
        f"Answer only using the following documents/websites/GitHub repo if relevant:\n"
        f"{context_text}\n\n"
        f"Question: {question}\nAnswer:"
    )
    try:
        response = genai.generate_text(
            model=GEMINI_MODEL,
            prompt=prompt,
            temperature=0
        )
        answer = response.text.strip()
        return answer if answer else "question out of scope"
    except Exception as e:
        print("Gemini API error:", e)
        return "question out of scope"
"""


# ----------------- FLASK ENDPOINT -----------------
@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    if not data or "query" not in data:
        return jsonify({"error": "No query provided"}), 400

    user_query = data.get("query")
    if not user_query or user_query.strip() == "":
        return jsonify({"error": "Empty query"}), 400

    # Step 1: Search both FAISS knowledge bases
    context_docs = search_faiss(user_query)

    if context_docs:
        answer = "\n\n".join(context_docs)
    else:
        # Step 2: Gemini fallback commented, return 'question out of scope' instead
        # answer = ask_gemini(user_query, context_docs)
        answer = "question out of scope"

        # Step 3: Gemini logging commented
        # if answer and answer != "question out of scope":
        #     log_external_qa(user_query, answer)

    return jsonify({"answer": answer})


# ----------------- RUN -----------------
if __name__ == "__main__":
    app.run(debug=True)
# ----------------- INGESTION SCRIPT -----------------