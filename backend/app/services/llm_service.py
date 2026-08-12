from ollama import chat

from app.services.chat_history import (
    add_message,
    get_history
)


def generate_answer(
    question,
    context,
    user_id,
    sources=None
):

    # ==========================================
    # Get conversation history for this user
    # ==========================================

    history = get_history(
        user_id=user_id,
        limit=10
    )

    # ==========================================
    # System message
    # ==========================================

    messages = [
        {
            "role": "system",
            "content": f"""
You are a helpful AI assistant for a user's personal knowledge system.

The provided context can contain:

1. Uploaded documents
2. Saved personal memories

Answer the user's question ONLY using the provided context
and the user's conversation history.

Do not use information from another user's data.

If the answer cannot be found in the provided context,
say:

"I couldn't find that information in your documents or memories."

Context:
{context}
"""
        }
    ]

    # ==========================================
    # Add this user's previous conversation
    # ==========================================

    for message in history:

        messages.append(
            {
                "role": message["role"],
                "content": message["content"]
            }
        )

    print(
        "\n========== PREVIOUS HISTORY =========="
    )

    for message in history:

        print(
            f"{message['role']}: "
            f"{message['content']}"
        )

    print(
        "======================================\n"
    )

    # ==========================================
    # Add current question
    # ==========================================

    messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    # ==========================================
    # Generate answer using Llama
    # ==========================================

    try:

        response = chat(
            model="llama3.2",
            messages=messages
        )

        answer = response["message"]["content"]

    except Exception as error:

        print(
            f"Ollama error: {error}"
        )

        return (
            "The AI service is currently unavailable. "
            "Please make sure Ollama is running and "
            "the Llama model is available."
        )

    # ==========================================
    # Save user's question
    # ==========================================

    add_message(
        user_id=user_id,
        role="user",
        content=question,
        sources=[]
    )

    # ==========================================
    # Save AI answer + sources
    # ==========================================

    add_message(
        user_id=user_id,
        role="assistant",
        content=answer,
        sources=sources or []
    )

    return answer