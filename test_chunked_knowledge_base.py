from mcp.knowledge_base import KnowledgeBase


def main() -> None:
    knowledge_base = KnowledgeBase()

    long_content = """
会员退款规则如下。用户提交退款申请后，平台会先检查订单状态、
支付状态和商品使用情况。只有符合退款条件的订单才会进入退款审核流程。

退款审核通过后，款项会原路退回。支付宝和微信支付通常需要一至三个工作日，
银行卡支付通常需要三至七个工作日。节假日可能影响银行处理速度。

如果用户发现重复扣款，需要提供订单号、交易时间、支付渠道和扣款金额。
客服人员只能帮助核实交易状态，不能要求用户提供银行卡密码、短信验证码
或者完整的支付密钥。

如果退款超过正常到账时间，用户可以先检查原支付账户的交易记录。
如果仍然没有收到退款，可以联系人工客服，并提供订单号和退款申请时间。
客服人员可以根据退款流水号进一步核实支付渠道的处理状态。

账号安全同样非常重要。用户不应该通过聊天窗口发送密码、验证码、
完整银行卡号或者访问令牌。如果发现账号存在异常登录，应立即修改密码，
退出其他设备，并联系安全支持人员。

为了避免重复提交，系统会根据文档标题和正文内容生成稳定的文档标识。
同一篇文档被重复导入时，系统使用 upsert 更新已有切片，而不是不断创建
内容完全相同的新记录。
""".strip()


    # 重复三次，使文档长度超过切片上限。
    long_content = "\n\n".join(
        [long_content] * 3
    )
    
    document = {
        "title": "会员退款与安全处理指南",
        "content": long_content,
    }

    count_before = knowledge_base.count()

    first_ids = knowledge_base.add_documents([document])
    count_after_first = knowledge_base.count()

    second_ids = knowledge_base.add_documents([document])
    count_after_second = knowledge_base.count()

    print("Original document length:", len(long_content))
    print("Generated chunk count:", len(first_ids))
    print("Count before:", count_before)
    print("Count after first import:", count_after_first)
    print("Count after second import:", count_after_second)
    print("IDs reused:", first_ids == second_ids)
    print("Duplicate import added records:", count_after_second - count_after_first)

    results = knowledge_base.search(
        query="退款超过正常到账时间应该怎么处理？",
        top_k=3,
    )

    print("\nSearch results:")

    for index, result in enumerate(results, start=1):
        print("-" * 60)
        print("Rank:", index)
        print("Title:", result.title)
        print("Score:", result.score)
        print("Content length:", len(result.content))
        print("Content:", result.content)


if __name__ == "__main__":
    main()