import streamlit as st
import pandas as pd
import google.generativeai as genai

# ตั้งค่า API Key
genai.configure(api_key=st.secrets.get("GEMINI_API_KEY", "your-gemini-key"))

# สร้าง Gemini model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction="คุณคือผู้ช่วยวิเคราะห์ข้อมูล CSV อย่างละเอียด พูดสุภาพและเข้าใจง่าย"
)

# สร้าง session chat ครั้งเดียว
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

# โหลดไฟล์ CSV
st.set_page_config(page_title="CSV Gemini Chatbot 🤖", layout="centered")
st.title("📊 Chatbot คุยกับไฟล์ CSV (Gemini)")

uploaded_file = st.sidebar.file_uploader("📁 อัปโหลดไฟล์ CSV", type=["csv"])
if uploaded_file:
    # อ่าน DataFrame และโชว์ตัวอย่าง
    df = pd.read_csv(uploaded_file)
    st.session_state.df = df
    st.sidebar.success("✅ ไฟล์โหลดสำเร็จ")
    st.dataframe(df.head())

    # แปลงไฟล์เป็น binary (สำหรับแนบกับ prompt)
    file_data = uploaded_file.read()
    csv_file_for_gemini = {
        "mime_type": "text/csv",
        "data": file_data
    }

    # รับข้อความจากผู้ใช้
    prompt = st.chat_input("ถามคำถามเกี่ยวกับข้อมูลนี้...")

    # แสดงประวัติการสนทนา
    for msg in st.session_state.chat_session.history:
        with st.chat_message(msg.role):
            st.markdown(msg.parts[0].text if hasattr(msg.parts[0], "text") else str(msg.parts[0]))

    if prompt:
        # แสดงข้อความผู้ใช้
        st.chat_message("user").markdown(prompt)

        # ส่ง prompt + CSV ให้ Gemini
        try:
            response = st.session_state.chat_session.send_message(
                [csv_file_for_gemini, prompt]
            )
            with st.chat_message("assistant"):
                st.markdown(response.text)

        except Exception as e:
            st.error(f"❌ เกิดข้อผิดพลาด: {e}")
else:
    st.info("กรุณาอัปโหลดไฟล์ .csv ก่อนเริ่มสนทนา")
