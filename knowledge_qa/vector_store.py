import os

from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

# 设置 Hugging Face 镜像源（国内用户需要）
os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")

VECTOR_STORE_PATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "data", "faiss_index")
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
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    vector_store.save_local(save_path)


def load_vector_store(path: str = None) -> FAISS | None:
    load_path = path or VECTOR_STORE_PATH
    if not os.path.exists(load_path):
        return None
    embeddings = get_embeddings()
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
