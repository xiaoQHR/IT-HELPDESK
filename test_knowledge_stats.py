from mcp.knowledge_base import KnowledgeBase


def main() -> None:
    knowledge_base = KnowledgeBase()

    document_count = knowledge_base.count_documents()
    chunk_count = knowledge_base.count_chunks()
    stats = knowledge_base.get_stats()

    print("Document count:", document_count)
    print("Chunk count:", chunk_count)
    print("Stats:", stats)

    if chunk_count < document_count:
        raise AssertionError(
            "切片数量不应该小于原始文档数量"
        )


if __name__ == "__main__":
    main()