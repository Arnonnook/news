import streamlit as st
import feedparser
import google.generativeai as genai

# ตั้งค่าหน้าจอ
st.set_page_config(page_title="News to Image Prompt", page_icon="🎨", layout="wide")

st.title("📰 ระบบสรุปข่าว & เจนชุดคำสั่งสร้างรูป")
st.caption("ดึงข่าว สรุปเนื้อหา และสร้าง English Prompt สำหรับเอาไปเจนรูปเอง")

# ส่วนตั้งค่าใน Sidebar
with st.sidebar:
    st.header("⚙️ การตั้งค่า")
    default_api = st.secrets.get("GEMINI_API_KEY", "")
    user_api = st.text_input("Gemini API Key", value=default_api, type="password")
    
    st.divider()
    source_url = st.text_input("RSS Feed URL", "https://www.thairath.co.th/rss/news")
    num_news = st.slider("จำนวนข่าว", 1, 10, 5)

if user_api:
    try:
        genai.configure(api_key=user_api)
        model = genai.GenerativeModel('models/gemini-2.5-flash')

        if st.button("🔄 ดึงข่าวและสร้างชุดคำสั่ง"):
            with st.spinner('กำลังวิเคราะห์ข่าว...'):
                feed = feedparser.parse(source_url)
                
                for entry in feed.entries[:num_news]:
                    # 1. สั่งสรุปเนื้อหาข่าวสำหรับ Facebook
                    s_prompt = f"สรุปข่าวนี้สั้นๆ สำหรับโพสต์ Facebook พร้อมอีโมจิ: {entry.title} \nเนื้อหา: {entry.summary}"
                    summary_text = model.generate_content(s_prompt).text
                    
                    # 2. สั่งสร้าง Prompt สำหรับเอาไปเจนรูป (เน้นความสวยงามและสื่ออารมณ์)
                    # คุณสามารถแก้ 'สไตล์' ใน i_prompt นี้ได้ตามชอบ เช่น cinematic, oil painting, 3d render
                    i_prompt = f"""วิเคราะห์ข่าวนี้: '{entry.title}' 
                    แล้วเขียน Image Generation Prompt เป็นภาษาอังกฤษ 1 ประโยคยาวๆ 
                    ระบุรายละเอียด แสง สี และสไตล์แบบ Cinematic Photo เพื่อให้รูปออกมาดูแพงและสื่อถึงเนื้อหาข่าว
                    (ไม่ต้องมีเครื่องหมายคำพูด)
                    เนื้อหาข่าว: {entry.title}"""
                    
                    image_prompt_eng = model.generate_content(i_prompt).text.strip()

                    # --- แสดงผล ---
                    st.subheader(f"📌 {entry.title}")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("📝 **ข้อความสำหรับโพสต์ Facebook:**")
                        st.code(summary_text, language="text")
                    
                    with col2:
                        st.markdown("🎨 **ชุดคำสั่งสร้างรูป (Copy ไปวางใน AI ตัวอื่น):**")
                        # แสดง Prompt ภาษาอังกฤษในช่องที่ก๊อปปี้ง่ายๆ
                        st.code(image_prompt_eng, language="text")
                    
                    st.markdown(f"[🔗 ลิงก์ข่าวต้นฉบับ]({entry.link})")
                    st.divider()
                    
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาด: {e}")
else:
    st.info("👈 กรุณาใส่ Gemini API Key ที่แถบด้านข้าง")
