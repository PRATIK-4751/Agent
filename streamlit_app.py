import streamlit as st
import requests
import base64
from io import BytesIO
from PIL import Image

st.set_page_config(page_title="AI Agent", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Space+Grotesk:wght@400;500;600&display=swap');
    
    .stApp { background-color: #0a0a0a !important; }
    * { font-family: 'Space Grotesk', sans-serif !important; color: #00ff88 !important; }
    
    .logo-container {
        text-align: center;
        padding: 30px 20px;
        margin-bottom: 20px;
    }
    
    .logo-text {
        font-family: 'Orbitron', monospace !important;
        font-size: clamp(2rem, 8vw, 5rem);
        font-weight: 900;
        color: #00ff88 !important;
        text-shadow: 0 0 10px #00ff88, 0 0 20px #00ff88, 0 0 40px #00ff8855;
        letter-spacing: 0.2em;
        margin: 0;
    }
    
    .logo-subtitle {
        font-family: 'Orbitron', monospace !important;
        font-size: clamp(0.6rem, 2vw, 1rem);
        color: #00ff88 !important;
        letter-spacing: 0.5em;
        margin-top: 10px;
        opacity: 0.8;
    }
    
    .logo-line {
        width: 80%;
        max-width: 500px;
        height: 2px;
        background: linear-gradient(90deg, transparent, #00ff88, transparent);
        margin: 15px auto;
    }
    
    .stTextInput > div > div > input {
        background-color: #111 !important;
        border: 1px solid #00ff88 !important;
        border-radius: 8px !important;
        color: #00ff88 !important;
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #00ff88, #00cc6a) !important;
        color: #000 !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    
    .stButton > button:hover { box-shadow: 0 0 30px rgba(0, 255, 136, 0.6) !important; }
    
    .chat-user {
        background: linear-gradient(135deg, #0a1a0a, #102010) !important;
        border: 1px solid #00ff88 !important;
        border-radius: 12px 12px 4px 12px !important;
        padding: 14px 18px !important;
        margin: 10px 0 !important;
        margin-left: 10% !important;
    }
    
    .chat-ai {
        background: linear-gradient(135deg, #0a0a1a, #101020) !important;
        border: 1px solid #6666ff !important;
        border-radius: 12px 12px 12px 4px !important;
        padding: 14px 18px !important;
        margin: 10px 0 !important;
        margin-right: 10% !important;
    }
    
    .mode-box {
        background: #0a0a0a !important;
        border: 1px solid #00ff8855 !important;
        border-radius: 16px !important;
        padding: 25px !important;
        margin: 15px 0 !important;
    }
    
    .stSelectbox > div > div { background: #111 !important; border: 1px solid #00ff88 !important; }
    .stFileUploader > div { background: #0a0a0a !important; border: 2px dashed #00ff8855 !important; }
    .stRadio > div { flex-direction: row !important; gap: 20px !important; }
    .stRadio label { color: #00ff88 !important; }
</style>
""", unsafe_allow_html=True)

st.markdown('''
<div class="logo-container">
    <div class="logo-line"></div>
    <h1 class="logo-text">AI AGENT</h1>
    <p class="logo-subtitle">ANALYSIS & WEB BROWSING</p>
    <div class="logo-line"></div>
</div>
''', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    mode = st.selectbox("Mode", ["Text", "Vision", "Browse"], label_visibility="collapsed")

if 'text_h' not in st.session_state: st.session_state.text_h = []
if 'vision_h' not in st.session_state: st.session_state.vision_h = []
if 'browse_h' not in st.session_state: st.session_state.browse_h = []

API = "http://127.0.0.1:8002"

if mode == "Text":
    st.markdown('<div class="mode-box">', unsafe_allow_html=True)
    
    col_pdf, col_model = st.columns([2, 1])
    with col_pdf:
        pdf = st.file_uploader("[+] PDF (optional)", type=["pdf"])
    with col_model:
        model_type = st.radio("Model", ["Online", "Local"], horizontal=True)
    
    pdf_text = None
    if pdf:
        import PyPDF2
        pdf_text = "\n".join([p.extract_text() for p in PyPDF2.PdfReader(pdf).pages])
        st.success("[OK] PDF loaded")
    
    for m in st.session_state.text_h:
        c = "chat-user" if m['role'] == 'user' else "chat-ai"
        i = "[YOU]" if m['role'] == 'user' else "[AI]"
        st.markdown(f'<div class="{c}">{i} {m["content"]}</div>', unsafe_allow_html=True)
    
    with st.form("tf", clear_on_submit=True):
        inp = st.text_input("", placeholder="Ask anything...", label_visibility="collapsed")
        if st.form_submit_button("Send >>") and inp:
            st.session_state.text_h.append({'role': 'user', 'content': inp})
            with st.spinner("[...]"):
                try:
                    use_local = model_type == "Local"
                    p = {"prompt": inp, "use_local": use_local, "context": st.session_state.text_h}
                    if pdf_text: p["pdf_content"] = pdf_text
                    r = requests.post(f"{API}/text-analyze", json=p, timeout=120)
                    res = r.json().get("response", "Error") if r.status_code == 200 else "Error"
                    st.session_state.text_h.append({'role': 'assistant', 'content': res})
                    st.rerun()
                except Exception as e: st.error(f"[X] {e}")
    
    st.markdown('</div>', unsafe_allow_html=True)

elif mode == "Vision":
    st.markdown('<div class="mode-box">', unsafe_allow_html=True)
    
    col_img, col_model = st.columns([2, 1])
    with col_model:
        model_type = st.radio("Model", ["Online", "Local"], horizontal=True, key="v_model")
    
    for m in st.session_state.vision_h:
        c = "chat-user" if m['role'] == 'user' else "chat-ai"
        i = "[YOU]" if m['role'] == 'user' else "[AI]"
        st.markdown(f'<div class="{c}">{i} {m["content"]}</div>', unsafe_allow_html=True)
    
    img_file = st.file_uploader("[+] Image", type=["jpg", "jpeg", "png"])
    if img_file:
        img = Image.open(img_file)
        st.image(img, use_container_width=True)
        
        with st.form("vf", clear_on_submit=True):
            q = st.text_input("", placeholder="Ask about image...", label_visibility="collapsed")
            if st.form_submit_button("Analyze >>") and q:
                st.session_state.vision_h.append({'role': 'user', 'content': f"[IMG] {q}"})
                with st.spinner("[...]"):
                    try:
                        use_local = model_type == "Local"
                        buf = BytesIO()
                        img.save(buf, format="PNG")
                        b64 = base64.b64encode(buf.getvalue()).decode()
                        r = requests.post(f"{API}/vision-analyze", json={"image_data": b64, "prompt": q, "use_local": use_local}, timeout=120)
                        res = r.json().get("response", "Error") if r.status_code == 200 else "Error"
                        st.session_state.vision_h.append({'role': 'assistant', 'content': res})
                        st.rerun()
                    except Exception as e: st.error(f"[X] {e}")
    
    st.markdown('</div>', unsafe_allow_html=True)

elif mode == "Browse":
    st.markdown('<div class="mode-box">', unsafe_allow_html=True)
    
    for h in st.session_state.browse_h:
        st.markdown(f'<div class="chat-user">[URL] {h["url"]} - {h["query"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="chat-ai">[AI] {h["response"]}</div>', unsafe_allow_html=True)
        if h.get("ss"):
            try: st.image(Image.open(BytesIO(base64.b64decode(h["ss"]))), use_container_width=True)
            except: pass
    
    with st.form("bf", clear_on_submit=True):
        url = st.text_input("", placeholder="https://example.com", label_visibility="collapsed")
        q = st.text_input("", placeholder="What to know?", label_visibility="collapsed", key="bq")
        if st.form_submit_button("Browse >>") and url and q:
            with st.spinner("[...]"):
                try:
                    r = requests.post(f"{API}/browse", json={"url": url, "query": q}, timeout=90)
                    if r.status_code == 200:
                        d = r.json()
                        st.session_state.browse_h.append({"url": url, "query": q, "response": d.get("response", ""), "ss": d.get("screenshot_base64")})
                        st.rerun()
                    else: st.error(f"[X] {r.text}")
                except Exception as e: st.error(f"[X] {e}")
    
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")
st.markdown("<center style='opacity:0.6'>[ Made by Pratik Raj ]</center>", unsafe_allow_html=True)