from tools.error_code_tool import error_code_tool
import pytest

from mcp.tool_manager import tool_manager

def test_lookup_known_error_code() -> None:
    result = error_code_tool.lookup("401")

    assert result is not None
    assert result.code == "401"
    assert result.name == "Unauthorized"
    assert result.description == "请求没有通过身份认证。"
    assert len(result.suggestions) == 3


def test_lookup_normalizes_whitespace() -> None:
    result = error_code_tool.lookup(" 500 ")

    assert result is not None
    assert result.code == "500"
    assert result.name == "Internal Server Error"


def test_lookup_unknown_error_code_returns_none() -> None:
    result = error_code_tool.lookup("999")

    assert result is None


@pytest.mark.asyncio
async def test_tool_manager_looks_up_error_code() -> None:
    result = await tool_manager.lookup_error_code("401")

    assert result is not None
    assert result.code == "401"
    assert result.name == "Unauthorized"


@pytest.mark.asyncio
async def test_tool_manager_returns_none_for_unknown_code() -> None:
    result = await tool_manager.lookup_error_code("999")

    assert result is None