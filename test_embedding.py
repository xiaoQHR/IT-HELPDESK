from sentence_transformers import SentenceTransformer


MODEL_NAME = (
    "sentence-transformers/"
    "paraphrase-multilingual-MiniLM-L12-v2"
)


def main() -> None:
    model = SentenceTransformer(MODEL_NAME)

    texts = [
        "退款需要多久到账？",
        "退款什么时候能收到？",
        "应用登录时提示 401 错误。",
    ]

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    refund_similarity = float(
        embeddings[0] @ embeddings[1]
    )

    technical_similarity = float(
        embeddings[0] @ embeddings[2]
    )

    print("Embedding shape:", embeddings.shape)
    print(
        "Refund similarity:",
        round(refund_similarity, 4),
    )
    print(
        "Refund vs technical similarity:",
        round(technical_similarity, 4),
    )


if __name__ == "__main__":
    main()