# 📚 Knowledge QA — 个人知识库问答系统

> 基于 **RAG (Retrieval-Augmented Generation)** 架构的本地知识库问答系统。上传文档后自动构建向量索引，通过语义检索 + LLM 实现智能问答。

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://python.org)
[![LangChain](https://img.shields.io/badge/LangChain-0.2-1C3C3C?logo=langchain)](https://langchain.com)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B?logo=streamlit)](https://streamlit.io)
[![FAISS](https://img.shields.io/badge/Vector-FAISS-00BFFF)](https://github.com/facebookresearch/faiss)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## ✨ 功能特性

| 功能 | 说明 |
|------|------|
| 📄 **多格式文档导入** | PDF / Markdown / TXT / 网页内容 |
| 🔍 **语义向量检索** | FAISS + FastEmbed (`BAAI/bge-small-zh-v1.5`) |
| 🤖 **多模型 LLM 支持** | OpenAI / DeepSeek / 智谱 GLM / Qwen / 任意 OpenAI 兼容接口 |
| 💬 **多轮对话** | 保留最近 6 轮上下文，支持深度追问 |
| ⚡ **流式输出** | LLM 回复逐块实时显示，打字光标效果 |
| 💾 **索引持久化** | FAISS 索引自动保存，重启不用重建 |
| 📊 **知识库统计** | 文档源数量、文本段数量实时显示 |
| 🎨 **精美 UI** | 渐变主题、暗色侧边栏、动画交互 |

---

## 🛠️ 技术栈

| 组件 | 选型 |
|------|------|
| **框架** | LangChain |
| **UI** | Streamlit |
| **向量库** | FAISS (Facebook AI Similarity Search) |
| **嵌入模型** | FastEmbed `BAAI/bge-small-zh-v1.5` |
| **文档分块** | RecursiveCharacterTextSplitter |
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
                    │ RecursiveCharTextSplit │
                    │  chunk_size=500     │
                    │  chunk_overlap=100  │
                    └─────────┬───────────┘
                              ▼
                    ┌─────────────────────┐
                    │  向量化嵌入 (Embed)  │
                    │ FastEmbed(bge-small) │
                    └─────────┬───────────┘
                              ▼
                    ┌─────────────────────┐
                    │  FAISS 向量索引      │
                    │  持久化到本地磁盘    │
                    └─────────┬───────────┘
                              │
    ┌──────────┐    ┌────────┴────────┐    ┌──────────┐
    │ 用户提问  │───▶│  语义检索 (k=4) │───▶│  LLM 回答 │
    │ 多轮对话  │    │  阈值过滤过滤     │    │  流式输出 │
    └──────────┘    └─────────────────┘    └──────────┘
```

---

## 🚀 快速开始

### 前置要求

- Python 3.10+
- Windows / macOS / Linux

### 1. 安装

```bash
# Windows — 一键安装
.\setup.bat

# 或手动安装
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
```

### 2. 配置

```bash
# 复制配置文件
cp .env.example .env

# 编辑 .env，填入你的 API Key
```

| 环境变量 | 默认值 | 说明 |
|---------|--------|------|
| `OPENAI_API_KEY` | *(必填)* | LLM API 密钥 |
| `OPENAI_BASE_URL` | `https://api.openai.com/v1` | OpenAI 兼容接口地址 |
| `LLM_MODEL` | `gpt-4o-mini` | 对话模型名称 |
| `SIMILARITY_THRESHOLD` | `0.5` | 相似度阈值 (0.0~1.0) |

> 💡 **模型兼容性**：支持任何 OpenAI 兼容接口。智谱 GLM 免费模型 `glm-4-flash` 可直接使用。

### 3. 启动

```bash
# Windows
.\start.bat

# 或手动启动
python -m streamlit run app.py --server.port 8501
```

访问 **http://localhost:8501** 🎉

---

## 📖 使用指南

### 上传文档
1. 在左侧边栏点击「上传文档」
2. 选择 PDF / Markdown / TXT 文件（可多选）
3. 等待自动分块、向量化、构建索引
4. 知识库统计卡片会显示文档源数和文本段数

### 导入网页
1. 在左侧边栏输入网页 URL
2. 点击「导入网页」按钮
3. 系统自动抓取、清理 HTML、分块并索引

### 提问
- 在底部输入框输入问题
- 系统基于知识库内容 + LLM 进行回答
- 支持多轮追问（保留最近 6 轮上下文）

### 管理知识库
- **清空知识库**：点击「🗑️ 清空知识库」按钮
- **查看统计**：侧边栏实时显示文档源数和文本段数

---

## 📁 项目结构

```
knowledge-qa/
├── app.py                          # Streamlit 主应用（UI + 对话 + 文件上传）
├── knowledge_qa/                   # 核心 RAG 模块
│   ├── config.py                   # 配置加载（.env）+ API Key 校验
│   ├── loader.py                   # 文档加载器（PDF/MD/TXT/网页）
│   ├── splitter.py                 # 文本分块（RecursiveCharacterTextSplitter）
│   ├── vector_store.py             # FAISS 向量库（构建/保存/加载/合并）
│   └── qa_chain.py                 # LLM 封装 + Prompt 构建 + QAChat 对话类
├── data/faiss_index/               # FAISS 索引持久化（自动生成，不提交 Git）
├── .env                            # 运行时配置（不提交 Git）
├── .env.example                    # 配置模板
├── pyproject.toml                  # 项目元数据
├── requirements.txt                # Python 依赖
├── setup.bat                       # Windows 一键安装脚本
├── start.bat                       # Windows 启动脚本
└── CLAUDE.md                       # AI 辅助开发指南
```

---

## 🔌 支持的 LLM 提供商

| 提供商 | API 地址 | 示例模型 |
|--------|---------|---------|
| **OpenAI** | `https://api.openai.com/v1` | `gpt-4o`, `gpt-4o-mini` |
| **DeepSeek** | `https://api.deepseek.com/v1` | `deepseek-chat` |
| **智谱 GLM** | `https://open.bigmodel.cn/api/paas/v4` | `glm-4-flash`（免费） |
| **通义千问** | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `qwen-turbo`, `qwen-plus` |
| **硅基流动** | `https://api.siliconflow.cn/v1` | `deepseek-ai/DeepSeek-V3` |
| **Moonshot** | `https://api.moonshot.cn/v1` | `moonshot-v1-8k` |

---

## 🔒 安全注意事项

- ✅ **API Key 安全** — `.env` 已加入 `.gitignore`，不会被提交到 Git
- ✅ **FAISS 反序列化** — `allow_dangerous_deserialization=True` 已添加安全说明
- ✅ **配置验证不阻塞** — 缺少 API Key 时仅警告，不崩溃
- ⚠️ **建议**：生产环境使用 HTTPS + 认证保护 Streamlit 前端

---

## 🤔 常见问题

**Q: 如何切换 LLM 模型？**
> 修改 `.env` 中的 `OPENAI_BASE_URL` 和 `LLM_MODEL` 即可。重启应用后生效。

**Q: Embedding 模型可以更换吗？**
> 目前硬编码为 `BAAI/bge-small-zh-v1.5`。如需更换，修改 `knowledge_qa/vector_store.py` 中的 `model_name` 参数后重建索引。

**Q: 如何提高检索准确率？**
> 调低 `SIMILARITY_THRESHOLD`（如 0.3），让更多相关片段进入 LLM 上下文。

**Q: 模型下载慢？**
> 已内置 Hugging Face 镜像 `hf-mirror.com`。也可以通过 `export HF_ENDPOINT=https://hf-mirror.com` 加速。

**Q: 为什么选 `allow_dangerous_deserialization=True`？**
> FAISS 本地索引使用 pickle 序列化。由于索引由用户自己构建（非外部来源），此设置安全可控。

---

## 📄 许可证

[MIT License](LICENSE)

---

<p align="center">
  <sub>Built with ❤️ — RAG Knowledge Base Q&A System</sub>
</p>
