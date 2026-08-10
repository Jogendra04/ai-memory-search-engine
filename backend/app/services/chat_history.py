# Store chat history separately for each user
chat_history = {}


def add_message(user_id, role, content):
    """
    Save a chat message for a specific user.
    """

    if user_id not in chat_history:
        chat_history[user_id] = []

    chat_history[user_id].append(
        {
            "role": role,
            "content": content
        }
    )


def get_history(user_id, limit=10):
    """
    Return the last N messages for a specific user.
    """

    if user_id not in chat_history:
        return []

    return chat_history[user_id][-limit:]


def clear_history(user_id):
    """
    Remove chat history for a specific user.
    """

    if user_id in chat_history:
        chat_history[user_id].clear()