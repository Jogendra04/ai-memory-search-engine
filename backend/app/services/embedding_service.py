import os

from dotenv import load_dotenv
from google import genai


# Load environment variables
load_dotenv()


# Get Gemini API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is not configured."
    )


# Initialize Gemini client
client = genai.Client(
    api_key=GEMINI_API_KEY
)


def create_embedding(text):

    response = client.models.embed_content(
        model="gemini-embedding-2",
        contents=text,
        config={
            "output_dimensionality": 768
        }
    )

    if response and response.embeddings:
        return response.embeddings[0].values

    return None