import streamlit as st
import feedparser
import google.generativeai as genai
import requests

# ตั้งค่าหน้าจอ
st.set_page_config(page_title="AI News Fast Copy", page_icon="🚀", layout="wide")

st.title("📰 ระบบสรุปข่าว & ก๊อปปี้ลงเพจ")
st.caption("ดึงข่าว สรุปด้วย AI และกดก๊อปปี้ไปโพสต์ได้ทันที")

# ส่วนตั้งค่า API ใน Sidebar
with st.sidebar:
    st.header("⚙️ การตั้งค่า")
    # พยายามดึงจาก Secrets ก่อน ถ้าไม่มีค่อยให้กรอกเอง
    default_api = st.secrets.get("GEMINI_API_KEY", "")
    user_api = st.text_input("Gemini API Key", value=default_api, type="password")
    
    st.divider()
    source_url = st.text_input("RSS Feed URL", "https://www.thairath.co.th/rss/news")
    num_news = st.slider("จำนวนข่าวที่ต้องการ", 1, 10, 5)

if user_api:
    try:
        genai.configure(api_key=user_api)
        # ใช้ชื่อ model แบบเต็มเพื่อป้องกัน Error NotFound
        model = genai.GenerativeModel('models/gemini-2.5-flash')

        if st.button("🔄 ดึงข่าวและสรุปใหม่"):
            with st.spinner('กำลังประมวลผล...'):
                feed = feedparser.parse(source_url)
                
                if not feed.entries:
                    st.error("ไม่สามารถดึงข้อมูลจาก RSS นี้ได้ กรุณาตรวจสอบ URL")
                
                for entry in feed.entries[:num_news]:
                    col1, col2 = st.columns([1, 1.2])
                    
                    with col1:
                        # เจนรูปภาพจากหัวข้อข่าว (ใช้ Pollinations AI)
                        # ส่งหัวข้อไปให้ Gemini แปลเป็นอังกฤษสั้นๆ ก่อนเพื่อให้รูปออกมาตรงปก
                        t_prompt = f"Translate to short English for image prompt: {entry.title}"
                        eng_title = model.generate_content(t_prompt).text
                        img_url = f"https://pollinations.ai/p/{eng_title.replace(' ', '_')}?width=1080&height=1080&nologo=true"
                        st.image(img_url, caption="AI Generated Image")
                        st.markdown(f"[🔗 อ่านข่าวต้นฉบับ]({entry.link})")

                    with col2:
                        st.subheader(entry.title)
                        
                        # สั่งสรุปข่าว
                        s_prompt = f"""สรุปข่าวนี้สำหรับโพสต์ Facebook:
                        หัวข้อ: {entry.title}
                        เนื้อหา: {entry.summary}
                        
                        รูปแบบที่ต้องการ:
                        1. พาดหัวให้น่าสนใจ
                        2. เนื้อหาใจความสำคัญ 3-4 บรรทัด (ใช้อีโมจิ)
                        3. แฮชแท็กที่เกี่ยวข้อง
                        """
                        
                        response = model.generate_content(s_prompt)
                        final_text = response.text
                        
                        # ส่วนที่ให้ก๊อปปี้ (ใช้ st.code เพื่อให้มีปุ่ม Copy)
                        st.write("📋 **ก๊อปปี้ข้อความด้านล่างนี้:**")
                        st.code(final_text, language="text") 
                        
                        # ปุ่มแชร์ไป Facebook แบบด่วน (ส่งแค่ Link)
                        share_url = f"https://www.facebook.com/sharer/sharer.php?u={entry.link}"
                        st.markdown(f'<a href="{share_url}" target="_blank">🔵 แชร์ลิงก์ไป Facebook</a>', unsafe_allow_back_config=True, unsafe_allow_html=True)
                    
                    st.divider()
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาด: {e}")
        st.info("คำแนะนำ: ลองตรวจสอบ API Key หรือเปลี่ยนชื่อ Model ในโค้ดเป็น 'gemini-pro'")
else:
    st.info("👈 กรุณาใส่ Gemini API Key ที่แถบด้านข้างเพื่อเริ่มทำงาน")
