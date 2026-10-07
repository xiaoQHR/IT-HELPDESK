from dataclasses import dataclass


@dataclass(frozen=True)
class RequiredFieldResult:
    """必要字段检查结果。"""

    complete: bool
    missing_fields: list[str]
    missing_field_labels: list[str]


class RequiredFieldChecker:
    """根据业务意图检查必要字段。"""

    REQUIRED_FIELDS = {
        "billing": (
            "order_id",
            "date",
            "amount",
        ),
        "technical": (),
        "general": (),
    }

    FIELD_LABELS = {
        "order_id": "订单号或交易号",
        "date": "支付或问题发生时间",
        "amount": "支付或扣款金额",
        "error_code": "错误码",
    }

    def check(
        self,
        intent: str,
        entities: dict[str, list[str]],
    ) -> RequiredFieldResult:
        """检查当前意图所需字段是否完整。"""

        required_fields = self.REQUIRED_FIELDS.get(
            intent,
            (),
        )

        missing_fields = [
            field_name
            for field_name in required_fields
            if not entities.get(field_name)
        ]

        missing_field_labels = [
            self.FIELD_LABELS.get(
                field_name,
                field_name,
            )
            for field_name in missing_fields
        ]

        return RequiredFieldResult(
            complete=not missing_fields,
            missing_fields=missing_fields,
            missing_field_labels=(
                missing_field_labels
            ),
        )


required_field_checker = RequiredFieldChecker()