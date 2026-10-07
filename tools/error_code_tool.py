from dataclasses import dataclass


@dataclass(frozen=True)
class ErrorCodeResult:
    """错误码查询结果。"""

    code: str
    name: str
    description: str
    suggestions: list[str]


class ErrorCodeTool:
    """查询常见 HTTP 错误码及排查建议。"""

    ERROR_CODES: dict[str, ErrorCodeResult] = {
        "401": ErrorCodeResult(
            code="401",
            name="Unauthorized",
            description="请求没有通过身份认证。",
            suggestions=[
                "检查用户名、密码或验证码",
                "检查 Authorization 请求头",
                "确认访问令牌是否过期",
            ],
        ),
        "403": ErrorCodeResult(
            code="403",
            name="Forbidden",
            description="身份认证成功，但当前身份没有访问权限。",
            suggestions=[
                "检查账号角色和资源权限",
                "确认接口是否要求管理员权限",
                "检查网关或访问控制策略",
            ],
        ),
        "404": ErrorCodeResult(
            code="404",
            name="Not Found",
            description="服务器没有找到请求的资源。",
            suggestions=[
                "检查请求地址和接口路径",
                "确认资源是否已经被删除",
                "检查服务版本和路由配置",
            ],
        ),
        "500": ErrorCodeResult(
            code="500",
            name="Internal Server Error",
            description="服务端处理请求时发生内部异常。",
            suggestions=[
                "记录请求时间和 request_id",
                "查看服务端错误日志",
                "检查数据库及依赖服务状态",
            ],
        ),
    }

    def lookup(self, code: str) -> ErrorCodeResult | None:
        """根据错误码查询解释和建议。"""

        normalized_code = code.strip()
        return self.ERROR_CODES.get(normalized_code)


error_code_tool = ErrorCodeTool()