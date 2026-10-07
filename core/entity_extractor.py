import re
from dataclasses import dataclass, field


@dataclass(frozen=True)
class ExtractedEntities:
    """从用户消息中抽取的业务实体。"""

    order_id: list[str] = field(
        default_factory=list
    )
    product: list[str] = field(
        default_factory=list
    )
    date: list[str] = field(
        default_factory=list
    )
    amount: list[str] = field(
        default_factory=list
    )
    error_code: list[str] = field(
        default_factory=list
    )

    def to_dict(self) -> dict[str, list[str]]:
        return {
            "order_id": self.order_id,
            "product": self.product,
            "date": self.date,
            "amount": self.amount,
            "error_code": self.error_code,
        }


class EntityExtractor:
    """使用正则表达式抽取常见业务实体。"""

    ORDER_ID_PATTERN = re.compile(
        r"(?:订单号|订单|交易号|流水号)"
        r"[：:\s]*(?:是\s*)?"
        r"([A-Za-z0-9][A-Za-z0-9_-]{3,})",
        re.IGNORECASE,
    )

    PRODUCT_PATTERN = re.compile(
        r"(?:产品|商品)(?:名称)?"
        r"[：:\s]+"
        r"([^，。；;\n]{2,50})"
    )

    DATE_PATTERN = re.compile(
        r"\d{4}(?:年|[-/.])"
        r"\d{1,2}(?:月|[-/.])"
        r"\d{1,2}日?"
        r"|"
        r"\d{1,2}月\d{1,2}日"
    )

    AMOUNT_PATTERN = re.compile(
        r"(?:¥|￥)?\s*"
        r"(\d+(?:\.\d{1,2})?)"
        r"\s*元"
    )

    ERROR_CODE_PATTERN = re.compile(
        r"\b(?:HTTP\s*)?"
        r"([1-5]\d{2})\b",
        re.IGNORECASE,
    )

    @staticmethod
    def _unique(
        values: list[str],
    ) -> list[str]:
        """去重，同时保持原始出现顺序。"""

        return list(dict.fromkeys(values))

    def extract(
        self,
        message: str,
    ) -> ExtractedEntities:
        """从消息中抽取实体。"""

        message = message.strip()

        if not message:
            return ExtractedEntities()

        order_ids = self.ORDER_ID_PATTERN.findall(
            message
        )

        products = [
            value.strip()
            for value
            in self.PRODUCT_PATTERN.findall(message)
        ]

        dates = self.DATE_PATTERN.findall(message)

        amounts = self.AMOUNT_PATTERN.findall(
            message
        )

        error_codes = (
            self.ERROR_CODE_PATTERN.findall(
                message
            )
        )

        return ExtractedEntities(
            order_id=self._unique(order_ids),
            product=self._unique(products),
            date=self._unique(dates),
            amount=self._unique(amounts),
            error_code=self._unique(error_codes),
        )


entity_extractor = EntityExtractor()