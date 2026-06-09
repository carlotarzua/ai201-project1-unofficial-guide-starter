import json
import shutil
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

CHUNKS_FILE = Path("data/chunks.json")
CHROMA_DIR = Path("chroma_db")
COLLECTION_NAME = "depaul_professor_reviews"
MODEL_NAME = "all-MiniLM-L6-v2"


KNOWN_PROFESSORS = {
    "eric landahl": "Eric Landahl",
    "kristina thomas": "Kristina Thomas",
    "yang choi": "Yang Choi",
    "kenny castellanos": "Kenny Castellanos",
    "nancy brown": "Nancy Brown",
    "xorla ocloo": "Xorla Ocloo",
    "juan hu": "Juan Hu",
    "emily barnard": "Emily Barnard",
    "naomi wangler": "Naomi Wangler",
    "kaitlyn bolyard": "Kaitlyn Bolyard",
}


def load_chunks():
    if not CHUNKS_FILE.exists():
        raise FileNotFoundError("data/chunks.json not found. Run `python ingest.py` first.")

    with CHUNKS_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def detect_professor_filter(query):
    query_lower = query.lower()

    for name_lower, official_name in KNOWN_PROFESSORS.items():
        if name_lower in query_lower:
            return official_name

    return None


def get_collection():
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return client.get_or_create_collection(name=COLLECTION_NAME)


def build_vector_store(force_rebuild=False):
    if force_rebuild and CHROMA_DIR.exists():
        shutil.rmtree(CHROMA_DIR)

    chunks = load_chunks()
    model = SentenceTransformer(MODEL_NAME)
    collection = get_collection()

    existing_count = collection.count()
    if existing_count > 0:
        print(f"Collection already has {existing_count} chunks.")
        print("Skipping rebuild. Use force_rebuild=True to rebuild.")
        return collection

    documents = []
    ids = []
    metadatas = []

    for chunk in chunks:
        professor = chunk["metadata"]["professor"]
        source = chunk["metadata"]["source"]

        # Add professor/source text directly into the embedded document.
        # This improves retrieval when the user asks about a specific professor.
        embedded_text = (
            f"Professor: {professor}\n"
            f"Source: {source}\n\n"
            f"{chunk['text']}"
        )

        documents.append(embedded_text)
        ids.append(chunk["id"])
        metadatas.append(chunk["metadata"])

    print(f"Embedding {len(documents)} chunks...")
    embeddings = model.encode(documents).tolist()

    collection.add(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    print(f"Added {len(documents)} chunks to ChromaDB.")
    return collection


def retrieve(query, top_k=4):
    model = SentenceTransformer(MODEL_NAME)
    collection = get_collection()

    query_embedding = model.encode([query]).tolist()[0]
    professor_filter = detect_professor_filter(query)

    query_args = {
        "query_embeddings": [query_embedding],
        "n_results": top_k,
        "include": ["documents", "metadatas", "distances"],
    }

    if professor_filter:
        query_args["where"] = {"professor": professor_filter}

    results = collection.query(**query_args)

    retrieved = []

    for doc, metadata, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        retrieved.append(
            {
                "text": doc,
                "metadata": metadata,
                "distance": distance,
            }
        )

    return retrieved


def print_results(query):
    print("\n" + "=" * 80)
    print(f"QUERY: {query}")
    print("=" * 80)

    professor_filter = detect_professor_filter(query)
    if professor_filter:
        print(f"Metadata filter applied: professor = {professor_filter}")

    results = retrieve(query, top_k=4)

    for i, result in enumerate(results, start=1):
        metadata = result["metadata"]
        print(f"\nResult {i}")
        print(f"Professor: {metadata.get('professor')}")
        print(f"Source: {metadata.get('source')}")
        print(f"Chunk index: {metadata.get('chunk_index')}")
        print(f"Distance: {result['distance']:.4f}")
        print("-" * 80)
        print(result["text"][:900])


def main():
    build_vector_store(force_rebuild=True)

    test_queries = [
        "What do students say about Eric Landahl's lecture style?",
        "Is Kenny Castellanos described as difficult?",
        "What do students say about Kaitlyn Bolyard's feedback and grading?",
        "Which professors are described as caring or helpful?",
        "What complaints do students make about Kristina Thomas?",
    ]

    for query in test_queries:
        print_results(query)


if __name__ == "__main__":
    main()