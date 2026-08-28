import os

from dotenv import load_dotenv
from google import genai

from app.services.chat_history import (
    add_message,
    get_history
)


# Load environment variables from .env
load_dotenv()


# Initialize Gemini client
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def generate_answer(question, context, user_id, sources=None):

    # Get conversation history for this user
    history = get_history(
        user_id=user_id,
        limit=6
    )

    # System prompt
    system_prompt = f"""
You are a helpful AI assistant for a user's personal knowledge system.

Use the provided context and recent conversation history to answer the user's question.

Rules:

1. Answer using the provided context and conversation history.
2. Use conversation history to understand follow-up questions.
3. Resolve references such as:
   - it
   - that
   - this
   - they
   - which one
   - what was its
   - tell me more
   - what about
4. Do not invent information.
5. Do not use information belonging to another user.
6. If the answer cannot be found in the context or conversation history, say:

"I couldn't find that information in your documents or memories."

Keep the answer concise and directly answer the question.

Context:
{context}
"""

    # Build conversation for Gemini
    conversation = [
        system_prompt
    ]

    # Add previous conversation
    for message in history:

        conversation.append(
            f"{message['role']}: {message['content']}"
        )

    # Add current question
    conversation.append(
        f"user: {question}"
    )

    # Combine conversation into one prompt
    prompt = "\n\n".join(conversation)

    # Generate answer using Gemini
    try:

        response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents=prompt,
    config={
        "temperature": 0,
        "max_output_tokens": 150
    }
)

        answer = response.text.strip()

    except Exception as error:

        print(
            f"Gemini error: {error}"
        )

        return (
            "The AI service is currently unavailable. "
            "Please try again later."
        )

    # Save user's question
    add_message(
        user_id=user_id,
        role="user",
        content=question,
        sources=[]
    )

    # Save AI answer + sources
    add_message(
        user_id=user_id,
        role="assistant",
        content=answer,
        sources=sources or []
    )

    return answer