# 📚 Knowledge QA — 个人知识库问答系统

> 基于 **RAG (Retrieval-Augmented Generation)** 架构的本地知识库问答系统。上传文档后自动构建向量索引，通过语义检索 + LLM 实现智能问答。

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://python.org)
[![LangChain](https://img.shields.io/badge/LangChain-0.2-1C3C3C?logo=langchain)](https://langchain.com)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B?logo=streamlit)](https://streamlit.io)
[![FAISS](https://img.shields.io/badge/Vector-FAISS-00BFFF)](https://github.com/facebookresearch/faiss)
[![FastEmbed](https://img.shields.io/badge/Embed-BGE--small--zh-6C5CE7)](https://github.com/qdrant/fastembed)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## ✨ 功能特性

| 功能 | 说明 |
|------|------|
| 📄 **多格式文档导入** | PDF / Markdown / TXT / 网页内容 |
| 🔍 **语义向量检索** | FAISS + FastEmbed (`BAAI/bge-small-zh-v1.5`)，512 维向量 |
| 🤖 **多模型 LLM 支持** | OpenAI / DeepSeek / 智谱 GLM / Qwen / 任意 OpenAI 兼容接口 |
| 💬 **多轮对话** | 保留最近 6 轮上下文，支持深度追问 |
| ⚡ **流式输出** | LLM 回复逐块实时显示，打字光标效果 |
| 💾 **索引持久化** | FAISS 索引自动保存至 `~/.knowledge-qa-index`，重启不用重建 |
| 📊 **知识库统计** | 文档源数量、文本段数量实时显示，支持增量合并 |
| 🎨 **精致 UI** | 蓝紫品牌色 + 聊天气泡 + 动画过渡，深色侧边栏管理面板 |
| 🌐 **网页导入** | 输入 URL 自动抓取正文，去噪后构建索引 |

---

## 🛠️ 技术栈

| 组件 | 选型 |
|------|------|
| **框架** | LangChain |
| **UI** | Streamlit |
| **向量库** | FAISS (Facebook AI Similarity Search) |
| **嵌入模型** | FastEmbed `BAAI/bge-small-zh-v1.5` |
| **文档分块** | RecursiveCharacterTextSplitter (chunk_size=500, overlap=100) |
| **LLM** | ChatOpenAI（兼容 OpenAI 接口） |
| **PDF 解析** | pdfplumber |
| **网页抓取** | requests + BeautifulSoup4 |
| **配置管理** | python-dotenv |

---

## 🏗️ 系统架构

```
                    ┌─────────────────────┐
                    │   用户上传文档/网页   │
                    │  PDF / MD / TXT / URL │
                    └─────────┬───────────┘
                              ▼
                    ┌─────────────────────┐
                    │  文档分块 (Chunk)    │
                    │ RecursiveCharText   │
                    │ Splitter            │
                    │ chunk_size=500      │
                    │ chunk_overlap=100   │
                    └─────────┬───────────┘
                              ▼
                    ┌─────────────────────┐
                    │  向量化嵌入 (Embed)  │
                    │ FastEmbed           │
                    │ bge-small-zh-v1.5   │
                    │ 512维               │
                    └─────────┬───────────┘
                              ▼
                    ┌─────────────────────┐
                    │  FAISS 向量索引      │
                    │  持久化到本地磁盘    │
                    │  ~/.knowledge-qa-    │
                    │  index/              │
                    └─────────┬───────────┘
                              │
    ┌──────────┐    ┌────────┴────────┐    ┌──────────┐
    │ 用户提问  │───▶│  语义检索 (k=4) │───▶│  LLM 回答 │
    │ 多轮对话  │    │  阈值过滤        │    │  流式输出 │
    └──────────┘    └─────────────────┘    └──────────┘
```

---

## 🚀 快速开始

### 前置要求

- Python 3.10+
- Windows / macOS / Linux
- 一个 LLM API Key（支持 OpenAI / 智谱 GLM / DeepSeek / Qwen 等）

### 1. 安装

```bash
git clone <your-repo-url>
cd knowledge-qa

# 创建虚拟环境
python -m venv venv

# Windows:
venv\Scripts\activate
# macOS / Linux:
# source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置

```bash
# 复制环境变量模板
cp .env.example .env
```

编辑 `.env` 文件，填入你的 API Key：

```env
# 以智谱 GLM 免费模型为例
OPENAI_API_KEY=your-api-key-here
OPENAI_BASE_URL=https://open.bigmodel.cn/api/paas/v4
LLM_MODEL=glm-4-flash
```

**支持的 LLM 提供商：**

| 提供商 | API 地址 | 示例模型 |
|--------|---------|---------|
| **OpenAI** | `https://api.openai.com/v1` | `gpt-4o`, `gpt-4o-mini` |
| **DeepSeek** | `https://api.deepseek.com/v1` | `deepseek-chat`（性价比极高） |
| **智谱 GLM** | `https://open.bigmodel.cn/api/paas/v4` | `glm-4-flash`（免费） |
| **通义千问** | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `qwen-turbo`, `qwen-plus` |
| **硅基流动** | `https://api.siliconflow.cn/v1` | 多种开源模型托管 |

### 3. 启动

```bash
python -m streamlit run app.py
```

访问 **http://localhost:8501** 🎉

> 首次启动后上传文档时，系统会自动下载嵌入模型（约 33MB），请耐心等待。

---

## 🎨 界面设计

### 设计系统

```
品牌色: #6C5CE7 (蓝紫色)
圆角:   12px (大) / 8px (小)
过渡:   all 0.2s ease
```

| 区域 | 样式 |
|------|------|
| **主背景** | `#F8F7FC` 柔和浅紫底色，降低视觉疲劳 |
| **侧边栏** | `#14142B` 深蓝紫面板，300px 固定宽度 |
| **聊天气泡** | 用户消息蓝紫渐变右对齐 / AI 回复白色左对齐 |
| **按钮/输入框** | 蓝紫品牌色 + 聚焦光晕 + 0.2s 平滑过渡 |
| **统计卡片** | 悬停顶部发光条 + 上浮效果 |
| **空状态** | 居中布局 + 格式标签 + 优雅留白 |

### 页面布局

```
┌─────────────────────────────────────────────────────────┐
│  📚 个人知识库问答系统 — 你的私人 AI 研究助手            │
├──────────────┬──────────────────────────────────────────┤
│  ┌────────┐  │                                          │
│  │ 📚     │  │  空状态 / 聊天对话区域                    │
│  │ 知识库  │  │                                          │
│  │ 管理    │  │  ┌──────────────────────────┐            │
│  ├────────┤  │  │ 用户消息气泡 (蓝紫右对齐)  │            │
│  │ [3]文档 │  │  └──────────────────────────┘            │
│  │ [27]段  │  │  ┌────────────────────────┐              │
│  ├── ✦ ── │  │  │ AI 回复气泡 (白色左对齐)  │            │
│  │ 上传文档│  │  └────────────────────────┘              │
│  │ 导入网页│  │                                          │
│  │ Footer │  │  ┌──────────────────────────────┐         │
│  └────────┘  │  │  💬 请输入你的问题...         │         │
│    300px     │  └──────────────────────────────┘         │
└──────────────┴──────────────────────────────────────────┘
```

---

## 📖 使用指南

### 1️⃣ 上传文档
1. 在左侧边栏「上传文档」区域，点击 **Browse files**
2. 选择 PDF / Markdown / TXT 文件（可多选）
3. 系统自动分块 → 向量化 → 构建索引
4. 成功后侧边栏统计卡片显示**文档源数**和**文本段数**

### 2️⃣ 导入网页
1. 在左侧边栏「导入网页」区域，输入网页 URL
2. 点击 **📥 导入网页** 按钮
3. 系统自动抓取、清理 HTML、分块并索引

### 3️⃣ 提问
- 在底部输入框输入问题，按 Enter 发送
- 系统基于知识库内容 + LLM 进行回答
- 用户消息**蓝紫气泡右对齐**，AI 回复**白色气泡左对齐**
- 支持多轮对话，保留最近 6 轮上下文

### 4️⃣ 管理知识库
- **清空知识库**：点击「🗑️ 清空知识库」按钮
- **增量合并**：多次上传文档会自动合并到同一索引，不重复丢失
- **查看统计**：侧边栏实时显示文档源数和文本段数

---

## 📁 项目结构

```
knowledge-qa/
├── app.py                          # Streamlit 主应用（UI + 对话 + 文件上传）
├── knowledge_qa/                   # 核心 RAG 模块
│   ├── __init__.py
│   ├── config.py                   # 配置加载（.env）+ API Key 校验
│   ├── loader.py                   # 文档加载器（PDF/MD/TXT/网页）
│   ├── splitter.py                 # 文本分块（RecursiveCharacterTextSplitter）
│   ├── vector_store.py             # FAISS 向量库（构建/保存/加载/合并）
│   └── qa_chain.py                 # LLM 封装 + Prompt 构建 + QAChat 对话类
├── data/                           # 测试文档目录
│   └── 测试文档-RAG知识库深度解析.md
├── .env                            # 运行时配置（不提交 Git）
├── .env.example                    # 配置模板
├── requirements.txt                # Python 依赖
├── pyproject.toml                  # 项目元数据
├── CLAUDE.md                       # AI 辅助开发指南
└── README.md                       # 本文件
```

> **FAISS 索引存储位置**：`~/.knowledge-qa-index/`（纯英文路径，避免 Windows 中文路径兼容问题）

---

## ⚙️ 配置说明

| 环境变量 | 默认值 | 说明 |
|---------|--------|------|
| `OPENAI_API_KEY` | *(必填)* | LLM API 密钥 |
| `OPENAI_BASE_URL` | `https://api.openai.com/v1` | OpenAI 兼容接口地址 |
| `LLM_MODEL` | `gpt-4o-mini` | 对话模型名称 |
| `SIMILARITY_THRESHOLD` | `0.5` | 相似度阈值 (0.0~1.0)，越低召回越多 |

---

## 🔒 安全注意事项

- ✅ **API Key 安全** — `.env` 已加入 `.gitignore`，不会被提交到 Git
- ✅ **FAISS 反序列化** — `allow_dangerous_deserialization=True` 已添加安全说明，索引由用户自己构建
- ✅ **配置验证不阻塞** — 缺少 API Key 时仅警告，不崩溃
- ⚠️ **建议**：生产环境使用 HTTPS + 认证保护 Streamlit 前端

---

## 🤔 常见问题

**Q: 如何切换 LLM 模型？**
> 修改 `.env` 中的 `OPENAI_BASE_URL` 和 `LLM_MODEL` 即可。重启应用后生效。

**Q: Embedding 模型可以更换吗？**
> 修改 `knowledge_qa/vector_store.py` 中 `get_embeddings()` 函数的 `model_name` 参数，然后重建索引。

**Q: 如何提高检索准确率？**
> 调低 `SIMILARITY_THRESHOLD`（如 0.3），让更多相关片段进入 LLM 上下文。或调整 `chunk_size` / `chunk_overlap`。

**Q: 模型下载慢？**
> 代码已内置 Hugging Face 镜像 `hf-mirror.com`。也可以通过 `export HF_ENDPOINT=https://hf-mirror.com` 加速。

**Q: 为什么没有 `setup.bat` / `start.bat`？**
> 本项目为纯 Python 脚本，直接使用 `pip install -r requirements.txt` + `streamlit run app.py` 即可。

---

## 📄 许可证

[MIT License](LICENSE)

---

<p align="center">
  <sub>Built with ❤️ — RAG Knowledge Base Q&A System</sub>
</p>
