from ollama import chat

from app.services.chat_history import (
    add_message,
    get_history
)


def generate_answer(question, context):

    # Get previous conversation
    history = get_history()

    # If no relevant context was retrieved
    if not context or not context.strip():

        answer = (
            "I couldn't find that information in the uploaded documents."
        )

        add_message("user", question)
        add_message("assistant", answer)

        return answer

    # ==========================================
    # System instruction
    # ==========================================

    system_prompt = f"""
You are an AI assistant for a personal document and memory search engine.

Your task is to answer the user's question using ONLY the information
contained in the retrieved context below.

IMPORTANT RULES:

1. Use the retrieved context as your primary source of information.
2. Do not invent or assume information that is not present in the context.
3. If the answer can be found in the context, answer it clearly and directly.
4. If the answer cannot be found in the context, say:
   "I couldn't find that information in the uploaded documents."
5. You may combine information from multiple retrieved chunks.
6. Keep the answer concise but informative.

================ RETRIEVED CONTEXT ================

{context}

================ END CONTEXT ================
"""

    messages = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]

    # ==========================================
    # Previous conversation
    # ==========================================

    messages.extend(history)

    # ==========================================
    # Current question
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
    # Save conversation
    # ==========================================

    add_message(
        "user",
        question
    )

    add_message(
        "assistant",
        answer
    )

    return answer