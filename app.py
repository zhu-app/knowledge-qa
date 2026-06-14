import os
import sys
import shutil
import tempfile

import streamlit as st

sys.path.insert(0, os.path.dirname(__file__))

from knowledge_qa.loader import load_file, load_webpage
from knowledge_qa.vector_store import build_vector_store, save_vector_store, load_vector_store, merge_vector_stores, VECTOR_STORE_PATH
from knowledge_qa.qa_chain import QAChat

st.set_page_config(page_title="知识库问答系统", page_icon="📚", layout="wide")

# ── 自定义主题样式 ──────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* ========== 全局背景 ========== */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%);
    }

    /* ========== 主标题 ========== */
    .stApp > div:first-child > div > div > h1 {
        background: linear-gradient(90deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        margin-bottom: 0.2em !important;
    }

    /* ========== 侧边栏 ========== */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    }
    section[data-testid="stSidebar"] .st-emotion-cache-1v0mbdj {
        color: #e0e0e0;
    }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] h4,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] span {
        color: #e0e0e0 !important;
    }
    section[data-testid="stSidebar"] .stText {
        color: #ccc !important;
    }

    /* ========== 侧边栏按钮 ========== */
    section[data-testid="stSidebar"] .stButton > button {
        border-radius: 12px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
    }

    /* ========== 主区域按钮 ========== */
    .stButton > button {
        border-radius: 12px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }

    /* ========== 输入框 ========== */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 10px !important;
        border-color: #d0d7de !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2) !important;
    }

    /* ========== 分隔线 ========== */
    hr {
        border-color: #4a5568 !important;
    }

    /* ========== 聊天消息气泡 ========== */
    .stChatMessage {
        border-radius: 12px !important;
        transition: all 0.3s ease !important;
    }
    .stChatMessage > div {
        padding: 12px 16px !important;
    }

    /* ========== 统计卡片（自定义） ========== */
    .stats-container {
        display: flex;
        gap: 10px;
        margin-bottom: 8px;
    }
    .stat-card {
        flex: 1;
        background: rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 12px 8px;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.1);
    }
    .stat-card .stat-num {
        font-size: 1.6em;
        font-weight: 800;
        background: linear-gradient(90deg, #667eea, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1.2;
    }
    .stat-card .stat-label {
        font-size: 0.75em;
        color: #aaa;
        margin-top: 2px;
    }

    /* ========== 隐藏侧边栏底部链接 ========== */
    footer { visibility: hidden !important; }

    /* ========== 加载动画光标 ========== */
    .typing-cursor::after {
        content: "▌";
        animation: blink 0.8s infinite;
        color: #667eea;
    }
    @keyframes blink {
        0%, 50% { opacity: 1; }
        51%, 100% { opacity: 0; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📚 个人知识库问答系统")

# ----------------------------------------------------------------
# Sidebar: 知识库管理
# ----------------------------------------------------------------
with st.sidebar:
    st.header("🗂️ 知识库管理")

    # ── 知识库统计 ──
    current_vs = st.session_state.get("vector_store")
    if current_vs:
        vs_size = current_vs.index.ntotal if hasattr(current_vs, 'index') else 0
        # 统计不同来源
        sources = set()
        try:
            for doc_id in current_vs.index_to_docstore_id.values():
                doc = current_vs.docstore._dict.get(doc_id)
                if doc and "source" in doc.metadata:
                    sources.add(doc.metadata["source"])
        except:
            pass
        n_sources = max(len(sources), 1)

        st.markdown(
            '<div class="stats-container">'
            '<div class="stat-card"><div class="stat-num">{sources}</div><div class="stat-label">文档源</div></div>'
            '<div class="stat-card"><div class="stat-num">{chunks}</div><div class="stat-label">文本段</div></div>'
            '</div>'.format(sources=n_sources, chunks=vs_size),
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="stat-card" style="margin-bottom:8px;padding:16px 8px;">'
            '<div style="color:#888;font-size:0.85em;text-align:center;">知识库为空，请上传文档</div>'
            '</div>',
            unsafe_allow_html=True,
        )

    st.divider()

    # ── 清空知识库 ──
    if st.button("🗑️ 清空知识库", use_container_width=True, type="secondary"):
        if os.path.exists(VECTOR_STORE_PATH):
            shutil.rmtree(VECTOR_STORE_PATH)
        st.session_state.pop("vector_store", None)
        st.session_state.pop("qa_chain", None)
        st.session_state.pop("messages", None)
        st.rerun()

    st.divider()

    # ── 上传文档 ──
    st.subheader("📄 上传文档")
    st.info("💡 首次上传时会下载嵌入模型（约 100MB），请耐心等待。")
    uploaded_files = st.file_uploader(
        "支持 PDF / Markdown / TXT",
        type=["pdf", "md", "txt"],
        accept_multiple_files=True,
    )

    if uploaded_files:
        all_docs = []
        for f in uploaded_files:
            suffix = os.path.splitext(f.name)[1].lower()
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(f.read())
                tmp_path = tmp.name
            try:
                docs = load_file(tmp_path)
                if not docs:
                    st.warning(f"⚠️ {f.name} 未提取到文本内容（可能是图片型 PDF）")
                all_docs.extend(docs)
                if docs:
                    st.success(f"✅ {f.name} 已加载 ({len(docs)} 段)")
            except Exception as e:
                st.error(f"❌ {f.name} 加载失败: {e}")
            finally:
                os.unlink(tmp_path)

        if all_docs:
            with st.spinner("🔍 正在构建向量索引..."):
                vs = build_vector_store(all_docs)
                old_vs = load_vector_store()
                if old_vs:
                    vs = merge_vector_stores(old_vs, vs)
                save_vector_store(vs)
                st.session_state["vector_store"] = vs
                st.session_state.pop("qa_chain", None)
            st.toast(f"🎉 成功导入 {len(all_docs)} 段文本！", icon="✅")

    st.divider()

    # ── 导入网页 ──
    st.subheader("🌐 导入网页")
    url = st.text_input("输入网页 URL", placeholder="https://example.com/article")
    import_btn = st.button("📥 导入网页", use_container_width=True)
    if import_btn and url:
        try:
            with st.spinner("🌍 正在获取网页内容..."):
                docs = load_webpage(url)
            with st.spinner("🔍 正在构建向量索引..."):
                vs = build_vector_store(docs)
                old_vs = load_vector_store()
                if old_vs:
                    vs = merge_vector_stores(old_vs, vs)
                save_vector_store(vs)
                st.session_state["vector_store"] = vs
                st.session_state.pop("qa_chain", None)
            st.success(f"✅ 网页已加载 ({len(docs)} 段)")
            st.toast(f"🎉 网页导入成功！({len(docs)} 段)", icon="🌐")
        except Exception as e:
            st.error(f"❌ 网页加载失败: {e}")

    st.divider()

    # ── Footer ──
    st.markdown(
        '<div style="margin-top:20px;text-align:center;">'
        '<span style="color:#666;font-size:0.75em;">Knowledge QA v1.1</span><br>'
        '<span style="color:#555;font-size:0.7em;">Powered by 智谱 AI + FAISS</span>'
        '</div>',
        unsafe_allow_html=True,
    )

# ----------------------------------------------------------------
# 主界面：对话
# ----------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# 加载已有向量库
if "vector_store" not in st.session_state:
    vs = load_vector_store()
    if vs:
        st.session_state["vector_store"] = vs

# ── 空状态引导 ──
vs = st.session_state.get("vector_store")
messages = st.session_state["messages"]

if not vs:
    st.markdown(
        '<div style="text-align:center;padding:80px 20px 40px;">'
        '<div style="font-size:4em;margin-bottom:20px;">📭</div>'
        '<h2 style="color:#999;margin:0 0 10px;">知识库尚未初始化</h2>'
        '<p style="color:#aaa;font-size:1.05em;">请先在左侧边栏上传 PDF / Markdown / TXT 文档，或导入网页内容</p>'
        '<p style="color:#bbb;font-size:0.9em;margin-top:20px;">支持的文件格式：.pdf &nbsp; .md &nbsp; .txt</p>'
        '</div>',
        unsafe_allow_html=True,
    )
elif not messages:
    st.markdown(
        '<div style="text-align:center;padding:60px 20px 30px;">'
        '<div style="font-size:3.5em;margin-bottom:16px;">💬</div>'
        '<h2 style="color:#888;margin:0 0 8px;">知识已就绪</h2>'
        '<p style="color:#999;font-size:1em;">在下方输入你的问题，我将基于知识库内容为你解答</p>'
        '</div>',
        unsafe_allow_html=True,
    )

# ── 显示聊天历史 ──
for msg in messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── 用户输入与回复 ──
if prompt := st.chat_input("💬 请输入你的问题..."):
    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    vs = st.session_state.get("vector_store")
    if not vs:
        with st.chat_message("assistant"):
            st.markdown("⚠️ 知识库为空，请先在左侧上传文档或导入网页。")
        st.stop()

    if "qa_chain" not in st.session_state:
        st.session_state["qa_chain"] = QAChat(vs)

    qa = st.session_state["qa_chain"]

    with st.chat_message("assistant"):
        try:
            hist = st.session_state["messages"][:-1]
            response_container = st.empty()
            full_response = ""
            # 流式输出，带打字光标效果
            for chunk in qa.stream(prompt, history=hist):
                full_response += chunk
                response_container.markdown(full_response + "▌", unsafe_allow_html=True)
            response_container.markdown(full_response)
            st.session_state["messages"].append({"role": "assistant", "content": full_response})
        except Exception as e:
            err_msg = f"⚠️ 请求失败: {e}"
            st.error(err_msg)
            # 不将错误信息加入对话历史，避免污染后续上下文
