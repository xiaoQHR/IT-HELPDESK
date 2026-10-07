from sentence_transformers import SentenceTransformer


from core.config import settings

class EmbeddingService:
    """统一管理文本向量模型"""

    def __init__(self) -> None:
        self._model: SentenceTransformer |None = None

    def _get_model(self)->SentenceTransformer:
        """首次使用时加载模型，之后复用同一个实例"""

        if self._model is None:
            self._model=SentenceTransformer(
                settings.embedding_model
            )
        return self._model

    def encode(
        self,
        texts:list[str],
    )->list[list[float]]:
        """将多段文本转换为归一化向量。"""
        if not texts:
            return []

        model=self._get_model()

        embeddings=model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return embeddings.tolist()
    # 把 numpy 数组转成 Python list（便于 JSON 序列化、存 Redis/Chroma）

    def encode_one(
        self,
        text:str,
    )->list[float]:
        """将一段文本转换为归一化向量。"""
        embeddings=self.encode([text])
        return embeddings[0]

embedding_service=EmbeddingService()