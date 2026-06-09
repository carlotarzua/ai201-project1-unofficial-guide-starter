import gradio as gr

from query import ask
from retrieve import build_vector_store


def handle_query(question):
    if not question.strip():
        return "Please enter a question.", "", ""

    result = ask(question)

    answer = result["answer"]

    sources = "\n".join(f"- {source}" for source in result["sources"])

    retrieved_chunks = []
    for i, chunk in enumerate(result["retrieved_chunks"], start=1):
        metadata = chunk["metadata"]
        retrieved_chunks.append(
            f"Chunk {i}\n"
            f"Professor: {metadata.get('professor')}\n"
            f"Source: {metadata.get('source')}\n"
            f"Distance: {chunk['distance']:.4f}\n"
            f"{chunk['text'][:700]}"
        )

    retrieved_text = "\n\n" + ("-" * 80 + "\n\n").join(retrieved_chunks)

    return answer, sources, retrieved_text


def main():
    build_vector_store()

    with gr.Blocks(title="The Unofficial Guide to DePaul Professors") as demo:
        gr.Markdown("# The Unofficial Guide to DePaul Professors")
        gr.Markdown(
            "Ask a question about DePaul professors using the collected "
            "Rate My Professors review documents."
        )

        question = gr.Textbox(
            label="Your question",
            placeholder="Example: What do students say about Kaitlyn Bolyard's feedback?",
            lines=2,
        )

        ask_button = gr.Button("Ask")

        answer = gr.Textbox(label="Answer", lines=8)
        sources = gr.Textbox(label="Sources", lines=4)
        retrieved = gr.Textbox(label="Retrieved chunks", lines=14)

        ask_button.click(
            handle_query,
            inputs=question,
            outputs=[answer, sources, retrieved],
        )

        question.submit(
            handle_query,
            inputs=question,
            outputs=[answer, sources, retrieved],
        )

    demo.launch()


if __name__ == "__main__":
    main()