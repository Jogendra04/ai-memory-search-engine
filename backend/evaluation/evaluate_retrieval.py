import time

from evaluation.evaluation_dataset import evaluation_questions

from app.services.embedding_service import create_embedding
from app.services.qdrant_service import search_embeddings
from app.services.retrieval_service import rerank_results


# ============================================================
# Evaluation Configuration
# ============================================================

USER_ID = "6cf68ab8-82c9-4049-9d9a-ee6b13e4bf61"

# Number of results evaluated
TOP_K = 5

# Retrieve more candidates from Qdrant.
# BGE reranker will choose the final TOP_K from these.
INITIAL_K = 10


# ============================================================
# Get Chunk Number
# ============================================================

def get_chunk_number(result):
    """
    Safely get chunk number from a Qdrant result.
    """

    payload = result.payload or {}

    chunk_number = payload.get("chunk_number")

    if chunk_number is None:
        return None

    try:
        return int(chunk_number)

    except (TypeError, ValueError):
        return chunk_number


# ============================================================
# Check Relevance
# ============================================================

def is_relevant(result, relevant_chunks):
    """
    A result is relevant if its chunk_number exists
    in the ground-truth relevant_chunks list.
    """

    chunk_number = get_chunk_number(result)

    if chunk_number is None:
        return False

    return chunk_number in relevant_chunks


# ============================================================
# Calculate Metrics
# ============================================================

def calculate_metrics(results, relevant_chunks):
    """
    Calculate:

    Precision@K
    Recall@K
    Hit@K
    MRR@K
    """

    relevant_count = 0

    first_relevant_rank = None

    for rank, result in enumerate(
        results,
        start=1
    ):

        if is_relevant(
            result,
            relevant_chunks
        ):

            relevant_count += 1

            if first_relevant_rank is None:

                first_relevant_rank = rank

    retrieved_count = len(results)

    # ========================================================
    # Precision@K
    # ========================================================

    if retrieved_count > 0:

        precision = (
            relevant_count
            / retrieved_count
        )

    else:

        precision = 0.0

    # ========================================================
    # Recall@K
    # ========================================================

    total_relevant = len(
        relevant_chunks
    )

    if total_relevant > 0:

        recall = (
            relevant_count
            / total_relevant
        )

        recall = min(
            recall,
            1.0
        )

    else:

        recall = 0.0

    # ========================================================
    # Hit@K
    # ========================================================

    hit = (
        1
        if relevant_count > 0
        else 0
    )

    # ========================================================
    # MRR@K
    # ========================================================

    if first_relevant_rank is not None:

        mrr = (
            1
            / first_relevant_rank
        )

    else:

        mrr = 0.0

    return {
        "precision": precision,
        "recall": recall,
        "hit": hit,
        "mrr": mrr
    }


# ============================================================
# Get Qdrant Score
# ============================================================

def get_qdrant_score(result):
    """
    Get the original Qdrant semantic similarity score.
    """

    score = getattr(
        result,
        "score",
        None
    )

    if score is None:
        return 0.0

    return float(score)


# ============================================================
# Get BGE Reranker Score
# ============================================================

def get_reranker_score(result):
    """
    Get the BGE reranker score.

    The updated rerank_results() function should attach
    the BGE score to the result as:

        result.reranker_score
    """

    score = getattr(
        result,
        "reranker_score",
        None
    )

    if score is None:
        return None

    return float(score)


# ============================================================
# Print Retrieved Results
# ============================================================

def print_results(
    title,
    results,
    relevant_chunks,
    score_type
):
    """
    Print retrieved chunks and their scores.
    """

    print("\n" + "-" * 60)

    print(title)

    print("-" * 60)

    if not results:

        print("No results.")

        return

    for index, result in enumerate(
        results,
        start=1
    ):

        payload = result.payload or {}

        chunk_number = payload.get(
            "chunk_number",
            "N/A"
        )

        filename = payload.get(
            "filename",
            "N/A"
        )

        relevant = is_relevant(
            result,
            relevant_chunks
        )

        # ====================================================
        # Select Score
        # ====================================================

        if score_type == "qdrant":

            score = get_qdrant_score(
                result
            )

            score_label = "Qdrant"

        else:

            score = get_reranker_score(
                result
            )

            score_label = "BGE"

        # ====================================================
        # Print
        # ====================================================

        print(
            f"\n{index}. "
            f"Relevant={relevant}"
        )

        if score is not None:

            print(
                f"   {score_label} Score: "
                f"{score:.6f}"
            )

        else:

            print(
                f"   {score_label} Score: N/A"
            )

        print(
            f"   File: {filename}"
        )

        print(
            f"   Chunk: {chunk_number}"
        )


# ============================================================
# Evaluate One Question
# ============================================================

def evaluate_question(question_data):

    question = question_data[
        "question"
    ]

    relevant_chunks = question_data[
        "relevant_chunks"
    ]

    print("\n")

    print("=" * 60)

    print(
        f"QUESTION: {question}"
    )

    print("=" * 60)

    print(
        f"Expected relevant chunks: "
        f"{relevant_chunks}"
    )

    # ========================================================
    # Create Query Embedding
    # ========================================================

    start = time.perf_counter()

    query_embedding = create_embedding(
        question
    )

    embedding_time = (
        time.perf_counter()
        - start
    )

    # ========================================================
    # Qdrant Retrieval
    # ========================================================

    start = time.perf_counter()

    retrieved_results = search_embeddings(
        query_embedding=query_embedding,
        user_id=USER_ID,
        limit=INITIAL_K
    )

    qdrant_time = (
        time.perf_counter()
        - start
    )

    # ========================================================
    # BEFORE RERANKING
    # ========================================================

    # Keep only TOP_K Qdrant results.
    #
    # This represents the retrieval system BEFORE BGE
    # reranking.

    before_results = list(
        retrieved_results[:TOP_K]
    )

    # ========================================================
    # Calculate BEFORE Metrics
    # ========================================================

    before_metrics = calculate_metrics(
        before_results,
        relevant_chunks
    )

    # ========================================================
    # Print BEFORE Results
    # ========================================================

    print_results(
        title="BEFORE RERANKING - QDRANT",
        results=before_results,
        relevant_chunks=relevant_chunks,
        score_type="qdrant"
    )

    # ========================================================
    # BGE RERANKING
    # ========================================================

    start = time.perf_counter()

    after_results = rerank_results(
        results=retrieved_results,
        question=question,
        max_results=TOP_K
    )

    reranking_time = (
        time.perf_counter()
        - start
    )

    # ========================================================
    # Calculate AFTER Metrics
    # ========================================================

    after_metrics = calculate_metrics(
        after_results,
        relevant_chunks
    )

    # ========================================================
    # Print AFTER Results
    # ========================================================

    print_results(
        title="AFTER RERANKING - BGE",
        results=after_results,
        relevant_chunks=relevant_chunks,
        score_type="bge"
    )

    # ========================================================
    # Metric Comparison
    # ========================================================

    print("\n" + "-" * 60)

    print("BEFORE VS AFTER")

    print("-" * 60)

    print(
        f"Precision@{TOP_K}: "
        f"{before_metrics['precision'] * 100:.2f}%"
        f" -> "
        f"{after_metrics['precision'] * 100:.2f}%"
    )

    print(
        f"Recall@{TOP_K}: "
        f"{before_metrics['recall'] * 100:.2f}%"
        f" -> "
        f"{after_metrics['recall'] * 100:.2f}%"
    )

    print(
        f"Hit@{TOP_K}: "
        f"{before_metrics['hit']}"
        f" -> "
        f"{after_metrics['hit']}"
    )

    print(
        f"MRR@{TOP_K}: "
        f"{before_metrics['mrr']:.4f}"
        f" -> "
        f"{after_metrics['mrr']:.4f}"
    )

    # ========================================================
    # Metric Improvements
    # ========================================================

    precision_delta = (
        after_metrics["precision"]
        - before_metrics["precision"]
    )

    recall_delta = (
        after_metrics["recall"]
        - before_metrics["recall"]
    )

    hit_delta = (
        after_metrics["hit"]
        - before_metrics["hit"]
    )

    mrr_delta = (
        after_metrics["mrr"]
        - before_metrics["mrr"]
    )

    print("\nMetric improvement:")

    print(
        f"Precision@{TOP_K}: "
        f"{precision_delta * 100:+.2f} percentage points"
    )

    print(
        f"Recall@{TOP_K}: "
        f"{recall_delta * 100:+.2f} percentage points"
    )

    print(
        f"Hit@{TOP_K}: "
        f"{hit_delta:+d}"
    )

    print(
        f"MRR@{TOP_K}: "
        f"{mrr_delta:+.4f}"
    )

    # ========================================================
    # Timing
    # ========================================================

    print("\nTiming:")

    print(
        f"Embedding: "
        f"{embedding_time:.2f}s"
    )

    print(
        f"Qdrant: "
        f"{qdrant_time:.2f}s"
    )

    print(
        f"BGE Reranking: "
        f"{reranking_time:.2f}s"
    )

    # ========================================================
    # Return Results
    # ========================================================

    return {

        # ----------------------------------------------------
        # BEFORE
        # ----------------------------------------------------

        "before_precision":
            before_metrics["precision"],

        "before_recall":
            before_metrics["recall"],

        "before_hit":
            before_metrics["hit"],

        "before_mrr":
            before_metrics["mrr"],

        # ----------------------------------------------------
        # AFTER
        # ----------------------------------------------------

        "after_precision":
            after_metrics["precision"],

        "after_recall":
            after_metrics["recall"],

        "after_hit":
            after_metrics["hit"],

        "after_mrr":
            after_metrics["mrr"],

        # ----------------------------------------------------
        # Timing
        # ----------------------------------------------------

        "embedding_time":
            embedding_time,

        "qdrant_time":
            qdrant_time,

        "reranking_time":
            reranking_time
    }


# ============================================================
# Main Evaluation
# ============================================================

def main():

    print("\n")

    print("=" * 60)

    print("RAG RETRIEVAL EVALUATION")

    print("=" * 60)

    print(
        f"Initial Qdrant retrieval: "
        f"Top-{INITIAL_K}"
    )

    print(
        f"Final evaluation: "
        f"Top-{TOP_K}"
    )

    print(
        "Reranker: "
        "BAAI/bge-reranker-base"
    )

    # ========================================================
    # Store Results
    # ========================================================

    results = []

    # ========================================================
    # Evaluate Questions
    # ========================================================

    for question_data in evaluation_questions:

        result = evaluate_question(
            question_data
        )

        results.append(
            result
        )

    # ========================================================
    # Empty Dataset
    # ========================================================

    total_questions = len(
        results
    )

    if total_questions == 0:

        print(
            "\nNo evaluation questions found."
        )

        return

    # ========================================================
    # BEFORE AVERAGES
    # ========================================================

    average_before_precision = (
        sum(
            result["before_precision"]
            for result in results
        )
        / total_questions
    )

    average_before_recall = (
        sum(
            result["before_recall"]
            for result in results
        )
        / total_questions
    )

    average_before_hit = (
        sum(
            result["before_hit"]
            for result in results
        )
        / total_questions
    )

    average_before_mrr = (
        sum(
            result["before_mrr"]
            for result in results
        )
        / total_questions
    )

    # ========================================================
    # AFTER AVERAGES
    # ========================================================

    average_after_precision = (
        sum(
            result["after_precision"]
            for result in results
        )
        / total_questions
    )

    average_after_recall = (
        sum(
            result["after_recall"]
            for result in results
        )
        / total_questions
    )

    average_after_hit = (
        sum(
            result["after_hit"]
            for result in results
        )
        / total_questions
    )

    average_after_mrr = (
        sum(
            result["after_mrr"]
            for result in results
        )
        / total_questions
    )

    # ========================================================
    # Timing Averages
    # ========================================================

    average_embedding = (
        sum(
            result["embedding_time"]
            for result in results
        )
        / total_questions
    )

    average_qdrant = (
        sum(
            result["qdrant_time"]
            for result in results
        )
        / total_questions
    )

    average_reranking = (
        sum(
            result["reranking_time"]
            for result in results
        )
        / total_questions
    )

    # ========================================================
    # Improvements
    # ========================================================

    precision_improvement = (
        average_after_precision
        - average_before_precision
    )

    recall_improvement = (
        average_after_recall
        - average_before_recall
    )

    hit_improvement = (
        average_after_hit
        - average_before_hit
    )

    mrr_improvement = (
        average_after_mrr
        - average_before_mrr
    )

    # ========================================================
    # Final Report
    # ========================================================

    print("\n")

    print("=" * 60)

    print("FINAL RAG EVALUATION")

    print("=" * 60)

    print(
        f"Questions evaluated: "
        f"{total_questions}"
    )

    print()

    print(
        f"Reranker: "
        f"BAAI/bge-reranker-base"
    )

    print()

    # ========================================================
    # BEFORE
    # ========================================================

    print(
        "BEFORE RERANKING "
        "(Qdrant)"
    )

    print(
        f"Precision@{TOP_K}: "
        f"{average_before_precision * 100:.2f}%"
    )

    print(
        f"Recall@{TOP_K}: "
        f"{average_before_recall * 100:.2f}%"
    )

    print(
        f"Hit Rate@{TOP_K}: "
        f"{average_before_hit * 100:.2f}%"
    )

    print(
        f"MRR@{TOP_K}: "
        f"{average_before_mrr:.4f}"
    )

    print()

    # AFTER

    print(
        "AFTER RERANKING "
        "(BGE)"
    )

    print(
        f"Precision@{TOP_K}: "
        f"{average_after_precision * 100:.2f}%"
    )

    print(
        f"Recall@{TOP_K}: "
        f"{average_after_recall * 100:.2f}%"
    )

    print(
        f"Hit Rate@{TOP_K}: "
        f"{average_after_hit * 100:.2f}%"
    )

    print(
        f"MRR@{TOP_K}: "
        f"{average_after_mrr:.4f}"
    )

    print()

    # IMPROVEMENT

    print(
        "RERANKING IMPROVEMENT"
    )

    print(
        f"Precision@{TOP_K}: "
        f"{precision_improvement * 100:+.2f} percentage points"
    )

    print(
        f"Recall@{TOP_K}: "
        f"{recall_improvement * 100:+.2f} percentage points"
    )

    print(
        f"Hit Rate@{TOP_K}: "
        f"{hit_improvement * 100:+.2f} percentage points"
    )

    print(
        f"MRR@{TOP_K}: "
        f"{mrr_improvement:+.4f}"
    )

    print()

    # Timing

    print(
        "AVERAGE LATENCY"
    )

    print(
        f"Embedding: "
        f"{average_embedding:.2f}s"
    )

    print(
        f"Qdrant Search: "
        f"{average_qdrant:.2f}s"
    )

    print(
        f"BGE Reranking: "
        f"{average_reranking:.2f}s"
    )

    print(
        f"Total Retrieval Pipeline: "
        f"{(
            average_embedding
            + average_qdrant
            + average_reranking
        ):.2f}s"
    )

    print()

    # Final Interpretation

    print(
        "INTERPRETATION"
    )

    if precision_improvement > 0:

        print(
            "✓ BGE reranking improved Precision@5."
        )

    elif precision_improvement < 0:

        print(
            "✗ BGE reranking reduced Precision@5."
        )

    else:

        print(
            "→ BGE reranking produced no Precision@5 change."
        )

    if mrr_improvement > 0:

        print(
            "✓ BGE reranking improved MRR@5."
        )

    elif mrr_improvement < 0:

        print(
            "✗ BGE reranking reduced MRR@5."
        )

    else:

        print(
            "→ BGE reranking produced no MRR@5 change."
        )

    print("=" * 60)


# Run Evaluation

if __name__ == "__main__":

    main()