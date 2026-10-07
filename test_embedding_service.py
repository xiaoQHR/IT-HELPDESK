import math

from core.embedding_service import EmbeddingService


def vector_length(vector: list[float]) -> float:
    """计算向量的欧几里得长度。"""

    return math.sqrt(
        sum(value * value for value in vector)
    )


def main() -> None:
    service = EmbeddingService()

    print(
        "Model loaded before encode:",
        service._model is not None,
    )

    first_embeddings = service.encode(
        [
            "退款需要多久到账？",
            "退款什么时候能收到？",
        ]
    )

    first_model_id = id(service._model)

    second_embedding = service.encode_one(
        "应用登录时提示 401 错误。"
    )

    second_model_id = id(service._model)

    print(
        "Model loaded after encode:",
        service._model is not None,
    )
    print(
        "Model reused:",
        first_model_id == second_model_id,
    )
    print(
        "Document count:",
        len(first_embeddings),
    )
    print(
        "Vector dimension:",
        len(first_embeddings[0]),
    )
    print(
        "Single vector dimension:",
        len(second_embedding),
    )
    print(
        "Normalized vector length:",
        round(vector_length(first_embeddings[0]), 4),
    )


if __name__ == "__main__":
    main()