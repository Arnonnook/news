import streamlit as st
import feedparser
import google.generativeai as genai
import requests

# ตั้งค่าหน้าจอ
st.set_page_config(page_title="AI News & Image Gen", page_icon="🖼️", layout="wide")

st.title("📰 ระบบสรุปข่าว & สร้างรูปประกอบอัตโนมัติ")
st.caption("ดึงข่าว สรุปเนื้อหา และสร้างรูปที่เกี่ยวข้องด้วย AI")

# ส่วนตั้งค่า API ใน Sidebar
with st.sidebar:
    st.header("⚙️ การตั้งค่า")
    default_api = st.secrets.get("GEMINI_API_KEY", "")
    user_api = st.text_input("Gemini API Key", value=default_api, type="password")
    
    st.divider()
    source_url = st.text_input("RSS Feed URL", "https://www.thairath.co.th/rss/news")
    num_news = st.slider("จำนวนข่าวที่ต้องการ", 1, 5, 3) # ลดจำนวนลงเพื่อความเร็ว

if user_api:
    try:
        genai.configure(api_key=user_api)
        model = genai.GenerativeModel('models/gemini-2.5-flash')

        if st.button("🔄 ดึงข่าวและสรุปใหม่"):
            with st.spinner('กำลังประมวลผลข่าวและสร้างรูป...'):
                feed = feedparser.parse(source_url)
                
                if not feed.entries:
                    st.error("ไม่สามารถดึงข้อมูลจาก RSS นี้ได้ กรุณาตรวจสอบ URL")
                
                for entry in feed.entries[:num_news]:
                    # --- ส่วนของ AI Brain ---
                    # 1. สั่งสรุปข่าว
                    s_prompt = f"""สรุปข่าวนี้สำหรับโพสต์ Facebook: {entry.title} \nเนื้อหา: {entry.summary} \n\nรูปแบบ: พาดหัว, เนื้อหา 3 บรรทัดพร้อมอีโมจิ, แฮชแท็ก"""
                    response = model.generate_content(s_prompt)
                    final_text = response.text
                    
                    # 2. **(ใหม่)** สั่ง Gemini ให้เจน Prompt สำหรับสร้างรูปภาพ
                    # สั่งให้เอาแค่ Keyword ภาษาอังกฤษที่สื่อถึง 'อารมณ์' หรือ 'ธีมหลัก' ของข่าว
                    i_prompt = f"""วิเคราะห์เนื้อหาข่าวนี้: '{entry.title}' แล้วสร้าง 'Image Generation Prompt' เป็นภาษาอังกฤษสั้นๆ 1 ประโยค 
                    โดยเน้นธีมหลัก อารมณ์ของภาพ หรือคีย์เวิร์ดที่สำคัญ (ไม่ต้องสมจริงมาก เอาแค่สื่อถึงเรื่อง)
                    ตัวอย่าง: 'sad dramatic rain background, cyber crime abstract, football match atmosphere'
                    ขอแค่ประโยคภาษาอังกฤษอย่างเดียว ไม่เอาเครื่องหมายคำพูด
                    เนื้อหาข่าว: {entry.title}"""
                    
                    try:
                        img_gen_prompt = model.generate_content(i_prompt).text.strip()
                    except:
                        # Fallback ถ้า Gemini เจน Keyword ไม่ได้ ให้ใช้หัวข้อข่าวแทน
                        img_gen_prompt = entry.title 

                    # --- ส่วนแสดงผล ---
                    col1, col2 = st.columns([1, 1.2])
                    
                    with col1:
                        # 3. สร้างรูปภาพโดยใช้ Prompt ที่ Gemini เจนให้ (ใช้ Pollinations AI)
                        img_url = f"https://pollinations.ai/p/{img_gen_prompt.replace(' ', '_')}?width=1080&height=1080&nologo=true&enhance=true"
                        
                        st.image(img_url, caption=f"รูปประกอบธีม: {img_gen_prompt}")
                        st.markdown(f"[🔗 อ่านข่าวต้นฉบับ]({entry.link})")

                    with col2:
                        st.subheader(entry.title)
                        
                        # ส่วนที่ให้ก๊อปปี้ (มีปุ่ม Copy ในตัว)
                        st.write("📋 **ก๊อปปี้ข้อความด้านล่างนี้:**")
                        st.code(final_text, language="text") 
                        
                        # ปุ่มแชร์
                        share_url = f"https://www.facebook.com/sharer/sharer.php?u={entry.link}"
                        st.markdown(f'<a href="{share_url}" target="_blank" style="text-decoration: none; background-color: #1877F2; color: white; padding: 10px 20px; border-radius: 8px; font-weight: bold; display: inline-block;">🔵 กดเพื่อไปหน้าแชร์ Facebook</a>', unsafe_allow_html=True)
                    
                    st.divider()
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาด: {e}")
else:
    st.info("👈 กรุณาใส่ Gemini API Key ที่แถบด้านข้างเพื่อเริ่มทำงาน")
