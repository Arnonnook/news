import streamlit as st
import feedparser
from groq import Groq
# เพิ่มเพื่อให้ดึง HTML ได้ดีขึ้น (ถ้าต้องการดึงจากหน้าเว็บตรงๆ ต้องลง pip install beautifulsoup4)

st.set_page_config(page_title="Deep News Analysis", page_icon="📰", layout="wide")

st.title("📰 ระบบดึงข่าวและวิเคราะห์เชิงลึก")
st.caption("ดึงเนื้อหาละเอียดขึ้น สรุปยาวขึ้น และสร้าง Prompt ที่แม่นยำ")

with st.sidebar:
    st.header("⚙️ การตั้งค่า")
    default_api = st.secrets.get("GROQ_API_KEY", "")
    user_api = st.text_input("Groq API Key", value=default_api, type="password")
    
    st.divider()
    # แนะนำ RSS ของ Google News มักจะให้ข้อมูลที่เชื่อมโยงได้ดี
    source_url = st.text_input("RSS Feed URL", "https://news.google.com/rss?hl=th&gl=TH&ceid=TH:th")
    num_news = st.slider("จำนวนข่าว", 1, 5, 3) # ลดจำนวนลงเพื่อเน้นคุณภาพต่อข่าว

if user_api:
    try:
        client = Groq(api_key=user_api)

        if st.button("🚀 เริ่มดึงข้อมูลเชิงลึก"):
            with st.spinner('กำลังดึงและวิเคราะห์เนื้อหาอย่างละเอียด...'):
                feed = feedparser.parse(source_url)
                
                for entry in feed.entries[:num_news]:
                    # รวมหัวข้อและเนื้อหาที่มี (บางครั้งเนื้อหาเต็มอยู่ใน entry.description)
                    full_raw_content = f"หัวข้อ: {entry.title} \nรายละเอียดเบื้องต้น: {entry.get('summary', 'ไม่มีข้อมูลสรุป')}"

                    # 1. Prompt แบบ "Deep Summary" สำหรับ Facebook
                    # สั่งให้ AI วิเคราะห์บริบทเพิ่มเติมและเขียนให้น่าอ่านแบบยาว
                    s_prompt = f"""
                    วิเคราะห์ข่าวจากข้อมูลนี้: {full_raw_content}
                    งานของคุณ:
                    1. เขียนโพสต์ Facebook ความยาวประมาณ 3-5 ย่อหน้า
                    2. เริ่มด้วยพาดหัวที่หยุดนิ้วคนดู (Hook)
                    3. สรุปเนื้อหาสำคัญ แยกเป็นข้อๆ (Bullet points) ให้เข้าใจง่าย
                    4. เพิ่มบทวิเคราะห์สั้นๆ ว่าเรื่องนี้กระทบกับคนอ่านอย่างไร
                    5. ใส่ Emoji ที่เหมาะสมและ Hashtag 5-7 อัน
                    6. ใช้ภาษาที่เป็นกันเองแต่ดูน่าเชื่อถือ
                    """
                    
                    s_completion = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "user", "content": s_prompt}],
                        temperature=0.7,
                        max_tokens=2048 # เพิ่มจำนวน Token เพื่อให้เขียนได้ยาวขึ้น
                    )
                    summary_text = s_completion.choices[0].message.content

                    # 2. Prompt สำหรับ Image ที่ละเอียดขึ้น (Detailed Scene Description)
                    i_prompt = f"""
                    Based on this news: '{entry.title}'
                    Create a hyper-realistic, detailed English prompt for AI image generation (Midjourney/DALL-E style).
                    Include:
                    - Subject detail (clothing, expression, action)
                    - Environment/Background (weather, location, atmosphere)
                    - Camera settings (8k, cinematic lighting, 85mm lens, depth of field)
                    - Artistic style (Photo-realism)
                    One long continuous paragraph.
                    """
                    
                    i_completion = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "user", "content": i_prompt}],
                        temperature=0.6
                    )
                    image_prompt_eng = i_completion.choices[0].message.content

                    # --- UI Rendering ---
                    st.subheader(f"🔥 {entry.title}")
                    col1, col2 = st.columns([3, 2]) # ปรับสัดส่วนให้คอลัมน์เนื้อหายาวกว้างกว่า
                    
                    with col1:
                        st.markdown("### 📝 เนื้อหาโพสต์แบบละเอียด")
                        st.write(summary_text) # ใช้ write แทน code เพื่อให้อ่านง่ายขึ้น (ก๊อปปี้ได้เหมือนกัน)
                        if st.button(f"คัดลอกเนื้อหา {entry.title[:20]}...", key=entry.link):
                            st.write("คัดลอกสำเร็จ! (ตัวอย่างฟีเจอร์)")
                        
                    with col2:
                        st.markdown("### 🎨 Image Prompt (Detailed)")
                        st.code(image_prompt_eng, language="text")
                    
                    st.markdown(f"🔗 [อ่านข่าวเต็มจากแหล่งที่มา]({entry.link})")
                    st.divider()
                        
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาด: {e}")
else:
    st.info("👈 กรุณาใส่ Groq API Key")
