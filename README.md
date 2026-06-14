# 📚 个人知识库问答系统

基于 **RAG (Retrieval-Augmented Generation)** 架构的本地知识库问答系统，支持多种文档格式导入，通过向量检索 + LLM 实现智能问答与多轮对话。

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B?style=flat&logo=streamlit)
![License](https://img.shields.io/badge/License-MIT-blue.svg?style=flat)

## 功能特性

- **多格式文档导入** — 支持 PDF、Markdown、TXT 及网页内容
- **语义检索** — FAISS 向量库 + FastEmbed 中文嵌入模型 (`BAAI/bge-small-zh-v1.5`)
- **智能问答** — 基于 LLM 的上下文理解与精准回答
- **多轮对话** — 保留最近 6 轮对话上下文，支持深度追问
- **流式输出** — LLM 回复逐块实时显示，降低等待感
- **模型兼容** — 支持任何 OpenAI 兼容接口：OpenAI / DeepSeek / 智谱 GLM / Qwen 等
- **索引持久化** — FAISS 索引自动保存到本地，避免重复构建

## 技术栈

| 组件 | 技术选型 |
|---|---|
| 框架 | LangChain |
| UI | Streamlit |
| 向量库 | FAISS |
| 嵌入模型 | FastEmbed (`BAAI/bge-small-zh-v1.5`) |
| 向量检索 | `similarity_search_with_relevance_scores` |
| LLM | ChatOpenAI (OpenAI 兼容接口) |

## 系统架构

```
┌──────────────┐     ┌──────────────────┐     ┌──────────────┐
│  用户上传文档  │────▶│  文档分块 (Chunk)  │────▶│  向量化嵌入    │
│ PDF/MD/TXT   │     │  RecursiveChar   │     │ FastEmbed    │
└──────────────┘     └──────────────────┘     └──────┬───────┘
                                                      │
                                                      ▼
┌──────────────┐     ┌──────────────────┐     ┌──────────────┐
│  用户提问     │────▶│  向量检索 (FAISS)  │────▶│  LLM 生成回答  │
│  多轮对话     │     │  相似度阈值过滤    │     │  流式输出    │
└──────────────┘     └──────────────────┘     └──────────────┘
```

## 快速开始

### 1. 环境要求

- Python 3.10+
- Windows / macOS / Linux

### 2. 安装

```powershell
# Windows: 一键安装
.\setup.bat

# macOS / Linux (手动安装)
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. 配置

```bash
# 复制并编辑配置文件
cp .env.example .env
# 编辑 .env，填入你的 API Key
```

`.env` 配置文件说明：

| 变量 | 默认值 | 说明 |
|---|---|---|
| `OPENAI_API_KEY` | *(必填)* | LLM API 密钥 |
| `OPENAI_BASE_URL` | `https://api.openai.com/v1` | OpenAI 兼容接口地址 |
| `LLM_MODEL` | `gpt-4o-mini` | 使用的模型名称 |
| `EMBEDDING_MODEL` | `embedding-2` | Embedding 模型标识（实际模型已内置） |
| `SIMILARITY_THRESHOLD` | `0.5` | 相似度阈值 (0.0~1.0)，低于此值的结果将被过滤 |

### 4. 启动

```powershell
# Windows
.\start.bat

# 手动启动
python -m streamlit run app.py --server.port 8501
```

打开浏览器访问 `http://localhost:8501`

## 项目结构

```
knowledge-qa/
├── app.py                          # Streamlit 主应用（UI + 对话 + 文件上传）
├── knowledge_qa/                   # 核心模块
│   ├── config.py                   # 配置加载、API Key 校验、模型配置
│   ├── loader.py                   # 文档加载器（PDF / Markdown / TXT / 网页）
│   ├── splitter.py                 # 文本分块（RecursiveCharacterTextSplitter）
│   ├── vector_store.py             # FAISS 向量库（构建 / 保存 / 加载 / 合并）
│   └── qa_chain.py                 # LLM 封装、Prompt 构建、QAChat 对话类
├── data/faiss_index/               # FAISS 索引持久化目录
├── .env                            # 运行时配置（不提交到 Git）
├── .env.example                    # 配置模板
├── requirements.txt                # Python 依赖
├── setup.bat                       # Windows 一键安装脚本
└── start.bat                       # Windows 启动脚本
```

## 常见问题

**Q: 如何切换 LLM 模型？**

修改 `.env` 中的 `OPENAI_BASE_URL` 和 `LLM_MODEL` 即可。任何兼容 OpenAI 接口的服务都支持。

**Q: Embedding 模型可以更换吗？**

Embedding 模型在代码中硬编码为 `BAAI/bge-small-zh-v1.5`（通过 FastEmbed 自动下载）。如需更换，可修改 `knowledge_qa/vector_store.py` 中的模型名称。

**Q: 如何提高检索准确率？**

尝试调低 `SIMILARITY_THRESHOLD`（如 0.3），让更多相关片段进入上下文。

**Q: Embedding 模型下载慢？**

设置环境变量 `HF_ENDPOINT=https://hf-mirror.com` 使用 Hugging Face 镜像。

## 许可证

MIT License
