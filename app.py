import streamlit as st
import feedparser
import google.generativeai as genai
import requests

# การตั้งค่าหน้าจอ
st.set_page_config(page_title="AI News Summarizer", page_icon="📰")

# ใส่ API Key ของ Gemini (แนะนำให้ตั้งใน Streamlit Secrets)
# แต่ถ้าจะทดสอบเร็วๆ สามารถใส่ตรงๆ หรือทำช่อง Input ได้
api_key = st.sidebar.text_input("ใส่ Gemini API Key", type="password")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    st.title("📰 ระบบสรุปข่าวอัจฉริยะ")
    
    # เลือกแหล่งข่าว (RSS Feed)
    source_url = st.text_input("ใส่ URL ของ RSS Feed ข่าว", "https://www.thairath.co.th/rss/news")

    if st.button("ดึงข่าวและสรุป"):
        with st.spinner('กำลังอ่านข่าวและวิเคราะห์...'):
            feed = feedparser.parse(source_url)
            
            for entry in feed.entries[:5]: # ดึงมา 5 ข่าวล่าสุด
                st.subheader(entry.title)
                
                # สั่งให้ Gemini สรุป
                prompt = f"สรุปข่าวนี้ให้สั้น กระชับ สำหรับโพสต์ลง Facebook พร้อมอีโมจิและแฮชแท็ก: \nหัวข้อ: {entry.title} \nเนื้อหา: {entry.summary}"
                response = model.generate_content(prompt)
                summary_text = response.text
                
                # แสดงเนื้อหาที่สรุป
                st.text_area("สรุปสำหรับโพสต์:", summary_text, height=150)
                
                # สร้างรูปภาพจำลองจากหัวข้อข่าว (ใช้ Pollinations AI)
                # แปลหัวข้อเป็นอังกฤษก่อนส่งไปเจนรูปจะสวยกว่า
                translate_prompt = f"Translate this news title to English for Image Generation prompt: {entry.title}"
                eng_title = model.generate_content(translate_prompt).text
                image_url = f"https://pollinations.ai/p/{eng_title.replace(' ', '_')}?width=1080&height=1080&nologo=true"
                
                st.image(image_url, caption="รูปประกอบที่ AI แนะนำ")
                
                # ปุ่มแชร์ (แบบ Manual)
                st.markdown(f"[🔗 เปิดลิงก์ข่าวต้นฉบับ]({entry.link})")
                st.divider()
else:
    st.warning("กรุณาใส่ Gemini API Key ในแถบด้านข้างเพื่อเริ่มต้นใช้งาน")
