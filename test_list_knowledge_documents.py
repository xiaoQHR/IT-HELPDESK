from mcp.knowledge_base import KnowledgeBase


def main() -> None:
    knowledge_base = KnowledgeBase()

    documents = knowledge_base.list_documents()

    print("Document count:", len(documents))

    for index, document in enumerate(
        documents,
        start=1,
    ):
        print("-" * 60)
        print("Index:", index)
        print("Title:", document["title"])
        print("Source ID:", document["source_id"])
        print("Chunk count:", document["chunk_count"])


if __name__ == "__main__":
    main()