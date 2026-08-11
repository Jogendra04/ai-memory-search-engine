def rerank_results(
    results,
    question,
    max_results=5
):
    """
    Re-rank retrieved Qdrant results using
    semantic similarity plus simple lexical
    relevance signals.

    Qdrant's score remains the primary signal.
    """

    question_words = set(
        question.lower().split()
    )

    scored_results = []

    for result in results:

        payload = result.payload or {}

        # --------------------------------------
        # Qdrant semantic score
        # --------------------------------------

        qdrant_score = result.score or 0.0

        # --------------------------------------
        # Build searchable source text
        # --------------------------------------

        if payload.get("type") == "memory":

            source_text = " ".join(
                [
                    str(payload.get("title", "")),
                    str(payload.get("content", "")),
                    " ".join(
                        payload.get("tags", [])
                    )
                ]
            )

        else:

            source_text = " ".join(
                [
                    str(payload.get("filename", "")),
                    str(payload.get("text", ""))
                ]
            )

        source_words = set(
            source_text.lower().split()
        )

        # --------------------------------------
        # Keyword overlap
        # --------------------------------------

        if question_words:

            overlap = (
                len(
                    question_words
                    & source_words
                )
                / len(question_words)
            )

        else:

            overlap = 0.0

        # --------------------------------------
        # Final score
        # --------------------------------------

        final_score = (
            (qdrant_score * 0.80)
            + (overlap * 0.20)
        )

        scored_results.append(
            (
                final_score,
                result
            )
        )

    # --------------------------------------
    # Sort by final score
    # --------------------------------------

    scored_results.sort(
        key=lambda item: item[0],
        reverse=True
    )

    return [
        result
        for _, result in scored_results[:max_results]
    ]