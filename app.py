import streamlit as st
import feedparser
import requests
from bs4 import BeautifulSoup
from groq import Groq

# ตั้งค่าหน้าจอ
st.set_page_config(page_title="Thairath Deep Analysis", page_icon="📰", layout="wide")

st.title("📰 ระบบดึงข่าวไทยรัฐเชิงลึก (Full Content)")
st.caption("ดึง RSS ไทยรัฐ และเข้าอ่านเนื้อหาเต็มจากหน้าเว็บเพื่อสรุปด้วย Groq")

# --- ฟังก์ชันดึงเนื้อหาเต็มจากลิงก์ไทยรัฐ ---
def get_full_article(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # ไทยรัฐมักเก็บเนื้อหาหลักไว้ในคลาสหรือแท็กที่เฉพาะเจาะจง
        # เราจะดึงเฉพาะส่วนที่เป็นเนื้อหาข่าว (p tags)
        paragraphs = soup.find_all('p')
        content = " ".join([p.get_text() for p in paragraphs if len(p.get_text()) > 50])
        
        # ตัดเนื้อหาให้เหลือประมาณ 3000 ตัวอักษรเพื่อไม่ให้เกินขีดจำกัด AI
        return content[:3000] 
    except Exception as e:
        return f"ไม่สามารถดึงเนื้อหาเต็มได้: {e}"

# --- ส่วน Sidebar ---
with st.sidebar:
    st.header("⚙️ การตั้งค่า")
    default_api = st.secrets.get("GROQ_API_KEY", "")
    user_api = st.text_input("Groq API Key", value=default_api, type="password")
    
    st.divider()
    # RSS ของไทยรัฐ (เลือกหมวดหมู่ได้ เช่น /news, /sport, /ent)
    source_url = st.text_input("Thairath RSS URL", "https://www.thairath.co.th/rss/news")
    num_news = st.slider("จำนวนข่าวที่จะดึง", 1, 5, 3)

if user_api:
    try:
        client = Groq(api_key=user_api)

        if st.button("🚀 เริ่มดึงข่าวไทยรัฐแบบละเอียด"):
            with st.spinner('กำลังเข้าอ่านเนื้อหาข่าวจากไทยรัฐ...'):
                feed = feedparser.parse(source_url)
                
                if not feed.entries:
                    st.error("ไม่สามารถดึง RSS ได้ กรุณาตรวจสอบ URL")
                
                for entry in feed.entries[:num_news]:
                    # --- ขั้นตอนสำคัญ: ไปดึงเนื้อหาเต็มจากหน้าเว็บ ---
                    full_text = get_full_article(entry.link)
                    
                    # 1. สั่ง Groq สรุปเนื้อหาจากข้อมูลที่ดึงมาใหม่
                    s_prompt = f"""
                    นี่คือเนื้อหาข่าวจากไทยรัฐ: 
                    หัวข้อ: {entry.title}
                    เนื้อหาเต็ม: {full_text}
                    
                    งานของคุณ:
                    1. สรุปเป็นโพสต์ Facebook ที่ยาวและละเอียด (ประมาณ 4-5 ย่อหน้า)
                    2. เขียนพาดหัวให้น่าสนใจ (Clickbait แบบมีสาระ)
                    3. สรุปประเด็นสำคัญเป็นข้อๆ
                    4. วิเคราะห์ที่มาที่ไปและความน่าสนใจของข่าวนี้
                    5. ใส่ Emoji และ Hashtag ให้ครบถ้วน
                    """
                    
                    s_completion = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "user", "content": s_prompt}],
                        temperature=0.7,
                        max_tokens=2500
                    )
                    summary_result = s_completion.choices[0].message.content

                    # 2. สร้าง Prompt สำหรับเจนรูป
                    i_prompt = f"Create a high-quality cinematic photo prompt for AI generation based on this news: {entry.title}. Detailed lighting, 8k, professional photography style."
                    i_completion = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "user", "content": i_prompt}]
                    )
                    image_prompt = i_completion.choices[0].message.content

                    # --- แสดงผลหน้าจอ ---
                    st.subheader(f"🔥 {entry.title}")
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown("### 📝 โพสต์ Facebook ฉบับเต็ม")
                        st.write(summary_result)
                        
                    with col2:
                        st.markdown("### 🎨 AI Image Prompt")
                        st.code(image_prompt, language="text")
                        
                    st.caption(f"แหล่งข้อมูล: {entry.link}")
                    st.divider()
                        
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาด: {e}")
else:
    st.info("👈 ใส่ Groq API Key ใน Sidebar เพื่อเริ่มงาน")
