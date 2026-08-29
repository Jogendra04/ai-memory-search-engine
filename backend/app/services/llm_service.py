import os

from dotenv import load_dotenv
from google import genai

from app.services.chat_history import (
    add_message,
    get_history
)


# Load environment variables
load_dotenv()


# Initialize Gemini client
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is not configured."
    )

client = genai.Client(
    api_key=GEMINI_API_KEY
)


def generate_answer(
    question,
    context,
    user_id,
    sources=None
):

    # Get recent conversation history
    history = get_history(
        user_id=user_id,
        limit=6
    )

    # Build conversation history
    history_text = ""

    if history:

        history_parts = []

        for message in history:

            role = message.get(
                "role",
                "user"
            )

            content = message.get(
                "content",
                ""
            )

            history_parts.append(
                f"{role}: {content}"
            )

        history_text = "\n".join(
            history_parts
        )

    else:

        history_text = (
            "No previous conversation."
        )


    # Make sure context is not empty
    if not context.strip():

        context = (
            "No relevant documents or "
            "saved memories were found."
        )


    # System instructions
    system_prompt = """
You are an AI assistant for a user's personal
knowledge system.

Your job is to answer the user's question using
the retrieved documents, saved memories, and
recent conversation history.

IMPORTANT RULES:

1. Use the retrieved context as the primary source
   for your answer.

2. Answer the user's question directly.

3. If the answer is explicitly present in a saved
   memory, use that information.

4. If the answer is present in an uploaded document,
   use the relevant document information.

5. You may combine information from multiple
   retrieved sources when necessary.

6. Do not invent facts that are not supported by
   the retrieved context or conversation history.

7. Do not assume information that is not provided.

8. For follow-up questions, use the conversation
   history to understand references such as:
   "it", "that", "this", "they", "which one",
   "what was its", "tell me more", and "what about".

9. The retrieved context may contain information
   from different sources. Only use information
   relevant to the current user.

10. If the answer cannot be found in the retrieved
    context or conversation history, respond exactly:

"I couldn't find that information in your documents or memories."

11. Do not mention the retrieval process unless
    the user asks about it.

12. Keep the answer concise but complete.

13. Never return an incomplete sentence.

14. Always provide the actual answer when the
    retrieved context contains the information.
"""


    # Build final prompt
    prompt = f"""
{system_prompt}

====================
RETRIEVED CONTEXT
====================

{context}

====================
RECENT CONVERSATION
====================

{history_text}

====================
CURRENT QUESTION
====================

{question}

====================
ANSWER
====================

Provide the complete answer to the current question.
"""


    # Generate answer using Gemini
    try:

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
            config={
                "temperature": 0,
                "max_output_tokens": 250
            }
        )

        if not response or not response.text:

            answer = (
                "I couldn't generate an answer "
                "from the available information."
            )

        else:

            answer = response.text.strip()


    except Exception as error:

        print(
            f"Gemini error: {error}"
        )

        answer = (
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


    # Save AI answer and sources
    add_message(
        user_id=user_id,
        role="assistant",
        content=answer,
        sources=sources or []
    )


    return answer