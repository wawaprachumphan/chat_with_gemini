import streamlit as st
import pandas as pd
import openai

# CONFIG
st.set_page_config(page_title="CSV Chatbot 🤖", layout="centered")
st.title("🤖 CSV Chatbot")

# API Key (ใส่ใน secrets หรือตรงนี้ก็ได้)
openai.api_key = st.secrets.get("OPENAI_API_KEY", "sk-...")

# SESSION STATE
if "messages" not in st.session_state:
    st.session_state.messages = []

if "df" not in st.session_state:
    st.session_state.df = None
    st.session_state.file_name = None

# UPLOAD CSV
uploaded_file = st.sidebar.file_uploader("📁 อัปโหลดไฟล์ CSV", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.session_state.df = df
    st.session_state.file_name = uploaded_file.name
    st.sidebar.success(f"✅ อัปโหลด: {uploaded_file.name}")

# DISPLAY PREVIEW
if st.session_state.df is not None:
    with st.expander("👀 ดูข้อมูลตัวอย่าง"):
        st.dataframe(st.session_state.df.head())

# CHAT
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("พิมพ์คำถามเกี่ยวกับข้อมูล CSV...")

if user_input:
    # แสดงข้อความของผู้ใช้
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # สร้าง context จาก CSV
    df_sample = st.session_state.df.head(20).to_csv(index=False) if st.session_state.df is not None else "ไม่มีข้อมูล CSV"
    file_info = f"ชื่อไฟล์: {st.session_state.file_name}" if st.session_state.file_name else ""

    system_prompt = f"""
คุณเป็นผู้ช่วยอัจฉริยะที่สามารถเข้าใจข้อมูลจากไฟล์ CSV และตอบคำถามของผู้ใช้ได้อย่างแม่นยำ

ข้อมูล CSV (ตัวอย่าง 20 แถวแรก):
{file_info}
{df_sample}
"""

    # สร้างข้อความที่ส่งให้ GPT
    messages = [
        {"role": "system", "content": system_prompt},
        *st.session_state.messages
    ]

    # เรียก OpenAI GPT
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.4,
    )

    bot_reply = response["choices"][0]["message"]["content"]

    # แสดงข้อความบอท
    st.chat_message("assistant").markdown(bot_reply)
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
