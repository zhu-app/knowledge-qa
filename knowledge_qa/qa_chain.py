from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.outputs import ChatGenerationChunk

from .config import OPENAI_API_KEY, OPENAI_BASE_URL, LLM_MODEL, SIMILARITY_THRESHOLD


def get_llm():
    return ChatOpenAI(
        model=LLM_MODEL,
        openai_api_key=OPENAI_API_KEY,
        openai_api_base=OPENAI_BASE_URL,
        temperature=0.3,
        streaming=True,
    )


def build_prompt(question: str, context: str, history: list[dict]) -> str:
    history_text = ""
    for msg in history[-6:]:
        role = "用户" if msg["role"] == "user" else "助手"
        history_text += f"{role}：{msg['content']}\n"

    return f"""你是一个知识库问答助手。请根据以下资料内容，准确回答用户的问题。
如果资料中没有相关信息，请如实说"资料中未找到相关信息"，不要编造。

资料内容：
{context}

聊天历史：
{history_text}

用户问题：{question}

回答："""


class QAChat:
    def __init__(self, vector_store):
        self.llm = get_llm()
        self.vector_store = vector_store

    def _retrieve_context(self, question: str) -> str:
        """Retrieve relevant documents with similarity threshold filtering."""
        results = self.vector_store.similarity_search_with_relevance_scores(question, k=4)
        # 使用较低的阈值（0.1）避免过滤掉短文档的相关结果
        # LLM 的 prompt 中已有"找不到就说找不到"的指令，会自行判断
        filtered = [(doc, score) for doc, score in results if score >= SIMILARITY_THRESHOLD]
        if not filtered:
            return ""
        docs = [d for d, _ in filtered]
        return "\n\n".join([d.page_content for d in docs])

    def invoke(self, question: str, history: list[dict] = None) -> str:
        """Non-streaming: returns the full answer as a string."""
        history = history or []
        context = self._retrieve_context(question)
        prompt = build_prompt(question, context, history)
        response = self.llm.invoke([HumanMessage(content=prompt)])
        return response.content

    def stream(self, question: str, history: list[dict] = None):
        """Streaming generator: yields response chunks one by one."""
        history = history or []
        context = self._retrieve_context(question)
        prompt = build_prompt(question, context, history)
        for chunk in self.llm.stream([HumanMessage(content=prompt)]):
            if chunk.content is not None:
                yield chunk.content
