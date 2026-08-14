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
        limit=6
    )

    # ==========================================
    # System message
    # ==========================================

    messages = [
        {
            "role": "system",
            "content": f"""
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
        }
    ]

    # ==========================================
    # Add previous conversation
    # ==========================================

    for message in history:

        messages.append(
            {
                "role": message["role"],
                "content": message["content"]
            }
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
    messages=messages,
    options={
        "temperature": 0,
        "num_predict": 150
    },
    keep_alive="30m"
)

        answer = response["message"]["content"].strip()

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