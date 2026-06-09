import json
import re
from pathlib import Path

RAW_DIR = Path("data/raw")
OUTPUT_FILE = Path("data/chunks.json")

CHUNK_SIZE = 700
OVERLAP = 100


def clean_text(text: str) -> str:
    """Clean copied Rate My Professors text."""
    text = text.replace("\r", "\n")

    # Remove common clutter words/lines.
    clutter_patterns = [
        r"Helpful",
        r"Thumbs up",
        r"Thumbs down",
        r"Rate",
        r"Compare",
        r"I'm Professor.*",
        r"Jump To Ratings.*",
        r"Similar Professors",
        r"Discover more",
    ]

    for pattern in clutter_patterns:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)

    # Normalize whitespace.
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)

    return text.strip()


def get_professor_name(text: str, file_path: Path) -> str:
    """Try to find professor name from the file; fallback to filename."""
    match = re.search(r"Professor:\s*(.+)", text)
    if match:
        return match.group(1).strip()

    return file_path.stem.replace("_", " ").title()


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = OVERLAP) -> list[str]:
    """Split text into overlapping character chunks."""
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


def load_and_chunk_documents():
    all_chunks = []

    txt_files = sorted(RAW_DIR.glob("*.txt"))

    if not txt_files:
        raise FileNotFoundError("No .txt files found in data/raw/")

    for file_path in txt_files:
        raw_text = file_path.read_text(encoding="utf-8")
        cleaned = clean_text(raw_text)
        professor_name = get_professor_name(cleaned, file_path)
        chunks = chunk_text(cleaned)

        for i, chunk in enumerate(chunks):
            all_chunks.append({
                "id": f"{file_path.stem}_{i}",
                "text": chunk,
                "metadata": {
                    "source": file_path.name,
                    "professor": professor_name,
                    "chunk_index": i
                }
            })

    return all_chunks


def main():
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    chunks = load_and_chunk_documents()

    OUTPUT_FILE.write_text(
        json.dumps(chunks, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print(f"Saved {len(chunks)} chunks to {OUTPUT_FILE}")
    print("\nSample chunks:\n")

    for chunk in chunks[:5]:
        print("=" * 80)
        print(f"ID: {chunk['id']}")
        print(f"Source: {chunk['metadata']['source']}")
        print(f"Professor: {chunk['metadata']['professor']}")
        print(chunk["text"][:700])
        print()


if __name__ == "__main__":
    main()