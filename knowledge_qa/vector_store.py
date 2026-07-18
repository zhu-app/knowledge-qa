import os

from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

# 设置 Hugging Face 镜像源（国内用户需要）
os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")

# FAISS C++ 库在 Windows 上不支持中文路径，使用纯英文路径
# 索引存储在用户主目录下的 .knowledge-qa-index/
VECTOR_STORE_PATH = os.path.normpath(
    os.path.join(os.path.expanduser("~"), ".knowledge-qa-index")
)

# Module-level singleton — model is downloaded/loaded only once
_embeddings = None


def get_embeddings():
    global _embeddings
    if _embeddings is None:
        _embeddings = FastEmbedEmbeddings(model_name="BAAI/bge-small-zh-v1.5")
    return _embeddings


def build_vector_store(documents: list[Document]) -> FAISS:
    embeddings = get_embeddings()
    splits = []
    from .splitter import get_splitter
    splitter = get_splitter()
    for doc in documents:
        chunks = splitter.split_documents([doc])
        splits.extend(chunks)
    vector_store = FAISS.from_documents(splits, embeddings)
    return vector_store


def save_vector_store(vector_store: FAISS, path: str = None):
    save_path = path or VECTOR_STORE_PATH
    # 确保路径是绝对路径且目录已创建
    save_path = os.path.abspath(save_path)
    os.makedirs(save_path, exist_ok=True)
    # 再次确认目录可写
    if not os.path.isdir(save_path):
        raise RuntimeError(f"无法创建目录: {save_path}")
    vector_store.save_local(save_path)
    # 验证文件是否已写入
    index_file = os.path.join(save_path, "index.faiss")
    if not os.path.isfile(index_file):
        raise RuntimeError(f"FAISS 索引保存失败: {index_file} 未生成")


def load_vector_store(path: str = None) -> FAISS | None:
    load_path = path or VECTOR_STORE_PATH
    index_file = os.path.join(load_path, "index.faiss")
    if not os.path.isfile(index_file):
        return None
    embeddings = get_embeddings()
    # allow_dangerous_deserialization=True 是 FAISS 的安全要求 (pickle 反序列化)
    # 风险：仅当加载不可信的 index 文件时存在。本项目索引由用户自己构建，安全可控。
    return FAISS.load_local(load_path, embeddings, allow_dangerous_deserialization=True)


def merge_vector_stores(old_vs: FAISS, new_vs: FAISS) -> FAISS:
    """Merge two FAISS vector stores by adding new documents into the old one."""
    texts = []
    metadatas = []
    for idx, doc_id in new_vs.index_to_docstore_id.items():
        doc = new_vs.docstore._dict.get(doc_id)
        if doc:
            texts.append(doc.page_content)
            metadatas.append(doc.metadata)
    if texts:
        old_vs.add_texts(texts=texts, metadatas=metadatas)
    return old_vs
