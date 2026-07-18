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

# ── 统一设计系统 ──────────────────────────────────────────────
# 品牌色: 蓝紫色 #6C5CE7 | 圆角: 12px/8px | 过渡: 0.2s
st.markdown(
    """
    <style>
    /* ========== 字体 ========== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    * { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }

    /* ========== 设计变量 ========== */
    :root {
        --brand: #6C5CE7;
        --brand-hover: #5A4BD1;
        --brand-light: rgba(108, 92, 231, 0.10);
        --brand-glow: rgba(108, 92, 231, 0.18);
        --bg: #F8F7FC;
        --surface: #FFFFFF;
        --sidebar-bg: #1C1B2E;
        --sidebar-surface: rgba(255,255,255,0.05);
        --sidebar-border: rgba(255,255,255,0.07);
        --text: #1E1B4B;
        --text-secondary: #6B7280;
        --text-muted: #9CA3AF;
        --text-sidebar: #C8C6DD;
        --text-sidebar-muted: #7C7A99;
        --border: #E5E4EC;
        --radius-lg: 12px;
        --radius-sm: 8px;
        --shadow: 0 2px 8px rgba(108, 92, 231, 0.08);
        --shadow-lg: 0 8px 30px rgba(108, 92, 231, 0.12);
        --transition: all 0.2s ease;
    }

    /* ========== 全局 ========== */
    .stApp { background: var(--bg); }

    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #D1CFE0; border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: #B8B5CC; }

    /* ========== 顶部标题栏 ========== */
    .app-header {
        display: flex;
        align-items: baseline;
        gap: 14px;
        padding: 1.2rem 0 0.6rem 0;
        margin-bottom: 1.2rem;
        border-bottom: 1.5px solid var(--border);
    }
    .app-header h1 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 800 !important;
        font-size: 1.8rem !important;
        background: linear-gradient(135deg, #1E1B4B 0%, #6C5CE7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.02em;
        margin: 0 !important;
        padding: 0 !important;
        border: none !important;
    }
    .app-header .subtitle {
        color: var(--text-muted);
        font-size: 0.85rem;
        font-weight: 400;
        letter-spacing: 0.01em;
    }

    /* ========== 侧边栏 ========== */
    /* 侧边栏宽度 */
    section[data-testid="stSidebar"] {
        background: #14142B !important;
        border-right: 1px solid rgba(255,255,255,0.06) !important;
        min-width: 300px !important;
        max-width: 300px !important;
    }
    section[data-testid="stSidebar"] > div {
        background: #14142B !important;
        padding: 1rem 0.8rem 1rem 1rem !important;
    }
    /* 侧边栏内部内容区域 */
    section[data-testid="stSidebar"] > div > div {
        padding: 0 !important;
        gap: 0.2rem !important;
    }

    /* ── 侧边栏顶栏 ── */
    .sidebar-top {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 0 0.3rem 0.75rem 0.3rem;
        margin-bottom: 0.4rem;
        border-bottom: 1.5px solid rgba(255,255,255,0.06);
    }
    .sidebar-top-icon {
        width: 32px; height: 32px;
        background: linear-gradient(135deg, #6C5CE7, #A29BFE);
        border-radius: 8px;
        display: flex; align-items: center; justify-content: center;
        font-size: 1rem;
        flex-shrink: 0;
    }
    .sidebar-top-text {
        font-family: 'Inter', sans-serif !important;
        font-weight: 700;
        font-size: 0.95rem;
        color: #E8E7F0;
        letter-spacing: 0.01em;
        line-height: 1.3;
    }
    .sidebar-top-sub {
        font-size: 0.65rem;
        color: #6B6988;
        font-weight: 400;
        letter-spacing: 0.04em;
    }

    /* ── 侧边栏子标题 ── */
    section[data-testid="stSidebar"] .section-label {
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.72rem !important;
        color: #6F6D8F !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        padding: 0 0.3rem !important;
        margin: 0.1rem 0 0.35rem 0 !important;
    }

    /* ── 侧边栏文本 ── */
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] .st-emotion-cache-1v0mbdj {
        color: #C8C6DD !important;
    }

    /* ── 统计卡片 ── */
    .stats-container {
        display: flex;
        gap: 8px;
        padding: 0 0.3rem;
        margin: 0 0 0.6rem 0;
    }
    .stat-card {
        flex: 1;
        background: rgba(255,255,255,0.04);
        border-radius: 10px;
        padding: 14px 6px 12px 6px;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.06);
        transition: var(--transition);
        cursor: default;
        position: relative;
        overflow: hidden;
    }
    .stat-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(108,92,231,0.4), transparent);
        opacity: 0;
        transition: var(--transition);
    }
    .stat-card:hover::before { opacity: 1; }
    .stat-card:hover {
        background: rgba(255,255,255,0.07);
        border-color: rgba(108, 92, 231, 0.25);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.20);
    }
    .stat-card .stat-num {
        font-family: 'Inter', sans-serif !important;
        font-size: 1.7rem;
        font-weight: 800;
        background: linear-gradient(135deg, #A29BFE, #6C5CE7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1.2;
        letter-spacing: -0.03em;
    }
    .stat-card .stat-label {
        font-size: 0.62rem;
        color: #6F6D8F;
        margin-top: 3px;
        letter-spacing: 0.07em;
        text-transform: uppercase;
        font-weight: 500;
    }
    .stat-card-empty {
        background: rgba(255,255,255,0.03);
        border-radius: 10px;
        padding: 18px 12px;
        text-align: center;
        border: 1px dashed rgba(255,255,255,0.08);
        color: #6F6D8F;
        font-size: 0.78rem;
        margin: 0 0.3rem 0.6rem 0.3rem;
        transition: var(--transition);
    }
    .stat-card-empty:hover {
        border-color: rgba(108, 92, 231, 0.2);
        background: rgba(255,255,255,0.05);
    }

    /* ── 区隔装饰线 ── */
    .sidebar-divider {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 0.15rem 0.3rem;
        margin: 0.2rem 0 0.3rem 0;
        user-select: none;
    }
    .sidebar-divider-line {
        flex: 1;
        height: 1px;
        background: linear-gradient(90deg, rgba(255,255,255,0.06), rgba(255,255,255,0.12), rgba(255,255,255,0.06));
    }
    .sidebar-divider-dot {
        color: #4A4870;
        font-size: 0.45rem;
        opacity: 0.5;
    }

    /* ── 侧边栏按钮 ── */
    section[data-testid="stSidebar"] .stButton > button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.8rem !important;
        transition: var(--transition) !important;
        border: 1px solid rgba(255,255,255,0.07) !important;
        background: rgba(255,255,255,0.04) !important;
        color: #D8D6E6 !important;
        height: 2.35rem !important;
        letter-spacing: 0.01em;
        padding: 0 1rem !important;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(108, 92, 231, 0.16) !important;
        border-color: rgba(108, 92, 231, 0.35) !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 14px rgba(108, 92, 231, 0.15) !important;
    }
    section[data-testid="stSidebar"] .stButton > button[kind="secondary"] {
        background: rgba(255,255,255,0.03) !important;
        border-color: rgba(255,255,255,0.06) !important;
        color: #7C7A99 !important;
    }
    section[data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover {
        background: rgba(239, 68, 68, 0.10) !important;
        border-color: rgba(239, 68, 68, 0.20) !important;
        color: #E8A0A0 !important;
        box-shadow: none !important;
    }

    /* ── 侧边栏 info 提示框（模型下载） ── */
    section[data-testid="stSidebar"] .stAlert {
        background: rgba(108, 92, 231, 0.08) !important;
        border: 1px solid rgba(108, 92, 231, 0.15) !important;
        border-radius: 8px !important;
        color: #B8B5CC !important;
        font-size: 0.78rem !important;
        padding: 0.4rem 0.65rem !important;
        margin: 0 0.3rem 0.35rem 0.3rem !important;
    }
    section[data-testid="stSidebar"] .stAlert svg { fill: #8B7FEB !important; }

    /* ── 文件上传器 ── */
    /* 外层是 div，不是 section！ */
    [data-testid="stFileUploader"] {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        margin: 0 0.3rem !important;
    }
    /* 内部拖拽区 — 这才是白色背景的源头 */
    [data-testid="stFileUploader"] [data-testid="stFileUploaderDropzone"] {
        background: rgba(255,255,255,0.03) !important;
        background-color: rgba(255,255,255,0.03) !important;
        border: 1.5px dashed rgba(255,255,255,0.08) !important;
        border-radius: 8px !important;
        padding: 0.5rem !important;
        transition: var(--transition) !important;
    }
    [data-testid="stFileUploader"] [data-testid="stFileUploaderDropzone"]:hover {
        border-color: rgba(108, 92, 231, 0.30) !important;
        background: rgba(255,255,255,0.06) !important;
        background-color: rgba(255,255,255,0.06) !important;
    }
    /* 拖拽中覆盖层 */
    [data-testid="stFileUploader"] [data-testid="stFileUploaderDropzone"] > div {
        background: rgba(255,255,255,0.03) !important;
        background-color: rgba(255,255,255,0.03) !important;
    }
    /* 上传按钮 */
    [data-testid="stFileUploader"] button {
        background: rgba(108, 92, 231, 0.15) !important;
        color: #C8C6DD !important;
        border: 1px solid rgba(108, 92, 231, 0.20) !important;
        border-radius: 6px !important;
        font-size: 0.75rem !important;
        transition: var(--transition) !important;
    }
    [data-testid="stFileUploader"] button:hover {
        background: rgba(108, 92, 231, 0.28) !important;
    }
    /* 已上传文件列表 */
    [data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] {
        color: #C8C6DD !important;
        font-size: 0.75rem !important;
        background: transparent !important;
        background-color: transparent !important;
    }
    /* 提示文字 */
    [data-testid="stFileUploader"] [data-testid="stFileUploaderDropzoneInstructions"],
    [data-testid="stFileUploader"] [data-testid="stFileUploaderDropzoneInstructions"] span {
        color: #6F6D8F !important;
    }

    /* ── 侧边栏输入框 ── */
    section[data-testid="stSidebar"] .stTextInput,
    section[data-testid="stSidebar"] .stTextInput > div,
    section[data-testid="stSidebar"] .stTextInput > div > div,
    section[data-testid="stSidebar"] .stTextInput > div > div > div {
        background: transparent !important;
        background-color: transparent !important;
        padding: 0 !important;
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
    }
    section[data-testid="stSidebar"] .stTextInput > div > div > input {
        border-radius: 8px !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
        background: rgba(255,255,255,0.03) !important;
        color: #E2E0F0 !important;
        font-size: 0.82rem !important;
        transition: var(--transition) !important;
        height: 2.35rem !important;
        padding: 0 0.8rem !important;
        outline: none !important;
        box-shadow: none !important;
    }
    section[data-testid="stSidebar"] .stTextInput > div > div > input:focus {
        border-color: rgba(108, 92, 231, 0.45) !important;
        box-shadow: 0 0 0 3px rgba(108, 92, 231, 0.12) !important;
        background: rgba(255,255,255,0.05) !important;
    }
    section[data-testid="stSidebar"] .stTextInput > div > div > input::placeholder {
        color: #5A5878 !important;
    }

    /* ========== 主区域按钮 ========== */
    .stButton > button {
        border-radius: var(--radius-sm) !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        transition: var(--transition) !important;
        background: var(--brand) !important;
        color: white !important;
        border: none !important;
        height: 2.5rem !important;
    }
    .stButton > button:hover {
        background: var(--brand-hover) !important;
        box-shadow: 0 4px 12px var(--brand-glow) !important;
        transform: translateY(-1px);
    }

    /* ========== 主区域输入框 ========== */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: var(--radius-sm) !important;
        border: 1.5px solid var(--border) !important;
        background: var(--surface) !important;
        color: var(--text) !important;
        font-size: 0.9rem !important;
        transition: var(--transition) !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--brand) !important;
        box-shadow: 0 0 0 3px var(--brand-glow) !important;
    }
    .stTextInput > div > div > input::placeholder {
        color: var(--text-muted) !important;
    }

    /* ========== 聊天消息气泡 ========== */
    [data-testid="stChatMessage"] {
        border: none !important;
        background: transparent !important;
        padding: 0.25rem 0 !important;
        margin: 0 !important;
    }
    /* 用户气泡 - 右对齐蓝紫色 */
    [data-testid="stChatMessage"][aria-label="user"] .stChatMessageContent {
        background: linear-gradient(135deg, #6C5CE7, #5A4BD1) !important;
        color: #FFFFFF !important;
        border-radius: 18px 18px 4px 18px !important;
        padding: 12px 18px !important;
        box-shadow: 0 3px 12px rgba(108, 92, 231, 0.25) !important;
        margin-left: auto !important;
        max-width: 72% !important;
        margin-right: 0.5rem !important;
    }
    /* AI 气泡 - 左对齐白色 */
    [data-testid="stChatMessage"][aria-label="assistant"] .stChatMessageContent {
        background: var(--surface) !important;
        color: var(--text) !important;
        border-radius: 18px 18px 18px 4px !important;
        padding: 14px 20px !important;
        box-shadow: var(--shadow) !important;
        border: 1px solid var(--border) !important;
        max-width: 78% !important;
        margin-right: auto !important;
        margin-left: 0.5rem !important;
    }
    /* 消息文字排版 */
    [data-testid="stChatMessage"] .stChatMessageContent p {
        margin: 0 0 6px 0 !important;
        line-height: 1.65 !important;
        font-size: 0.92rem !important;
    }
    [data-testid="stChatMessage"] .stChatMessageContent p:last-child { margin-bottom: 0 !important; }
    /* 消息内代码 */
    [data-testid="stChatMessage"] .stChatMessageContent code {
        background: rgba(108, 92, 231, 0.10) !important;
        border-radius: 4px !important;
        padding: 1px 5px !important;
        font-size: 0.85em !important;
        color: #6C5CE7 !important;
    }
    [data-testid="stChatMessage"] .stChatMessageContent pre {
        background: #F1F0F7 !important;
        border-radius: var(--radius-sm) !important;
        padding: 12px !important;
        border: 1px solid var(--border) !important;
        margin: 8px 0 !important;
    }
    /* 头像微调 */
    [data-testid="stChatMessage"] [data-testid="chatAvatar"] {
        opacity: 0.7 !important;
        transform: scale(0.85) !important;
        transition: var(--transition) !important;
    }
    [data-testid="stChatMessage"]:hover [data-testid="chatAvatar"] {
        opacity: 1 !important;
    }

    /* ========== 聊天输入框 ========== */
    .stChatInputContainer {
        background: var(--surface) !important;
        border: 1.5px solid var(--border) !important;
        border-radius: 14px !important;
        padding: 3px !important;
        box-shadow: var(--shadow) !important;
        transition: var(--transition) !important;
        margin-top: 0.5rem !important;
    }
    .stChatInputContainer:focus-within {
        border-color: var(--brand) !important;
        box-shadow: 0 2px 16px var(--brand-glow) !important;
    }
    .stChatInputContainer input { font-size: 0.92rem !important; }
    .stChatInputContainer button {
        background: var(--brand) !important;
        color: white !important;
        border-radius: 10px !important;
        min-width: 2.4rem !important;
        height: 2.4rem !important;
        transition: var(--transition) !important;
    }
    .stChatInputContainer button:hover {
        background: var(--brand-hover) !important;
        transform: scale(1.05);
        box-shadow: 0 3px 10px rgba(108, 92, 231, 0.30) !important;
    }

    /* ========== 空状态 ========== */
    .empty-state {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        padding: 5rem 1.5rem 3rem 1.5rem;
        max-width: 420px;
        margin: 0 auto;
    }
    .empty-state-icon {
        font-size: 3.5rem;
        margin-bottom: 0.6rem;
        opacity: 0.7;
        line-height: 1;
    }
    .empty-state-title {
        font-family: 'Inter', sans-serif !important;
        font-weight: 700;
        font-size: 1.25rem;
        color: var(--text);
        margin: 0 0 0.5rem 0;
        line-height: 1.4;
    }
    .empty-state-desc {
        color: var(--text-secondary);
        font-size: 0.92rem;
        line-height: 1.7;
        margin: 0;
    }
    .empty-state-tags {
        margin-top: 1.2rem;
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        justify-content: center;
    }
    .empty-state-tags span {
        display: inline-block;
        background: rgba(108, 92, 231, 0.08);
        color: #6C5CE7;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 500;
        border: 1px solid rgba(108, 92, 231, 0.15);
    }

    /* ========== 通知消息 ========== */
    .stAlert {
        border-radius: var(--radius-sm) !important;
        border: none !important;
        font-size: 0.85rem !important;
        padding: 0.6rem 0.9rem !important;
    }
    .stAlert-success { background: rgba(16, 185, 129, 0.10) !important; color: #6EE7B7 !important; }
    .stAlert-error { background: rgba(239, 68, 68, 0.08) !important; color: #DC2626 !important; }
    .stAlert-warning { background: rgba(245, 158, 11, 0.10) !important; color: #D97706 !important; }
    .stAlert-info { background: rgba(108, 92, 231, 0.08) !important; color: #6C5CE7 !important; }

    /* ========== 模型下载提示 ========== */
    .model-hint {
        display: flex;
        align-items: center;
        gap: 6px;
        background: rgba(108, 92, 231, 0.10);
        border: 1px solid rgba(108, 92, 231, 0.20);
        border-radius: var(--radius-sm);
        padding: 0.45rem 0.75rem;
        margin: 0.2rem 0 0.5rem 0;
        font-size: 0.78rem;
        color: #C8C6DD;
        line-height: 1.4;
    }
    .model-hint-icon {
        font-size: 0.85rem;
        flex-shrink: 0;
    }
    .model-hint-dots {
        display: inline-flex;
        gap: 3px;
        margin-left: 2px;
    }
    .model-hint-dots span {
        width: 4px;
        height: 4px;
        background: #8B7FEB;
        border-radius: 50%;
        animation: hint-dot-pulse 1.4s ease-in-out infinite;
    }
    .model-hint-dots span:nth-child(2) { animation-delay: 0.2s; }
    .model-hint-dots span:nth-child(3) { animation-delay: 0.4s; }
    @keyframes hint-dot-pulse {
        0%, 80%, 100% { opacity: 0.3; transform: scale(0.8); }
        40% { opacity: 1; transform: scale(1.2); }
    }

    /* ========== toast ========== */
    .stToast {
        background: var(--sidebar-bg) !important;
        color: #E8E7F0 !important;
        border-radius: var(--radius-lg) !important;
        border: 1px solid rgba(108, 92, 231, 0.25) !important;
        font-size: 0.88rem !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25) !important;
        backdrop-filter: blur(12px) !important;
    }

    /* ========== 侧边栏 Footer ========== */
    .sidebar-footer {
        margin-top: 1.8rem;
        padding-top: 1rem;
        border-top: 1px solid var(--sidebar-border);
        text-align: center;
    }
    .sidebar-footer .brand {
        color: var(--text-sidebar-muted);
        font-size: 0.72rem;
        letter-spacing: 0.06em;
        font-weight: 500;
    }
    .sidebar-footer .brand-em {
        color: #8B7FEB;
        font-weight: 700;
    }
    .sidebar-footer .powered {
        color: rgba(255,255,255,0.25);
        font-size: 0.62rem;
        margin-top: 3px;
    }

    /* ========== spinner 加载 ========== */
    .stSpinner > div { border-color: var(--brand) !important; border-top-color: transparent !important; }
    .stSpinner p { color: var(--text-secondary) !important; font-size: 0.85rem !important; }

    /* ========== 打字光标 ========== */
    .typing-cursor::after {
        content: "▌";
        animation: cursor-blink 0.8s infinite;
        color: var(--brand);
        font-weight: 300;
    }
    @keyframes cursor-blink {
        0%, 50% { opacity: 1; }
        51%, 100% { opacity: 0; }
    }

    /* ========== 隐藏 Streamlit 品牌 ========== */
    footer, #MainMenu, .stDeployButton { display: none !important; }

    /* ========== 响应式 ========== */
    @media (max-width: 640px) {
        .app-header h1 { font-size: 1.4rem !important; }
        .app-header .subtitle { display: none; }
        [data-testid="stChatMessage"][aria-label="user"] .stChatMessageContent,
        [data-testid="stChatMessage"][aria-label="assistant"] .stChatMessageContent {
            max-width: 92% !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── 页面头部 ──
st.markdown(
    '<div class="app-header">'
    '<h1>📚 个人知识库问答系统</h1>'
    '<span class="subtitle">— 你的私人 AI 研究助手</span>'
    '</div>',
    unsafe_allow_html=True,
)

# 提前加载已有向量库，确保侧边栏能正确读取到统计
if "vector_store" not in st.session_state:
    vs = load_vector_store()
    if vs:
        st.session_state["vector_store"] = vs

# ----------------------------------------------------------------
# Sidebar: 知识库管理
# ----------------------------------------------------------------
with st.sidebar:
    # ── 顶栏 ──
    st.markdown(
        '<div class="sidebar-top">'
        '<div class="sidebar-top-icon">📚</div>'
        '<div>'
        '<div class="sidebar-top-text">知识库管理</div>'
        '<div class="sidebar-top-sub">Knowledge Base</div>'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    # ── 知识库统计 ──
    current_vs = st.session_state.get("vector_store")
    if current_vs:
        vs_size = current_vs.index.ntotal if hasattr(current_vs, 'index') else 0
        sources = set()
        try:
            for doc_id in current_vs.index_to_docstore_id.values():
                doc = current_vs.docstore._dict.get(doc_id)
                if doc and "source" in doc.metadata:
                    sources.add(doc.metadata["source"])
        except Exception:
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
            '<div class="stat-card-empty">📭 暂无内容，上传文档后自动统计</div>',
            unsafe_allow_html=True,
        )

    # ── 区隔线 ──
    st.markdown(
        '<div class="sidebar-divider">'
        '<span class="sidebar-divider-line"></span>'
        '<span class="sidebar-divider-dot">✦</span>'
        '<span class="sidebar-divider-line"></span>'
        '</div>',
        unsafe_allow_html=True,
    )

    # ── 清空知识库 ──
    if st.button("🗑️ 清空知识库", use_container_width=True, type="secondary"):
        if os.path.exists(VECTOR_STORE_PATH):
            try:
                shutil.rmtree(VECTOR_STORE_PATH)
            except Exception as e:
                st.error(f"清空失败: {e}")
        st.session_state.pop("vector_store", None)
        st.session_state.pop("qa_chain", None)
        st.session_state.pop("messages", None)
        st.rerun()

    # ── 区隔线 ──
    st.markdown(
        '<div class="sidebar-divider">'
        '<span class="sidebar-divider-line"></span>'
        '<span class="sidebar-divider-dot">✦</span>'
        '<span class="sidebar-divider-line"></span>'
        '</div>',
        unsafe_allow_html=True,
    )

    # ── 上传文档 ──
    st.markdown(
        '<div class="section-label">📄 上传文档</div>',
        unsafe_allow_html=True,
    )

    # 模型下载状态追踪
    if "model_ready" not in st.session_state:
        from knowledge_qa.vector_store import _embeddings
        st.session_state["model_ready"] = _embeddings is not None

    # 仅在首次需要下载模型时显示提示
    if not st.session_state["model_ready"]:
        st.markdown(
            '<div class="model-hint">'
            '<span class="model-hint-icon">💡</span>'
            '首次上传需下载模型，请稍候'
            '<span class="model-hint-dots">'
            '<span></span><span></span><span></span>'
            '</span>'
            '</div>',
            unsafe_allow_html=True,
        )

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
                # 修正：用原始文件名覆盖临时文件名
                for d in docs:
                    d.metadata["source"] = f.name
                all_docs.extend(docs)
                if docs:
                    st.success(f"✅ {f.name} 已加载")
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
            # 模型已就绪，后续不再显示下载提示
            st.session_state["model_ready"] = True
            n_chunks = vs.index.ntotal if hasattr(vs, 'index') else 0
            st.toast(f"🎉 成功导入 {n_chunks} 段文本！", icon="✅")

    # ── 区隔线 ──
    st.markdown(
        '<div class="sidebar-divider">'
        '<span class="sidebar-divider-line"></span>'
        '<span class="sidebar-divider-dot">✦</span>'
        '<span class="sidebar-divider-line"></span>'
        '</div>',
        unsafe_allow_html=True,
    )

    # ── 导入网页 ──
    st.markdown(
        '<div class="section-label">🌐 导入网页</div>',
        unsafe_allow_html=True,
    )
    url = st.text_input("网页链接", placeholder="https://example.com/article", label_visibility="collapsed", key="url_input")
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
            st.session_state["model_ready"] = True
            n_chunks = vs.index.ntotal if hasattr(vs, 'index') else 0
            st.session_state["url_input"] = ""  # 清空输入框
            st.toast(f"🌐 网页导入成功！({n_chunks} 段)", icon="✅")
        except Exception as e:
            st.error(f"❌ 网页加载失败: {e}")

    st.markdown(
        '<div class="sidebar-divider">'
        '<span class="sidebar-divider-line"></span>'
        '<span class="sidebar-divider-dot">✦</span>'
        '<span class="sidebar-divider-line"></span>'
        '</div>',
        unsafe_allow_html=True,
    )

    # ── Footer ──
    st.markdown(
        '<div class="sidebar-footer">'
        '<div class="brand">Knowledge QA <span class="brand-em">v1.2</span></div>'
        '<div class="powered">Powered by 智谱 AI · FAISS · LangChain</div>'
        '</div>',
        unsafe_allow_html=True,
    )

# ----------------------------------------------------------------
# 主界面：对话
# ----------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# 限制聊天历史最多 50 条（25 轮对话），防止内存无限增长
MAX_MESSAGES = 50
if len(st.session_state["messages"]) > MAX_MESSAGES:
    st.session_state["messages"] = st.session_state["messages"][-MAX_MESSAGES:]

# ── 空状态引导 ──
vs = st.session_state.get("vector_store")
messages = st.session_state["messages"]

if not vs:
    st.markdown(
        '<div class="empty-state">'
        '<div class="empty-state-icon">📖</div>'
        '<h2 class="empty-state-title">知识库尚未初始化</h2>'
        '<p class="empty-state-desc">在左侧边栏上传你的文档，<br>将知识转化为可对话的智慧。</p>'
        '<div class="empty-state-tags">'
        '<span>PDF</span> <span>Markdown</span> <span>TXT</span>'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )
elif not messages:
    st.markdown(
        '<div class="empty-state" style="padding:4rem 1.5rem 2.5rem 1.5rem;">'
        '<div class="empty-state-icon" style="font-size:3rem;">💬</div>'
        '<h2 class="empty-state-title">知识已就绪，等你发问</h2>'
        '<p class="empty-state-desc">在下方输入你的问题，我将基于知识库内容为你解答。</p>'
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
