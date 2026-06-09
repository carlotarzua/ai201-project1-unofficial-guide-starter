import os
from dotenv import load_dotenv
from groq import Groq

from retrieve import build_vector_store, retrieve

load_dotenv()

MODEL_NAME = "llama-3.3-70b-versatile"


def format_context(chunks):
    context_parts = []

    for i, chunk in enumerate(chunks, start=1):
        metadata = chunk["metadata"]
        professor = metadata.get("professor", "Unknown professor")
        source = metadata.get("source", "Unknown source")

        context_parts.append(
            f"[Source {i}]\n"
            f"Professor: {professor}\n"
            f"File: {source}\n"
            f"Text:\n{chunk['text']}"
        )

    return "\n\n---\n\n".join(context_parts)


def ask(question, top_k=4):
    retrieved_chunks = retrieve(question, top_k=top_k)
    context = format_context(retrieved_chunks)

    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    system_prompt = """
You are an assistant for The Unofficial Guide to DePaul Professors.

Answer the user's question using ONLY the provided retrieved source chunks.
Do not use outside knowledge.
If the retrieved chunks do not contain enough information to answer, say:
"I don't have enough information in the provided sources to answer that."

When you answer, cite the professor names and source filenames that support your answer.
Be honest about mixed or contradictory student reviews.
"""

    user_prompt = f"""
Question:
{question}

Retrieved source chunks:
{context}
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt.strip()},
            {"role": "user", "content": user_prompt.strip()},
        ],
        temperature=0.2,
    )

    answer = response.choices[0].message.content

    sources = []
    for chunk in retrieved_chunks:
        metadata = chunk["metadata"]
        source_label = f"{metadata.get('professor')} — {metadata.get('source')}"
        if source_label not in sources:
            sources.append(source_label)

    return {
        "question": question,
        "answer": answer,
        "sources": sources,
        "retrieved_chunks": retrieved_chunks,
    }


def print_answer(question):
    print("\n" + "=" * 80)
    print(f"QUESTION: {question}")
    print("=" * 80)

    result = ask(question)

    print("\nANSWER:")
    print(result["answer"])

    print("\nSOURCES:")
    for source in result["sources"]:
        print(f"- {source}")

    print("\nRETRIEVED CHUNKS:")
    for i, chunk in enumerate(result["retrieved_chunks"], start=1):
        metadata = chunk["metadata"]
        print(f"\nChunk {i}")
        print(f"Professor: {metadata.get('professor')}")
        print(f"Source: {metadata.get('source')}")
        print(f"Distance: {chunk['distance']:.4f}")
        print(chunk["text"][:500])


def main():
    build_vector_store()

    test_questions = [
        "What do students say about Eric Landahl's lecture style?",
        "Is Kenny Castellanos described as difficult?",
        "What do students say about Kaitlyn Bolyard's feedback and grading?",
        "What dining hall has the best food at DePaul?",
    ]

    for question in test_questions:
        print_answer(question)


if __name__ == "__main__":
    main()