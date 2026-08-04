chat_history = []


def add_message(role, content):
    """
    Save a chat message.
    """

    chat_history.append(
        {
            "role": role,
            "content": content
        }
    )


def get_history(limit=10):
    """
    Return the last N messages.
    """

    return chat_history[-limit:]


def clear_history():
    """
    Remove all chat history.
    """

    chat_history.clear()