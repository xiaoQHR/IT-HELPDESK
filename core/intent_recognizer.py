
from dataclasses import dataclass



@dataclass(frozen=True)
class IntentResult:
    """意图识别结果"""
    intent:str
    confidence:float
    # 暂时使用关键词匹配
    matched_keywords:list[str]

class IntentRecognizer:
    """基于关键词规则识别用户的意图"""

    BILLING_KEYWORDS=[
        "退款",
        "扣款",
        "账单",
        "支付",
        "发票",
        "订阅",
        "续费",
        "金额",
    ]
    
    TECHNICAL_KEYWORDS = [
        "报错",
        "错误",
        "登录",
        "崩溃",
        "接口",
        "api",
        "部署",
        "网络",
        "超时",
        "401",
        "403",
        "404",
        "500",
    ]

    def recognize(self,message:str) -> IntentResult:
        normalized_message=message.lower()
        # 英文转为小写

        billing_matches=[
            keyword
            for keyword in self.BILLING_KEYWORDS
            if keyword in normalized_message
        ]
        # 寻找命中的关键词

        technical_matches=[
            keyword
            for keyword in self.TECHNICAL_KEYWORDS
            if keyword in normalized_message
        ]

        if (
                billing_matches
                and len(billing_matches)
                >= len(technical_matches)
        ):
            return IntentResult(
                intent="billing",
                confidence=min(0.6+len(billing_matches)*0.1,0.95),
                # 账单问题要置信度高，0.6+命中数量*0.1；命中越多置信度越高，最高不超过0.95
                matched_keywords=billing_matches,
            )

        if technical_matches:
            return IntentResult(
                intent="technical",
                confidence=min(0.6+len(technical_matches)*0.1,0.95),
                matched_keywords=technical_matches,
            )


        return IntentResult(
            intent="general",
            confidence=0.5,
        #   普通问题置信度居中
            matched_keywords=[],
        )