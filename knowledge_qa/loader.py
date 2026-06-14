import os
import tempfile
from pathlib import Path

import pdfplumber
import requests
from bs4 import BeautifulSoup
from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document


def load_pdf(file_path: str) -> list[Document]:
    docs = []
    with pdfplumber.open(file_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text and text.strip():
                docs.append(Document(
                    page_content=text.strip(),
                    metadata={"source": os.path.basename(file_path), "page": i + 1, "type": "pdf"}
                ))
    return docs


def load_markdown(file_path: str) -> list[Document]:
    loader = TextLoader(file_path, encoding="utf-8")
    docs = loader.load()
    for d in docs:
        d.metadata.update({"source": os.path.basename(file_path), "type": "markdown"})
    return docs


def load_text(file_path: str) -> list[Document]:
    loader = TextLoader(file_path, encoding="utf-8")
    docs = loader.load()
    for d in docs:
        d.metadata.update({"source": os.path.basename(file_path), "type": "text"})
    return docs


def load_webpage(url: str) -> list[Document]:
    resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
    resp.raise_for_status()

    content_type = resp.headers.get("Content-Type", "")
    if "text/html" not in content_type:
        raise ValueError(f"URL 返回的内容类型不支持: {content_type}（仅支持 HTML 网页）")

    soup = BeautifulSoup(resp.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    text = soup.get_text(separator="\n", strip=True)
    lines = [line for line in text.split("\n") if line.strip()]
    cleaned = "\n".join(lines)
    return [Document(
        page_content=cleaned,
        metadata={"source": url, "type": "webpage"}
    )]


SUPPORTED_EXTENSIONS = {".pdf", ".md", ".txt"}


def load_file(file_path: str) -> list[Document]:
    ext = Path(file_path).suffix.lower()
    if ext == ".pdf":
        return load_pdf(file_path)
    elif ext == ".md":
        return load_markdown(file_path)
    elif ext == ".txt":
        return load_text(file_path)
    else:
        raise ValueError(
            f"不支持的文件格式: {ext!r}，支持的格式: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )
