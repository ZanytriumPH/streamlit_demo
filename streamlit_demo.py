import json
import streamlit as st
import os
from openai import OpenAI
from datetime import datetime


# 页面配置 st.title() 等元素之前调用
st.set_page_config(
    page_title = "Giweue",        # 页面标题（浏览器标签显示）
    page_icon = "icon.png",       # 页面图标（可以是 emoji 或图片路径）
    layout = "wide",              # 页面布局："centered" 或 "wide"
    initial_sidebar_state = "expanded", # 侧边栏状态："expanded", "collapsed", "auto"
    menu_items = None,            # 菜单项配置
)

def save_session():
    """保存当前会话数据"""
    if st.session_state.current_session:
        session_data = {
            "system_prompt": st.session_state.system_prompt,
            "temperature": st.session_state.temperature,
            "max_tokens": st.session_state.max_tokens,
            "top_p": st.session_state.top_p,
            "frequency_penalty": st.session_state.frequency_penalty,
            "presence_penalty": st.session_state.presence_penalty,
            "messages": st.session_state.messages,
        }

        if not os.path.exists("sessions"):
            os.mkdir("sessions")
        # json 操作
        with open(f"sessions/{st.session_state.current_session}.json", "w", encoding="utf-8") as f:
            json.dump(session_data, f, ensure_ascii=False, indent=4)

def load_sessions():
    """加载所有会话"""
    sessions = []
    if os.path.exists("sessions"):
        for filename in os.listdir("sessions"):
            if filename.endswith(".json"):
                sessions.append(filename[:-5]) # 去掉 .json 后缀
    sessions.sort(reverse=True)
    return sessions

def load_session(session_name):
    """加载指定会话"""
    try:
        if os.path.exists(f"sessions/{session_name}.json"):
            with open(f"sessions/{session_name}.json", "r", encoding="utf-8") as f:
                session_data = json.load(f)
                st.session_state.system_prompt = session_data["system_prompt"]
                st.session_state.temperature = session_data["temperature"]
                st.session_state.max_tokens = session_data["max_tokens"]
                st.session_state.top_p = session_data["top_p"]
                st.session_state.frequency_penalty = session_data["frequency_penalty"]
                st.session_state.presence_penalty = session_data["presence_penalty"]
                st.session_state.messages = session_data["messages"]
                st.session_state.current_session = session_name
    except Exception as e:
        st.error(f"加载会话失败：{e}")

# 定义默认参数
DEFAULT_SYSTEM_PROMPT = ""
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 1024
DEFAULT_TOP_P = 1.0
DEFAULT_FREQUENCY_PENALTY = 0.0
DEFAULT_PRESENCE_PENALTY = 0.0

def init_session_state():
    """初始化或重置会话状态为默认值"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "system_prompt" not in st.session_state:
        st.session_state.system_prompt = DEFAULT_SYSTEM_PROMPT
    if "temperature" not in st.session_state:
        st.session_state.temperature = DEFAULT_TEMPERATURE
    if "max_tokens" not in st.session_state:
        st.session_state.max_tokens = DEFAULT_MAX_TOKENS
    if "top_p" not in st.session_state:
        st.session_state.top_p = DEFAULT_TOP_P
    if "frequency_penalty" not in st.session_state:
        st.session_state.frequency_penalty = DEFAULT_FREQUENCY_PENALTY
    if "presence_penalty" not in st.session_state:
        st.session_state.presence_penalty = DEFAULT_PRESENCE_PENALTY
    if "current_session" not in st.session_state:
        st.session_state.current_session = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def reset_session():
    """重置所有会话状态为默认值（用于新建会话）"""
    st.session_state.messages = []
    st.session_state.system_prompt = DEFAULT_SYSTEM_PROMPT
    st.session_state.temperature = DEFAULT_TEMPERATURE
    st.session_state.max_tokens = DEFAULT_MAX_TOKENS
    st.session_state.top_p = DEFAULT_TOP_P
    st.session_state.frequency_penalty = DEFAULT_FREQUENCY_PENALTY
    st.session_state.presence_penalty = DEFAULT_PRESENCE_PENALTY
    st.session_state.current_session = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def delete_session(session_name):
    """删除指定会话"""
    try:
        if os.path.exists(f"sessions/{session_name}.json"):
            os.remove(f"sessions/{session_name}.json")
            if st.session_state.current_session == session_name:
                reset_session()
    except Exception as e:
        st.error(f"删除会话失败：{e}")

# -------------------------------------------------------------------------------------------------------

st.title("Giweue")
st.logo("./icon.png")

init_session_state()

for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message["content"])

client = OpenAI(api_key = os.getenv("DASHSCOPE_API_KEY"),
                base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1",
                timeout=60)

# 侧边栏
with st.sidebar:
    # 新建会话
    if st.button("新建会话", width="stretch"):
        # 保存当前会话数据
        if st.session_state.messages:
            save_session()
        # 创建新会话，重置所有参数为默认值
        reset_session()
        # save_session()
        st.rerun()

    # 历史会话
    st.subheader("历史会话")
    sessions_list = load_sessions()
    for session in sessions_list:
        col1, col2 = st.columns([4,1])
        with col1:
            if st.button(session, width="stretch", icon="📄", key=f"load_{session}", type=st.session_state.current_session == session and "primary" or "secondary"):
                load_session(session)
                st.rerun()
        with col2:
            if st.button("", width="stretch", icon="❌", key=f"del_{session}"):
                delete_session(session)
                st.rerun()

    st.divider()

    st.subheader("参数设置")
    system_prompt = st.text_area("系统提示词", st.session_state.system_prompt, height=100)
    st.session_state.system_prompt = system_prompt
    temperature = st.slider("温度", 0.0, 1.0, st.session_state.temperature, step = 0.01)
    st.session_state.temperature = temperature
    max_tokens = st.slider("最大生成长度", 0, 2048, st.session_state.max_tokens)
    st.session_state.max_tokens = max_tokens
    top_p = st.slider("Top P", 0.0, 1.0, st.session_state.top_p, step = 0.01)
    st.session_state.top_p = top_p
    frequency_penalty = st.slider("频率惩罚", 0.0, 1.0, st.session_state.frequency_penalty, step = 0.01)
    st.session_state.frequency_penalty = frequency_penalty
    presence_penalty = st.slider("存在惩罚", 0.0, 1.0, st.session_state.presence_penalty, step = 0.01)
    st.session_state.presence_penalty = presence_penalty

# 消息输入框
prompt = st.chat_input("请输入问题")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        response_placeholder = st.empty() # 占位符，后续更新内容
        response_placeholder.write("浅度思考中...")
        full_response = "" # 用于存储完整响应

        response = client.chat.completions.create(
            model = "qwen2.5-7b-instruct",
            messages = [
                {"role": "system", "content": system_prompt},
                *st.session_state.messages, # 会话记忆
            ],
            stream = True,
            temperature = temperature,
            max_tokens = max_tokens,
            top_p = top_p,
            frequency_penalty = frequency_penalty,
            presence_penalty = presence_penalty,
        )
        # print(*st.session_state.messages)

        for chunk in response:
            full_response += chunk.choices[0].delta.content
            response_placeholder.write(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
    save_session() # 大模型响应完成后保存会话数据
    st.rerun()