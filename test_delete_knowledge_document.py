from mcp.knowledge_base import KnowledgeBase


def main() -> None:
    knowledge_base = KnowledgeBase()

    source_id = (
        "8bd3a26d02536ad760116fd7f7fe683d"
        "c61518bf7f32539678dda6a65fedc2b0"
    )

    stats_before = knowledge_base.get_stats()

    deleted_chunks = knowledge_base.delete_document(
        source_id
    )

    stats_after = knowledge_base.get_stats()

    print("Deleted chunks:", deleted_chunks)
    print("Stats before:", stats_before)
    print("Stats after:", stats_after)

    remaining_titles = [
        str(document["title"])
        for document in knowledge_base.list_documents()
    ]

    print(
        "upload_test still exists:",
        "upload_test" in remaining_titles,
    )


if __name__ == "__main__":
    main()