from core.required_field_checker import (
    RequiredFieldChecker,
)


def test_billing_missing_all_fields() -> None:
    checker = RequiredFieldChecker()

    result = checker.check(
        intent="billing",
        entities={
            "order_id": [],
            "date": [],
            "amount": [],
        },
    )

    assert result.complete is False
    assert result.missing_fields == [
        "order_id",
        "date",
        "amount",
    ]


def test_billing_missing_some_fields() -> None:
    checker = RequiredFieldChecker()

    result = checker.check(
        intent="billing",
        entities={
            "order_id": ["A123456"],
            "date": [],
            "amount": ["99.50"],
        },
    )

    assert result.complete is False
    assert result.missing_fields == ["date"]
    assert result.missing_field_labels == [
        "支付或问题发生时间"
    ]


def test_billing_fields_complete() -> None:
    checker = RequiredFieldChecker()

    result = checker.check(
        intent="billing",
        entities={
            "order_id": ["A123456"],
            "date": ["2026年10月3日"],
            "amount": ["99.50"],
        },
    )

    assert result.complete is True
    assert result.missing_fields == []


def test_general_requires_no_fields() -> None:
    checker = RequiredFieldChecker()

    result = checker.check(
        intent="general",
        entities={},
    )

    assert result.complete is True
    assert result.missing_fields == []