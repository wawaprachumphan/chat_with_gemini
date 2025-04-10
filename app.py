import streamlit as st
import pandas as pd
import google.generativeai as genai

# --- CONFIG Gemini ---
genai.configure(api_key=st.secrets.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY"))

# --- สร้าง Gemini Model แบบ multimodal ---
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction='คุณคือผู้ช่วยที่สามารถวิเคราะห์ข้อมูลจากไฟล์ CSV ได้อย่างเข้าใจง่าย'
)

# --- PAGE CONFIG ---
st.set_page_config(page_title="CSV Chatbot (Gemini)", layout="centered")
st.title("🤖 CSV Chatbot (Gemini)")

# --- UPLOAD ---
uploaded_file = st.file_uploader("📁 อัปโหลดไฟล์ .CSV", type=["csv"])

if uploaded_file:
    st.success("✅ อัปโหลดไฟล์เรียบร้อย")
    df = pd.read_csv(uploaded_file)
    st.dataframe(df.head())

    # แปลงไฟล์อัปโหลดให้เป็น bytes (ใช้เป็น part ของ Gemini multimodal)
    file_bytes = uploaded_file.read()
    uploaded_file.seek(0)  # รีเซ็ต pointer กลับ (สำหรับ pandas อ่านด้านบน)

    # รับ prompt จากผู้ใช้
    user_prompt = st.chat_input("ถามอะไรก็ได้เกี่ยวกับข้อมูลในไฟล์นี้")

    # แสดงข้อความก่อนหน้า (chat history)
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if user_prompt:
        # แสดง prompt ผู้ใช้
        st.chat_message("user").markdown(user_prompt)
        st.session_state.chat_history.append({"role": "user", "content": user_prompt})

        # สร้าง Gemini multimodal content
        contents = [
            {
                "mime_type": "text/csv",
                "data": file_bytes
            },
            user_prompt
        ]

        try:
            response = model.generate_content(contents)
            reply = response.text
        except Exception as e:
            reply = f"❌ เกิดข้อผิดพลาด: {e}"

        # แสดงตอบกลับ
        st.chat_message("assistant").markdown(reply)
        st.session_state.chat_history.append({"role": "assistant", "content": reply})

else:
    st.info("กรุณาอัปโหลดไฟล์ .csv ก่อนเริ่มใช้งานแชทบอท")
