from ollama import chat

from app.services.chat_history import (
    add_message,
    get_history
)


def generate_answer(question, context):

    # Get previous conversation
    history = get_history()

    messages = [
        {
            "role": "system",
            "content": f"""
You are a helpful AI assistant.

Answer the user's question ONLY using the provided context.

If the answer is not in the context, say:
"I couldn't find that information in the uploaded documents."

Context:
{context}
"""
        }
    ]

    # Previous conversation
    messages.extend(history)

    # Current question
    messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    response = chat(
        model="llama3.2",
        messages=messages
    )

    answer = response["message"]["content"]

    # Save current conversation
    add_message("user", question)
    add_message("assistant", answer)

    return answers