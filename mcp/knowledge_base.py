
from dataclasses import  dataclass
import hashlib
# 生成全局唯一文档id

import chromadb
from chromadb.config import Settings as ChromaSettings

from core.config import settings
from core.embedding_service import embedding_service
from core.text_splitter import split_text

@dataclass(frozen=True)
class SearchResult:
    """知识库检索结果"""
    document_id:str
    title:str
    content:str
    score:float

class KnowledgeBase:
    """使用chromaDB管理和检索知识库文档"""

    COLLECTION_NAME="knowledge_base"
    def __init__(self) ->None:
        self.client=chromadb.HttpClient(
            host=settings.chroma_host,
            port=settings.chroma_port,
            settings=ChromaSettings(
                anonymized_telemetry=False,
            #     关闭匿名遥测，不上报使用数据
            ),
        )
        self.collection=(
            self.client.get_or_create_collection(
                name=self.COLLECTION_NAME,
                metadata={
                    "hnsw:space":"cosine",
                },
            #     l2欧氏距离，ip内积（适合已归一化向量），此处向量已经归一化，可以使用ip，也可以cosine
            )
        )

    def add_documents(
        self,
        documents : list[dict[str,str]],
    #    document是字典列表类型的，每个含title和content
    ) -> list[str]:
    #     返回生成的文档ID列表
        """将文档切分、生成向量并写入chromaDB"""
        if not documents:
            return []

        ids: list[str]=[]
        contents: list[str]=[]
        metadatas: list[dict[str, str|int]]=[]
        # 用于记录每个标题在本次导入中生成了哪些切片ID
        current_ids_by_title:dict[str, set[str]]={}
    #     待写入的ID列表、正文列表、元数据列表

        for document in documents:
            title=document.get("title","").strip()
            content=document.get("content","").strip()

            if not title:
                raise ValueError("文档 title 不能为空")

            if not content:
                raise ValueError("文档 content 不能为空")

            # source_id表示原始文档的稳定ID
            source_id=self._build_document_id(
                title=title,
                content=content,
            )
            chunks=split_text(
                text=content,
                chunk_size=500,
                overlap=50,
            )

            total_chunks=len(chunks)
            for chunk_index,chunk in enumerate(chunks):

            # 短文档继续使用原来的文档 ID，
            # 避免已有短文档被重复写入。
                if total_chunks==1:
                    chunk_id=source_id
                else:
                    chunk_id=self._build_chunk_id(
                        source_id=source_id,
                        chunk_index=chunk_index,
                )

                ids.append(chunk_id)

                contents.append(chunk)

                # 如果是第一次出现这个标题，先创建空集合，然后将当前切片ID加进去
                current_ids_by_title.setdefault(
                    title,
                    set(),
                ).add(chunk_id)

                metadatas.append(
                    {
                        "title": title,
                        "source_id":source_id,
                        "chunk_index":chunk_index,
                        "total_chunks":total_chunks,
                     }
                )

        embeddings=embedding_service.encode(contents)

        # upsert的含义：ID不存在则新增，存在则更新。则同一个文档重复提交不会产生多份相同数据
        self.collection.upsert(
            ids=ids,
            documents=contents,
            metadatas=metadatas,
            embeddings=embeddings,
        )
        # 删除相同标题下不属于当前版本的旧切片
        for title,current_ids in current_ids_by_title.items():
            stored_records=self.collection.get(
                where={"title":title},
                include=["metadatas"],
            )
            stored_ids=stored_records["ids"]

            stale_ids=[
                stored_id
                for stored_id in stored_ids
                if stored_id not in current_ids
            ]

            if stale_ids:
                self.collection.delete(ids=stale_ids)

        return ids

    def search(
        self,
        query: str,
        top_k: int =3
    )-> list[SearchResult]:
        """根据语义相似度检索知识库"""

        query=query.strip()

        if not query:
            raise ValueError("query 不能为空")

        if top_k<=0:
            raise ValueError("top_k必须大于0")
#         先进行strip再判空，因为用户可能全部输入空格，如果只判断 not query，则会被判为非空，因此先清理空格再判空

        document_count=self.collection.count()
#         查询集合内的文档总数
        if document_count==0:
            return []

        query_embedding=embedding_service.encode_one(query)
#         查询文本转换为向量
        result_count=min(top_k,document_count)
#         不请求超过实际文档数的结果，如果知识库只有2个文档，但是top_k=3，则如果直接传n_counts=3，chroma会抛出异常,要求 n_results <= count,用 min 保证请求数量永远不超过实际库存

        raw_result=self.collection.query(
            query_embeddings=[query_embedding],
            # 外面包一层列表，支持批量查询，这里只查询一个
            n_results=result_count,
            # 返回数据数量
            include=[
                "documents",
                "metadatas",
                "distances",
            ],
        #     chromaDB支持批量查询（一次传多个query），所以接口设计为list[list[sloat]],我们这只查一个，就用单元素列表包装
        #       返回结构中，每个字段都多了一层批次维度（外面多一层[]表示批次）
        )
        ids=raw_result["ids"][0]
        documents=raw_result["documents"][0]
        metadatas=raw_result["metadatas"][0]
        distances=raw_result["distances"][0]
#        此处只取第0个批次，因为我们只差查了一个

        results:list[SearchResult]=[]
#         最终结果列表
        for(
            document_id,
            content,
            metadata,
            distance,
        ) in zip(
            ids,
            documents,
            metadatas,
            distances,
        ):
            score=max(
                0.0,
                min(1.0,1.0-float(distance)),
            #     上限1，1-距离
            #     chroma返回的是距离(越小越相关),但searchresult.score是相似度评分,二者转换公式为:相似度=1-距离
            #     使用余弦距离时,距离范围:[0,2],距离为0则完全相同,相似度1.0;距离为2时完全相反,相似度为-1.0
            #     因此1-distance可能会得到负数,用Max(0.0,...)夹到0,用min(1.0,...)夹到1,这就是夹紧(clamp)操作

            )

            results.append(
                SearchResult(
                    document_id=document_id,
                    title=metadata.get(
                        "title",
                        "未命名文档",
                    #     元数据缺失的时候使用未命名文档
                    ),
                    content=content,
                    score=round(score,4),
                # round(score,4)保留四位小数
                )
            )
        return results
#     返回结果列表

    @staticmethod
    def _build_document_id(
            title:str,
            content:str,
    ) -> str:
        """根据标题和内容生成稳定的文档ID"""
        source_text=f"{title}\n{content}"
        # 使用sha256不用于加密。用于生成内容指纹：每次使用同样的标题和内容会得到相同的结果，则不会出现相同内容但是不同编号的情况
        return hashlib.sha256(
            source_text.encode("utf-8")
        ).hexdigest()

    @staticmethod
    def _build_chunk_id(
            source_id:str,
            chunk_index:int,
    )->str:
        """根据原始文档ID和切片序号生成稳定的切片ID。"""

        chunk_identity=f"{source_id}:{chunk_index}"

        return hashlib.sha256(
            chunk_identity.encode("utf-8")
        ).hexdigest()

    def count_chunks(self)->int:
        """返回知识库中的向量切片数量"""
        return self.collection.count()
#     用于健康检查(health返回文档数),监控面板,判断是否需要重建索引

    def count_documents(self)->int:
        """返回知识库中原始文档数量"""
        stored_records=self.collection.get(
            include=["metadatas"],
        )
        stored_ids=stored_records["ids"]
        stored_metadatas=stored_records["metadatas"]

        source_ids:set[str]=set()

        for record_id,metadata in zip(
            stored_ids,
            stored_metadatas,
        ):
            metadata=metadata or {}
#            新版数据通过source_id 判断属于哪篇原始文档
            source_id=metadata.get("source_id")

            if source_id:
                source_ids.add(str(source_id))
            else:
#                 兼容以前没有source_id的旧数据
#                 将该记录自身的ID当作原始文档ID
                source_ids.add(record_id)

        return len(source_ids)

    def get_stats(self)->dict[str,int]:
        """返回知识库文档和切片统计信息"""

        return{
            "total_documents":self.count_documents(),
            "total_chunks":self.count_chunks(),
        }

    def count(self)->int:
        """兼容旧代码，返回知识库中的切片数量"""
        return self.count_chunks()


    def list_documents(
            self,
    ) -> list[dict[str,str|int]]:
        """按原始文档分组返回知识库文档列表"""

        stored_records=self.collection.get(
            include=["metadatas"],
        )
        stored_ids=stored_records["ids"]
        stored_metadatas=stored_records["metadatas"]

        document_groups:dict[
            str,
            dict[str,str|int],
        ]={}

        for record_id,metadata in zip(
            stored_ids,
            stored_metadatas,
        ):
            metadata=metadata or {}

            title=str(
                metadata.get("title","未命名文档")
            )
#             兼容没有source_id的旧数据
            source_id=str(
                metadata.get("source_id") or record_id
            )

            if source_id not in document_groups:
                document_groups[source_id]={
                    "source_id":source_id,
                    "title":title,
                    "chunk_count":0,
                }
            document_groups[source_id]["chunk_count"]+=1

        return sorted(
            document_groups.values(),
            key=lambda document:str(document["title"]),
        )

    def delete_document(
        self,
        source_id:str,
    )->int:
        """根据source_id删除原始文档及其全部切片"""
        source_id=source_id.strip()

        if not source_id:
            raise ValueError("source_id 不能为空")

        stored_records=self.collection.get(
            include=["metadatas"],
        )
        stored_ids=stored_records["ids"]
        stored_metadatas=stored_records["metadatas"]

        ids_to_delete:list[str]=[]

        for record_id,metadata in zip(
            stored_ids,
            stored_metadatas,
        ):
            metadata=metadata or {}
            metadata_source_id=metadata.get(
                "source_id"
            )
            # 新数据通过metadata,source_id匹配
            if metadata_source_id==source_id:
                ids_to_delete.append(record_id)
                continue

            if(
                not metadata_source_id
                and record_id==source_id
            ):
                ids_to_delete.append(record_id)

        if not ids_to_delete:
            return 0

        self.collection.delete(
            ids=ids_to_delete,
        )

        return len(ids_to_delete)
