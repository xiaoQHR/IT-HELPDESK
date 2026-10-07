import json
from collections import defaultdict
from pathlib import Path

from core.hybrid_intent_recognizer import (
    HybridIntentRecognizer,
)


def main() -> None:
    dataset_path = (
        Path(__file__).parent
        / "intent_cases.json"
    )

    cases = json.loads(
        dataset_path.read_text(
            encoding="utf-8"
        )
    )

    recognizer = HybridIntentRecognizer()

    correct = 0

    label_stats: dict[str, dict[str, int]] = (
        defaultdict(
            lambda: {
                "total": 0,
                "correct": 0,
            }
        )
    )

    for case in cases:
        message = case["message"]
        expected = case["expected"]

        result = recognizer.recognize(message)
        predicted = result.intent

        label_stats[expected]["total"] += 1

        is_correct = predicted == expected

        if is_correct:
            correct += 1
            label_stats[expected]["correct"] += 1

        print(
            f"[{'PASS' if is_correct else 'FAIL'}] "
            f"expected={expected}, "
            f"predicted={predicted}, "
            f"pattern={result.pattern_intent}, "
            f"semantic={result.semantic_intent}, "
            f"message={message}"
        )

    total = len(cases)
    accuracy = correct / total if total else 0.0

    print("\nHybrid evaluation summary")
    print(f"Total: {total}")
    print(f"Correct: {correct}")
    print(f"Accuracy: {accuracy:.2%}")

    for label, stats in sorted(
        label_stats.items()
    ):
        label_accuracy = (
            stats["correct"] / stats["total"]
        )

        print(
            f"{label}: "
            f"{stats['correct']}/"
            f"{stats['total']} "
            f"({label_accuracy:.2%})"
        )


if __name__ == "__main__":
    main()