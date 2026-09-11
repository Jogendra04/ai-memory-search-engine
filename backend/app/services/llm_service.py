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

    # --------------------------------------------------
    # Get recent conversation history
    # --------------------------------------------------

    history = get_history(
        user_id=user_id,
        limit=6
    )


    # --------------------------------------------------
    # Build conversation history
    # Ignore incomplete previous assistant answers
    # --------------------------------------------------

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
            ).strip()

            if not content:
                continue

            # Skip incomplete assistant responses
            if role == "assistant":

                incomplete_response = (
                    len(content) < 40
                    or content.endswith(":")
                    or content.endswith("-")
                    or content.endswith("**")
                    or content.endswith(",")
                )

                if incomplete_response:
                    continue

            history_parts.append(
                f"{role}: {content}"
            )

        if history_parts:
            history_text = "\n".join(
                history_parts
            )

        else:
            history_text = (
                "No previous conversation."
            )

    else:

        history_text = (
            "No previous conversation."
        )


    # --------------------------------------------------
    # Make sure context is not empty
    # --------------------------------------------------

    if not context or not context.strip():

        context = (
            "No relevant documents or "
            "saved memories were found."
        )


    # --------------------------------------------------
    # System instructions
    # --------------------------------------------------

    system_prompt = """
You are an AI assistant for a user's personal knowledge system.

Your task is to answer the user's question using the retrieved
documents, saved memories, and recent conversation history.

IMPORTANT RULES:

1. Answer the current question directly.

2. Use the retrieved context as the primary source of information.

3. Extract actual information from the context.

4. Do not merely describe what the context contains.

5. If the user asks for a list, provide all relevant items found
   in the retrieved context.

6. If the user asks about skills, provide the actual skills as a
   complete list.

7. If the user asks about projects, provide the actual project
   names and relevant details found in the context.

8. If the user asks for a publication name, provide the actual
   publication title found in the context.

9. If the user asks for a name, title, company, technology, date,
   achievement, or other specific information, provide the actual
   value from the context.

10. Never invent facts.

11. Never assume information that is not provided.

12. You may combine information from multiple retrieved sources.

13. Use recent conversation history only when it helps answer the
    current question.

14. Ignore incomplete previous assistant responses.

15. Only use information relevant to the current user.

16. If the answer cannot be found in the retrieved context or
    conversation history, respond exactly:

"I couldn't find that information in your documents or memories."

17. Do not mention retrieval, embeddings, Qdrant, prompts, or
    internal processing unless the user asks.

18. Keep answers concise but complete.

19. Never stop after an introductory sentence.

20. Never end with a colon.

21. Never return an incomplete sentence.

22. Never return an incomplete list.

23. Before finishing, verify that the answer directly answers the
    user's question.

24. Return only the final answer.
"""


    # --------------------------------------------------
    # Build final prompt
    # --------------------------------------------------

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

Answer the current question directly.

Use the retrieved context to provide the actual information.

If the question asks for multiple items, include all relevant items.

Do not provide only an introduction.

Do not end with a colon.

Do not leave the answer incomplete.

Return only the final answer.
"""


    # --------------------------------------------------
    # Generate answer using Gemini
    # --------------------------------------------------

    answer = None

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

                generated_answer = response.text.strip()


                # --------------------------------------------------
                # Validate generated answer
                # --------------------------------------------------

                incomplete_answer = (
                    not generated_answer
                    or len(generated_answer) < 20
                    or generated_answer.endswith(":")
                    or generated_answer.endswith("-")
                    or generated_answer.endswith("**")
                    or generated_answer.endswith(",")
                )


                if incomplete_answer:

                    print(
                        "Gemini returned an incomplete answer."
                    )

                    answer = (
                        "I couldn't generate a complete answer "
                        "from the available information. "
                        "Please try asking the question again."
                    )

                else:

                    answer = generated_answer

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


            # Temporary Gemini server errors
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


            # Exponential backoff
            wait_time = 2 ** (attempt + 1)

            print(
                f"Retrying Gemini request "
                f"in {wait_time} seconds..."
            )

            time.sleep(wait_time)


    # --------------------------------------------------
    # All attempts failed
    # --------------------------------------------------

    if answer is None:

        answer = (
            "The AI service is temporarily unavailable. "
            "Please try again shortly."
        )


    # --------------------------------------------------
    # Save user's question
    # --------------------------------------------------

    add_message(
        user_id=user_id,
        role="user",
        content=question,
        sources=[]
    )


    # --------------------------------------------------
    # Save AI answer and sources
    # --------------------------------------------------

    add_message(
        user_id=user_id,
        role="assistant",
        content=answer,
        sources=sources or []
    )


    return answer