from ollama import embed


def create_embedding(text):
    response = embed(
        model="nomic-embed-text",
        input=text
    )

    return response["embeddings"][0]