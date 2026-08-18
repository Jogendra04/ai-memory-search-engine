def rerank_results(
    results,
    question,
    max_results=5
):
    """
    Re-rank retrieved Qdrant results using
    semantic similarity plus keyword relevance.
    """

    question_words = set(
        question.lower()
        .replace("?", "")
        .replace(",", "")
        .split()
    )

    stop_words = {
        "what",
        "is",
        "are",
        "the",
        "a",
        "an",
        "do",
        "does",
        "did",
        "i",
        "me",
        "my",
        "you",
        "your",
        "about",
        "of",
        "in",
        "to",
        "and",
        "for",
        "on"
    }

    question_keywords = (
        question_words - stop_words
    )

    scored_results = []

    for result in results:

        payload = result.payload or {}

        qdrant_score = (
            result.score or 0.0
        )

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
            source_text.lower()
            .replace(",", " ")
            .replace(".", " ")
            .replace(":", " ")
            .replace(";", " ")
            .replace("-", " ")
            .replace("/", " ")
            .split()
        )

        if question_keywords:

            matched_keywords = (
                question_keywords
                & source_words
            )

            keyword_overlap = (
                len(matched_keywords)
                / len(question_keywords)
            )

        else:

            keyword_overlap = 0.0

        final_score = (
            (qdrant_score * 0.75)
            + (keyword_overlap * 0.25)
        )

        scored_results.append(
            (
                final_score,
                result
            )
        )

    scored_results.sort(
        key=lambda item: item[0],
        reverse=True
    )

    return [
        result
        for _, result
        in scored_results[:max_results]
    ]