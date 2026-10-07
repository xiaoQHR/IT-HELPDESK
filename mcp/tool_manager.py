import asyncio


from mcp.knowledge_base import (
    KnowledgeBase,
    SearchResult,
)
from tools.error_code_tool import (
    ErrorCodeResult,
    error_code_tool,
)

class ToolManager:
    """统一管理agent可以使用的工具"""

    def __init__(self) -> None:
        # 实例化知识库，作为本类的成员
        self.knowledge_base=KnowledgeBase()

    async def search_knowledge_base(
        self,
        query:str,
        top_k:int=3,
        min_score:float=0.5,
    ) -> list[SearchResult]:
        """检索知识库，并避免同一文档占满结果"""

        if top_k<=0:
            raise ValueError("top_k必须大于0")
        # 多取一些候选切片，再进行来源去重。
        candidate_top_k=top_k*4
        candidates=await asyncio.to_thread(
            self.knowledge_base.search,
            query,
            candidate_top_k,
        )

        selected_results:list[SearchResult]=[]
        seen_titles:set[str]=set()

        for result in candidates:
            if result.score<min_score:
                continue

                # 当前系统将标题作为逻辑文档标识。
            if result.title in seen_titles:
                continue

            seen_titles.add(result.title)
            selected_results.append(result)

            if len(selected_results) >= top_k:
                 break

        return selected_results
        # # 把同步阻塞调用扔进线程池中，转为异步
        # # search函数是同步阻塞的，内部需要发HTTP请求给chroma，等数据返回，如果直接在async中调用，则在等待的时候会阻塞线程
        # # 因此asyncio.to_thread把同步函数扔到线程池的某个工作进程执行，主事件循环处理其他任务，等线程执行完再将结果传回给await
        # results= await asyncio.to_thread(
        #     # 要执行的同步函数（只传函数名不传括号）
        #     self.knowledge_base.search,
        #     query,
        #     top_k,
        # )
        # return [
        #     result
        #     for result in results
        #     if result.score>=min_score
        # ]


    async def lookup_error_code(
        self,
        code: str,
    ) -> ErrorCodeResult | None:
        """异步查询错误码信息。"""

        return await asyncio.to_thread(
            error_code_tool.lookup,
            code,
        )

    @staticmethod
    def format_knowledge_context(
        results:list[SearchResult],
    ) ->str:
        """将检索结果格式化为适合注入prompt的文本。"""
        if not results:
            return ""

        sections:list[str]=[]

        for index,result in enumerate(
            results,
            # 从1开始编号
            start=1,
        ):
            # 拼接单个资料快
            section=(
                f"[知识库资料 {index}]\n"
                f"标题：{result.title}\n"
                f"相关度：{result.score}\n"
                f"内容：{result.content}"
            )
            sections.append(section)

        return "\n\n".join(sections)

    async def add_knowledge_documents(
            self,
            documents:list[dict[str,str]],
    ) -> list[str]:
        """异步生成向量并添加知识库文档"""
        return await asyncio.to_thread(
            self.knowledge_base.add_documents,
            documents,
        )

    async def get_knowledge_count(self) ->int:
        """异步获取知识库文档数量"""
        return await asyncio.to_thread(
            self.knowledge_base.count,
        )

    async def get_knowledge_stats(self)->dict[str,int]:
        """异步获取知识库的文档数和切片数"""

        return await asyncio.to_thread(
            self.knowledge_base.get_stats,
        )


    async def list_knowledge_documents(
        self,
    )->list[dict[str,str|int]]:
        """异步获取知识库原始文档列表"""
        return await asyncio.to_thread(
            self.knowledge_base.list_documents,
        )

    async def delete_knowledge_document(
            self,
            source_id:str,
    )->int:
        """异步删除原始文档及其全部切片"""
        return await asyncio.to_thread(
            self.knowledge_base.delete_document,
            source_id,
        )

tool_manager=ToolManager()