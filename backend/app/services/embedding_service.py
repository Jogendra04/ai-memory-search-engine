from google import genai

client = genai.Client()


def create_embedding(text):
    response = client.models.embed_content(
        model="gemini-embedding-2",
        contents=text,
        config={
            "output_dimensionality": 768
        }
    )

    return response.embeddings[0].values