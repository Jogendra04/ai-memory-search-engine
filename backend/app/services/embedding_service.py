import os

from dotenv import load_dotenv
from google import genai


# Load environment variables from .env
load_dotenv()


# Initialize Gemini client
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def create_embedding(text):

    response = client.models.embed_content(
        model="gemini-embedding-2",
        contents=text,
        config={
            "output_dimensionality": 768
        }
    )

    return response.embeddings[0].values