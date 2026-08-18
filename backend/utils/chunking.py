import re


def chunk_text(
    text,
    chunk_size=500,
    overlap=100
):
    """
    Split text into overlapping chunks while
    trying to preserve sentence and word boundaries.
    """

    if not text:
        return []

    # Normalize excessive whitespace
    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    if not text:
        return []

    chunks = []

    start = 0

    while start < len(text):

        # Initial chunk boundary

        end = min(
            start + chunk_size,
            len(text)
        )

        # Try to end at a natural boundary

        if end < len(text):

            boundary_candidates = [
                text.rfind(". ", start, end),
                text.rfind("? ", start, end),
                text.rfind("! ", start, end),
                text.rfind(", ", start, end),
                text.rfind(" ", start, end),
            ]

            valid_boundaries = [
                position
                for position in boundary_candidates
                if position > start
            ]

            if valid_boundaries:

                boundary = max(
                    valid_boundaries
                )

                end = boundary + 1

        # Create chunk

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        # Stop at the end

        if end >= len(text):
            break

        # Calculate overlapping start

        start = max(
            end - overlap,
            start + 1
        )

    return chunks