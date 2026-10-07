from core.entity_extractor import EntityExtractor


def test_extract_business_entities() -> None:
    extractor = EntityExtractor()

    entities = extractor.extract(
        "订单号 A123456 在 2026年10月3日"
        "支付了 99.50 元，登录时出现 HTTP 401。"
    )

    assert entities.order_id == ["A123456"]
    assert entities.date == ["2026年10月3日"]
    assert entities.amount == ["99.50"]
    assert entities.error_code == ["401"]


def test_extract_product() -> None:
    extractor = EntityExtractor()

    entities = extractor.extract(
        "产品名称：IT Helpdesk 企业版，无法正常登录。"
    )

    assert entities.product == [
        "IT Helpdesk 企业版"
    ]


def test_duplicate_entities_are_removed() -> None:
    extractor = EntityExtractor()

    entities = extractor.extract(
        "订单号 A123456，还是订单号 A123456。"
    )

    assert entities.order_id == ["A123456"]


def test_empty_message_returns_empty_entities() -> None:
    extractor = EntityExtractor()

    entities = extractor.extract("   ")

    assert entities.to_dict() == {
        "order_id": [],
        "product": [],
        "date": [],
        "amount": [],
        "error_code": [],
    }