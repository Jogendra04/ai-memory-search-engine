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

    history = get_history(
        user_id=user_id,
        limit=limit
    )

    if not history:
        return question

    # Combine recent conversation with the current question.
    conversation_parts = []

    for message in history:
        role = message.get("role", "")
        content = message.get("content", "")

        if content:
            conversation_parts.append(
                f"{role}: {content}"
            )

    conversation_parts.append(
        f"user: {question}"
    )

    conversation = "\n".join(
        conversation_parts
    )

    # Keep the current question as the main search query.
    # Recent conversation provides additional semantic context.
    search_query = (
        f"Recent conversation:\n"
        f"{conversation}\n\n"
        f"Current question:\n"
        f"{question}"
    )

    print(
        "\n========== SEARCH QUERY =========="
    )

    print(search_query)

    print(
        "==================================\n"
    )

    return search_query