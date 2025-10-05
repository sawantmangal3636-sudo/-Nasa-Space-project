from vector_utils import build_faiss_index, load_json, save_json
from data_loaders import scrape_website, clone_github_repo
import os
from typing import List, Dict, Any
import requests
from bs4 import BeautifulSoup
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# --- Configuration ---

# File paths (relative to the 'backend' directory)
KNOWLEDGE_FILE = "knowledge_base.json"
EXTERNAL_FILE = "external_texts.json"
INDEX_FILE = "faiss_index.index"
EXTERNAL_INDEX_FILE = "external_faiss_index.index"

# External sources
WEB_SOURCES = [
    "https://science.nasa.gov/biological-physical/data/",
    "https://public.ksc.nasa.gov/nslsl/",
    "https://taskbook.nasaprs.com/tbp/welcome.cfm"
]
GITHUB_REPO = "https://github.com/jgalazka/SB_publications"
REPO_DIR = "repo_data"  # Matches the default in data_loaders.py

# --- Index Building Functions ---

def build_faiss_index(data, index_file):
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")  # your embedding model
    texts = [item["answer"] for item in data]
    metadatas = [{"question": item["question"]} for item in data]

    faiss_index = FAISS.from_texts(texts, embeddings, metadatas=metadatas)
    faiss_index.save_local(index_file)  # Saves automatically
    return faiss_index   # <--- important!

def build_knowledge_index():
    """
    Builds the primary FAISS index (Step 1 KB) from the internal Q&A JSON.
    """
    print(f"\nBuilding primary index from: {KNOWLEDGE_FILE}...")
    try:
        data: List[Dict[str, str]] = load_json(KNOWLEDGE_FILE)
        
        # This function (from vector_utils) handles embedding and indexing the data
        faiss_index = build_faiss_index(data, INDEX_FILE)
        
        print(f" Primary FAISS index built with {len(data)} knowledge base items in {INDEX_FILE}.")
    except FileNotFoundError:
        print(f" Error: {KNOWLEDGE_FILE} not found. Ensure it's populated.")
    except Exception as e:
        print(f" Error building knowledge index: {e}")

def scrape_website(url: str, min_text_len: int = 200) -> list:
    """
    Scrapes main paragraph content from a webpage.
    Returns a list of text chunks (paragraphs).
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Get all <p> tags that have meaningful content
        paragraphs = [p.get_text().strip() for p in soup.find_all('p')]
        paragraphs = [p for p in paragraphs if len(p) >= min_text_len]

        return paragraphs
    except Exception as e:
        print(f" Failed to scrape {url}: {e}")
        return []

def build_external_index():
    """
    Scrapes external sources, saves the content to a JSON, and builds a secondary FAISS index.
    """
    print("\nBuilding external data index...")
    data: List[Dict[str, str]] = []

    # Scrape websites
    for url in WEB_SOURCES:
        chunks = scrape_website(url, 200)
        for i, paragraph in enumerate(chunks):
            data.append({
                "question": f"What information is provided in paragraph {i+1} from {url}?",
                "answer": paragraph
            })

    # GitHub repo
    repo_texts = clone_github_repo(GITHUB_REPO, local_dir=REPO_DIR)
    for i, text in enumerate(repo_texts):
        data.append({"question": f"GitHub content {i}", "answer": text})

    # Save the raw external data
    save_json(EXTERNAL_FILE, data)
    print(f"✅ External data saved to {EXTERNAL_FILE}.")

    # Build the FAISS index for the external data
    if data:
        # ❌ The external FAISS index is optional / for RAG. Commented if not using Gemini.
        # build_faiss_index(data, EXTERNAL_INDEX_FILE)
        # print(f"✅ External FAISS index built with {len(data)} items in {EXTERNAL_INDEX_FILE}.")
        pass
    else:
        print("⚠️ No external data collected. External index not built.")

if __name__ == "__main__":
    
    # --- DEMO SETUP (Create dummy files if they don't exist) ---
    if not os.path.exists(KNOWLEDGE_FILE):
        print(f"Creating dummy {KNOWLEDGE_FILE}...")
        dummy_kb = [
            {"id": 1, "question": "What is the mission of NSLSL?", "answer": "The NASA Space Life Sciences Lab (NSLSL) supports research for human spaceflight."},
            {"id": 2, "question": "What is the Task Book?", "answer": "The NASA Human Research Program's Task Book tracks research tasks and progress."}
        ]
        save_json(KNOWLEDGE_FILE, dummy_kb)
        
    if not os.path.exists(EXTERNAL_FILE):
        # Initialize external file as empty
        save_json(EXTERNAL_FILE, [])

    # --- Run Ingestion ---
    print("--- STARTING DATA INGESTION ---")
    
    # Build the core index for fast lookups (Step 1)
    build_knowledge_index() 
    
    # Build the index from external sources (optional, Gemini / RAG commented out)
    build_external_index()

    print("\n--- INGESTION COMPLETE ---")



# import os
# import json
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain.vectorstores import FAISS
# from langchain.embeddings import HuggingFaceEmbeddings
# import requests
# from bs4 import BeautifulSoup
# from github import Github

# # --------------------------
# # Helper functions to fetch resources
# # --------------------------
# def fetch_website_text(url):
#     res = requests.get(url)
#     soup = BeautifulSoup(res.text, "html.parser")
#     return ' '.join([p.get_text() for p in soup.find_all('p')])

# def fetch_github_repo_text(repo_url, token=None):
#     g = Github(token) if token else Github()
#     repo_name = '/'.join(repo_url.rstrip('/').split('/')[-2:])
#     repo = g.get_repo(repo_name)
#     texts = []
#     for file in repo.get_contents(""):
#         if file.path.endswith((".md",".txt",".py")):
#             texts.append(file.decoded_content.decode())
#     return ' '.join(texts)

# # --------------------------
# # Main ingestion
# # --------------------------
# def main():
#     resources = {
#         "website1": "https://science.nasa.gov/biological-physical/data/",
#         "website2": "https://public.ksc.nasa.gov/nslsl/",
#         "website3": "https://taskbook.nasaprs.com/tbp/welcome.cfm",
#         "github_repo": "https://github.com/jgalazka/SB_publications"
#     }

#     knowledge_texts = []
#     for name, url in resources.items():
#         if "github.com" in url:
#             knowledge_texts.append(fetch_github_repo_text(url))
#         else:
#             knowledge_texts.append(fetch_website_text(url))

#     # Save JSON knowledge base
#     with open("knowledge_base.json", "w", encoding="utf-8") as f:
#         json.dump({"resources": knowledge_texts}, f, indent=4, ensure_ascii=False)

#     # Create FAISS index
#     text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
#     docs = text_splitter.split_text(' '.join(knowledge_texts))
#     embeddings = HuggingFaceEmbeddings()
#     faiss_index = FAISS.from_texts(docs, embeddings)
#     faiss_index.save_local("faiss_index")
#     print("Knowledge base + FAISS index created successfully!")

# if __name__ == "__main__":
#     main()