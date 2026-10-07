import pytest

from core.document_loader import load_text_document


def test_load_utf8_text_document() -> None:
    title, content = load_text_document(
        filename="退款政策.txt",
        data="退款将在三个工作日内到账。".encode(
            "utf-8"
        ),
    )

    assert title == "退款政策"
    assert content == "退款将在三个工作日内到账。"


def test_load_gb18030_document() -> None:
    title, content = load_text_document(
        filename="中文资料.md",
        data="这是中文资料。".encode("gb18030"),
    )

    assert title == "中文资料"
    assert content == "这是中文资料。"


def test_unsupported_extension_raises_error() -> None:
    with pytest.raises(
        ValueError,
        match="暂不支持",
    ):
        load_text_document(
            filename="图片.png",
            data=b"content",
        )


def test_empty_file_raises_error() -> None:
    with pytest.raises(
        ValueError,
        match="上传文件不能为空",
    ):
        load_text_document(
            filename="空文件.txt",
            data=b"",
        )


def test_oversized_file_raises_error() -> None:
    with pytest.raises(
        ValueError,
        match="不能超过",
    ):
        load_text_document(
            filename="大文件.txt",
            data=b"123456",
            max_bytes=5,
        )