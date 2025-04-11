import streamlit as st
import pandas as pd
import google.generativeai as genai

# 1. ตั้งค่า Gemini API
genai.configure(api_key=st.secrets.get("GEMINI_API_KEY", "your-gemini-key"))

# 2. โหลด Model
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    system_instruction="คุณคือผู้ช่วยวิเคราะห์ข้อมูล CSV ที่เก่งมาก พูดจาชัดเจน กระชับ และมีเหตุผล"
)

# 3. Session state
if "chat" not in st.session_state:
    st.session_state.chat = None
if "df_summary" not in st.session_state:
    st.session_state.df_summary = ""
if "chat_log" not in st.session_state:
    st.session_state.chat_log = []

# 4. UI
st.set_page_config(page_title="CSV Gemini Chatbot", layout="centered")
st.title("🤖 QueryTalker")

# 5. Upload CSV
uploaded_file = st.file_uploader("📁 อัปโหลดไฟล์ .csv", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("👀 ตัวอย่างข้อมูล:")
    st.dataframe(df.head())

    # แปลง DataFrame เป็นข้อความแบบย่อส่งให้โมเดล
    summary_text = f"""
นี่คือตัวอย่างข้อมูลจากไฟล์ CSV ที่ผู้ใช้อัปโหลด:
- จำนวนแถว: {df.shape[0]} แถว
- จำนวนคอลัมน์: {df.shape[1]} คอลัมน์
- ชื่อคอลัมน์: {', '.join(df.columns)}
- ตัวอย่าง 5 แถวแรก:
{df.head().to_string(index=False)}
"""
    st.session_state.df_summary = summary_text

    # สร้าง session แชท
    st.session_state.chat = model.start_chat(
        history=[
            {"role": "user", "parts": [summary_text]},
            {"role": "model", "parts": ["เข้าใจข้อมูลแล้วค่ะ คุณสามารถถามอะไรเกี่ยวกับไฟล์นี้ได้เลย 🙂"]}
        ]
    )
    st.success("✅ พร้อมเริ่มสนทนาแล้ว")

# 6. แสดงประวัติแชท
for msg in st.session_state.chat_log:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 7. แชท
if st.session_state.chat:
    prompt = st.chat_input("พิมพ์คำถามเกี่ยวกับไฟล์ CSV ได้เลย...")
    if prompt:
        st.chat_message("user").markdown(prompt)
        st.session_state.chat_log.append({"role": "user", "content": prompt})

        try:
            response = st.session_state.chat.send_message(prompt)
            st.chat_message("assistant").markdown(response.text)
            st.session_state.chat_log.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"❌ เกิดข้อผิดพลาด: {e}")
