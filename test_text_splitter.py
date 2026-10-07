from core.text_splitter import split_text


def main() -> None:
    text = "".join(
        f"这是第{i}段测试内容，用来验证文档切片。"
        for i in range(1, 101)
    )

    chunks = split_text(
        text=text,
        chunk_size=200,
        overlap=20,
    )

    print("Original length:", len(text))
    print("Chunk count:", len(chunks))

    for index, chunk in enumerate(chunks, start=1):
        print(f"Chunk {index}: length={len(chunk)}")


if __name__ == "__main__":
    main()