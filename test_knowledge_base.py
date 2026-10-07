from mcp.knowledge_base import KnowledgeBase


TEST_DOCUMENTS = [
    {
        "title": "退款政策",
        "content": (
            "退款申请审核通过后，款项将原路退回。"
            "支付宝和微信通常需要 1 至 3 个工作日，"
            "银行卡通常需要 3 至 7 个工作日。"
        ),
    },
    {
        "title": "登录故障排查",
        "content": (
            "登录出现 401 错误时，请检查账号密码、"
            "访问令牌、Authorization 请求头以及账号状态。"
        ),
    },
    {
        "title": "配送说明",
        "content": (
            "普通订单付款后通常会在 48 小时内发货，"
            "发货后可以通过订单页面查看物流进度。"
        ),
    },
]


def main() -> None:
    knowledge_base = KnowledgeBase()

    if knowledge_base.count() == 0:
        document_ids = knowledge_base.add_documents(
            TEST_DOCUMENTS
        )

        print("Added document IDs:")
        for document_id in document_ids:
            print("-", document_id)
    else:
        print(
            "Knowledge base already contains documents:",
            knowledge_base.count(),
        )

    query = "退款什么时候可以到账？"

    results = knowledge_base.search(
        query=query,
        top_k=3,
    )

    print()
    print("Query:", query)
    print("Results:")

    for index, result in enumerate(
        results,
        start=1,
    ):
        print("-" * 60)
        print("Rank:", index)
        print("Title:", result.title)
        print("Score:", result.score)
        print("Content:", result.content)


if __name__ == "__main__":
    main()