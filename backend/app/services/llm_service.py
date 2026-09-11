import os
import time

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

Your task is to answer the user's question using
the retrieved documents, saved memories, and recent
conversation history.

IMPORTANT ANSWERING RULES:

1. Always answer the user's question directly.

2. Use the retrieved context as the primary source
   of information.

3. When the requested information exists in the
   retrieved context, extract the actual information
   and include it in the answer.

4. Never stop after an introductory sentence.

5. Never end an answer with a colon if more information
   is required.

6. If the user asks for skills, provide the actual
   skills as a complete list.

7. If the user asks for a publication name, provide
   the actual publication title.

8. If the user asks for a name, title, company,
   technology, date, achievement, or other specific
   information, provide the actual value.

9. If the question asks for a list, provide all relevant
   items available in the retrieved context.

10. Do not merely describe what the context contains.
    Extract and answer with the information itself.

11. Do not invent facts.

12. Do not assume information that is not provided.

13. You may combine information from multiple retrieved
    sources when necessary.

14. Use recent conversation history for follow-up
    questions and references such as "it", "that",
    "this", "they", "which one", "tell me more",
    and "what about".

15. Only use information relevant to the current user.

16. If the answer cannot be found in the retrieved
    context or conversation history, respond exactly:

"I couldn't find that information in your documents or memories."

17. Do not mention the retrieval process unless
    the user asks about it.

18. Keep answers concise but complete.

19. Never return an incomplete sentence.

20. Never return an incomplete list.

21. Before finishing, verify that the response directly
    answers the user's question.

22. Return only the final answer.

Examples:

Bad answer:
"Based on your resume, your technical skills include:"

Good answer:
"Your technical skills include Python, JavaScript, SQL,
FastAPI, Flask, React.js, PostgreSQL, Qdrant, PyTorch,
TensorFlow, LangChain, Docker, AWS, and related AI/ML
technologies."

Bad answer:
"The name of your publication is:"

Good answer:
"The name of your research publication is [actual title
from the retrieved context]."
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
FINAL ANSWER
====================

Answer the current question directly using the retrieved
context.

If the requested information exists in the context,
extract and provide the actual information.

Do not provide only an introduction.

Do not end with a colon.

Do not leave the answer incomplete.

Return only the final answer.
"""


    # Generate answer using Gemini
    answer = None

    # Number of Gemini attempts
    max_retries = 4

    for attempt in range(max_retries):

        try:

            print(
                f"Sending request to Gemini "
                f"(attempt {attempt + 1}/{max_retries})..."
            )

            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt,
                config={
                    "temperature": 0,
                    "max_output_tokens": 400
                }
            )

            if response and response.text:

                answer = response.text.strip()

                print(
                    f"Gemini request succeeded "
                    f"on attempt {attempt + 1}/{max_retries}"
                )

                break

            answer = (
                "I couldn't generate an answer "
                "from the available information."
            )

            print(
                "Gemini returned an empty response."
            )

            break


        except Exception as error:

            error_text = str(error)

            print(
                f"Gemini error "
                f"(attempt {attempt + 1}/{max_retries}): "
                f"{error}"
            )


            # Detect temporary Gemini server errors
            is_temporary_error = (
                "500" in error_text
                or "503" in error_text
                or "INTERNAL" in error_text
                or "UNAVAILABLE" in error_text
                or "high demand" in error_text
                or "overloaded" in error_text
                or "temporarily unavailable" in error_text
            )


            # Stop immediately for non-temporary errors
            if not is_temporary_error:

                print(
                    "Non-temporary Gemini error. "
                    "Stopping retries."
                )

                break


            # Final attempt failed
            if attempt == max_retries - 1:

                print(
                    "Gemini remained unavailable "
                    "after all retry attempts."
                )

                break


            # Exponential backoff:
            #
            # Attempt 1 -> wait 2 seconds
            # Attempt 2 -> wait 4 seconds
            # Attempt 3 -> wait 8 seconds
            wait_time = 2 ** (attempt + 1)

            print(
                f"Retrying Gemini request "
                f"in {wait_time} seconds..."
            )

            time.sleep(wait_time)


    # All attempts failed
    if answer is None:

        answer = (
            "The AI service is temporarily unavailable. "
            "Please try again shortly."
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