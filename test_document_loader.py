from core.document_loader import load_text_document


def main() -> None:
    title, content = load_text_document(
        filename="退款政策.md",
        data=(
            "退款审核通过后，款项将原路退回。"
            "银行卡通常需要三至七个工作日。"
        ).encode("utf-8"),
    )

    print("Title:", title)
    print("Content:", content)

    try:
        load_text_document(
            filename="图片.png",
            data=b"not-an-image",
        )
    except ValueError as exc:
        print("Unsupported file error:", exc)

    try:
        load_text_document(
            filename="空文件.txt",
            data=b"",
        )
    except ValueError as exc:
        print("Empty file error:", exc)


if __name__ == "__main__":
    main()