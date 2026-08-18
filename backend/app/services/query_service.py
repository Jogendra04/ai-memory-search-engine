from app.services.chat_history import get_history

def build_search_query(
    question,
    user_id,
    limit=6
):
    """
    Build a search query using recent conversation
    when the current question appears to be a follow-up.
    """

    # Get recent conversation

    history = get_history(
        user_id=user_id,
        limit=limit
    )

    # No previous conversation

    if not history:

        return question

    # Build conversation context

    conversation_parts = []

    for message in history:

        role = message.get(
            "role",
            ""
        )

        content = message.get(
            "content",
            ""
        )

        if content:

            conversation_parts.append(
                f"{role}: {content}"
            )

    # Add current question

    conversation_parts.append(
        f"user: {question}"
    )

    conversation = "\n".join(
        conversation_parts
    )

    # Build semantic search query

    search_query = (
        "Use the following recent conversation "
        "to understand the context of the user's "
        "current question.\n\n"

        "Recent conversation:\n"
        f"{conversation}\n\n"

        "Current question:\n"
        f"{question}"
    )

    # Debug output

    print(
        "\n========== SEARCH QUERY =========="
    )

    print(search_query)

    print(
        "==================================\n"
    )

    return search_query