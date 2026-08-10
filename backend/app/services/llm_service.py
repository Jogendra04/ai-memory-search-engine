from ollama import chat

from app.services.chat_history import (
    add_message,
    get_history
)


def generate_answer(
    question,
    context,
    user_id
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

    messages.extend(history)

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

    response = chat(
        model="llama3.2",
        messages=messages
    )

    answer = response["message"]["content"]

    # ==========================================
    # Save conversation for THIS user only
    # ==========================================

    add_message(
        user_id,
        "user",
        question
    )

    add_message(
        user_id,
        "assistant",
        answer
    )

    return answer