import pytest

from core.text_splitter import split_text


def test_empty_text_returns_empty_list() -> None:
    assert split_text("") == []
    assert split_text("   ") == []


def test_long_text_is_split_with_overlap() -> None:
    text = "a" * 1000

    chunks = split_text(
        text=text,
        chunk_size=500,
        overlap=50,
    )

    assert len(chunks) == 3
    assert len(chunks[0]) == 500
    assert len(chunks[1]) == 500
    assert len(chunks[2]) == 100

    # 前一片最后 50 个字符，
    # 应等于后一片最前面的 50 个字符。
    assert chunks[0][-50:] == chunks[1][:50]


@pytest.mark.parametrize(
    ("chunk_size", "overlap"),
    [
        (0, 0),
        (-1, 0),
        (500, -1),
        (500, 500),
        (500, 600),
    ],
)
def test_invalid_parameters_raise_error(
    chunk_size: int,
    overlap: int,
) -> None:
    with pytest.raises(ValueError):
        split_text(
            text="测试文本",
            chunk_size=chunk_size,
            overlap=overlap,
        )