from pathlib import Path
SUPPORTED_EXTENSIONS={
    # set而非list,线性查找时间复杂度
    ".txt",
    ".md",
}
# 上限是2mb，单个文件不超过2mb

DEFAULT_MAX_BYTES=2*1024*1024


def load_text_document(
        filename:str,
        data:bytes,
        max_bytes:int=DEFAULT_MAX_BYTES,
) -> tuple[str,str]:
    """
    校验并读取文件
    :param filename:
    :param data:
    :param max_bytes:
    :return: 文档标题，文档正文
    """
    if not filename.strip():
        raise ValueError("文件名不能为空")

    if not data:
        raise ValueError("上传文件不能为空")

    if len(data)>max_bytes:
        raise ValueError(
            f"文件不能超过{max_bytes}字节"
        )

    path=Path(filename)
    # 去后缀并转小写
    extension=path.suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        supported=",".join(
            sorted(SUPPORTED_EXTENSIONS)
        )
        raise ValueError(
            f"暂不支持{extension or '无扩展名'}文件，"
            f"当前支持{supported}"
        )

    content:str|None=None

    for encoding in(
        "utf-8-sig",
        "utf-8",
        "gb18030",
    ):
        try:
            content=data.decode(encoding)
            break
        except UnicodeDecodeError:
            continue

    if content is None:
        raise ValueError(
            "无法识别文件编码，请使用 UTF-8 编码"
        )

    content =content.strip()

    if not content:
        raise ValueError("文件正文不能为空")

    title=path.stem.strip()

    if not title:
        raise ValueError("无法从文件名中获取文档标题")

    return title,content