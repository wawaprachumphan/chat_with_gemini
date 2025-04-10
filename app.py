import streamlit as st
import pandas as pd
import openai

# ====== SETUP ======
st.set_page_config(page_title="CSV Chatbot 🤖", layout="wide")
st.title("🤖 CSV Chatbot")
openai.api_key = st.secrets.get("OPENAI_API_KEY", "sk-...")  # เปลี่ยนเป็น API จริงหรือใช้ st.secrets

# ====== SESSION STATE ======
if "df" not in st.session_state:
    st.session_state.df = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ====== FILE UPLOAD ======
uploaded_file = st.file_uploader("📁 อัปโหลดไฟล์ CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.session_state.df = df
    st.write("🧾 ตัวอย่างข้อมูล:")
    st.dataframe(df.head())

# ====== CHAT INTERFACE ======
if st.session_state.df is not None:
    user_input = st.chat_input("💬 ถามคำถามเกี่ยวกับข้อมูลนี้...")

    # แสดงประวัติการสนทนา
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if user_input:
        # --- แสดงข้อความผู้ใช้
        st.chat_message("user").markdown(user_input)
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        # --- สร้าง context
        context_text = st.session_state.df.head(10).to_csv(index=False)

        # --- เตรียมข้อความทั้งหมด
        messages = [
            {"role": "system", "content": "คุณคือผู้ช่วยอัจฉริยะที่ตอบคำถามเกี่ยวกับข้อมูล CSV ที่อัปโหลดเข้ามา"},
            {"role": "system", "content": f"นี่คือตัวอย่างข้อมูลจาก CSV:\n{context_text}"},
        ] + st.session_state.chat_history

        # --- เรียก GPT
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.4
        )

        assistant_reply = response["choices"][0]["message"]["content"]
        st.session_state.chat_history.append({"role": "assistant", "content": assistant_reply})

        # --- แสดงข้อความผู้ช่วย
        st.chat_message("assistant").markdown(assistant_reply)

else:
    st.info("กรุณาอัปโหลดไฟล์ CSV ก่อนเริ่มสนทนา")
