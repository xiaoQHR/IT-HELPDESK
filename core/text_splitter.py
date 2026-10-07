

def split_text(
        text:str,
        chunk_size:int=500,
        overlap:int =50,
) -> list[str]:
    """按照指定长度切分文本，并在相邻切片间保留重叠内容。"""

    text=text.strip()

    if not text:
        return []

    if chunk_size<=0:
        raise ValueError("chunk_size必须大于0")

    if overlap <0:
        raise ValueError("overlap不能小于0")

    if overlap>=chunk_size:
        raise ValueError("overlap必须小于chunk_size")

    chunks:list[str]=[]
    start=0

    while start<len(text):
        end=min(start+chunk_size,len(text))
        chunk=text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end>=len(text):
            break

        # 下一块向前回退overlap个字符，保证上下文衔接
        start=end - overlap

    return chunks