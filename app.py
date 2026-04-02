import streamlit as st
import feedparser
from groq import Groq # เปลี่ยนจาก google.generativeai เป็น groq

# ตั้งค่าหน้าจอ
st.set_page_config(page_title="News to Image Prompt (Groq)", page_icon="🎨", layout="wide")

st.title("📰 ระบบสรุปข่าว & เจนชุดคำสั่งสร้างรูป (Powered by Groq)")
st.caption("ดึงข่าว สรุปเนื้อหา และสร้าง English Prompt สำหรับเอาไปเจนรูปเองด้วย Llama 3.3")

# ส่วนตั้งค่าใน Sidebar
with st.sidebar:
    st.header("⚙️ การตั้งค่า")
    # ดึง Key จาก Secrets หรือให้ User กรอกเอง
    default_api = st.secrets.get("GROQ_API_KEY", "")
    user_api = st.text_input("Groq API Key", value=default_api, type="password")
    
    st.divider()
    source_url = st.text_input("RSS Feed URL", "https://news.google.com/rss?hl=th&gl=TH&ceid=TH:th")
    num_news = st.slider("จำนวนข่าว", 1, 10, 5)

if user_api:
    try:
        # สร้าง Client สำหรับ Groq
        client = Groq(api_key=user_api)

        if st.button("🔄 ดึงข่าวและสร้างชุดคำสั่ง"):
            with st.spinner('กำลังวิเคราะห์ข่าวด้วย AI...'):
                feed = feedparser.parse(source_url)
                
                if not feed.entries:
                    st.warning("ไม่พบข่าวจาก URL ที่ระบุ")
                
                for entry in feed.entries[:num_news]:
                    # 1. สั่งสรุปเนื้อหาข่าวสำหรับ Facebook
                    s_completion = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {"role": "system", "content": "สรุปข่าวสั้นๆ สำหรับโพสต์ Facebook พร้อมอีโมจิและ Hashtag"},
                            {"role": "user", "content": f"ข่าว: {entry.title}"}
                        ]
                    )
                    summary_text = s_completion.choices[0].message.content
                    
                    # 2. สั่งสร้าง Prompt ภาษาอังกฤษสำหรับเจนรูป
                    i_completion = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {"role": "system", "content": "You are a professional image prompt engineer."},
                            {"role": "user", "content": f"Create a detailed, 1-sentence English cinematic photo prompt based on this news title: '{entry.title}'. Focus on lighting, mood, and high-quality details. No quotes."}
                        ]
                    )
                    image_prompt_eng = i_completion.choices[0].message.content.strip()

                    # --- แสดงผล ---
                    with st.container():
                        st.subheader(f"📌 {entry.title}")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("📝 **ข้อความสำหรับโพสต์ Facebook:**")
                            st.code(summary_text, language="text")
                        
                        with col2:
                            st.markdown("🎨 **ชุดคำสั่งสร้างรูป (English Prompt):**")
                            st.code(image_prompt_eng, language="text")
                        
                        st.markdown(f"[🔗 ลิงก์ข่าวต้นฉบับ]({entry.link})")
                        st.divider()
                        
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาด: {e}")
else:
    st.info("👈 กรุณาใส่ Groq API Key ที่แถบด้านข้าง (สมัครฟรีที่ console.groq.com)")
