import streamlit as st
import requests
import base64
from io import BytesIO
from PIL import Image
import os

st.set_page_config(
    page_title="AI Web Browser",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp {
        background-color: #000000;
        color: #00FF00;
    }
    .stTextInput > div > div > input {
        background-color: #111111;
        color: #00FF00;
        border: 1px solid #00AA00;
    }
    .stButton > button {
        background-color: #002200;
        color: #00FF00;
        border: 1px solid #00AA00;
    }
    .stButton > button:hover {
        background-color: #004400;
    }
    .stTextArea > div > div > textarea {
        background-color: #111111;
        color: #00FF00;
        border: 1px solid #00AA00;
    }
    .css-1d391kg, .css-1offfwp, .css-1kyxreq {
        background-color: #000000;
    }
    .st-emotion-cache-1v0mbdj {
        border: 1px solid #00AA00;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #00FF00;
    }
    .stAlert {
        border: 1px solid #00AA00;
        border-radius: 5px;
    }
    .response-box {
        background-color: #111111;
        border: 1px solid #00AA00;
        border-radius: 5px;
        padding: 10px;
        margin: 10px 0;
    }
    .chat-message-user {
        background-color: #002200;
        border: 1px solid #00AA00;
        border-radius: 5px;
        padding: 10px;
        margin: 5px 0;
        text-align: right;
    }
    .chat-message-assistant {
        background-color: #111111;
        border: 1px solid #00AA00;
        border-radius: 5px;
        padding: 10px;
        margin: 5px 0;
    }
    
    /* Responsive ASCII Art */
    .ascii-logo {
        color: #00FF00;
        text-align: center;
        font-family: 'Courier New', monospace;
        white-space: pre;
        overflow-x: auto;
        line-height: 1.2;
    }
    
    /* Desktop - Full size */
    @media (min-width: 1200px) {
        .ascii-logo {
            font-size: 0.9em;
        }
    }
    
    /* Laptop */
    @media (max-width: 1199px) and (min-width: 992px) {
        .ascii-logo {
            font-size: 0.75em;
        }
    }
    
    /* Tablet */
    @media (max-width: 991px) and (min-width: 768px) {
        .ascii-logo {
            font-size: 0.6em;
        }
    }
    
    /* Mobile Landscape */
    @media (max-width: 767px) and (min-width: 576px) {
        .ascii-logo {
            font-size: 0.45em;
        }
    }
    
    /* Mobile Portrait */
    @media (max-width: 575px) {
        .ascii-logo {
            font-size: 0.35em;
        }
        .ascii-logo-simple {
            display: block;
            font-size: 1.2em;
            font-weight: bold;
        }
        .ascii-logo-full {
            display: none;
        }
    }
    
    /* Very small screens */
    @media (max-width: 400px) {
        .ascii-logo {
            font-size: 0.28em;
        }
    }
</style>
""", unsafe_allow_html=True)

# ASCII Art Header with responsive design
ascii_art_full = '''    ▄▄▄       ██▓    ▄▄▄       ███▄    █  ▄▄▄       ██▓     ██▓███  
   ▒████▄    ▓██▒   ▒████▄     ██ ▀█   █ ▒████▄    ▓██▒    ▓██░  ██▒
   ▒██  ▀█▄  ▒██▒   ▒██  ▀█▄  ▓██  ▀█ ██▒▒██  ▀█▄  ▒██░    ▓██░ ██▓▒
   ░██▄▄▄▄██ ░██░   ░██▄▄▄▄██ ▓██▒  ▐▌██▒░██▄▄▄▄██ ▒██░    ▒██▄█▓▒ ▒
    ▓█   ▓██▒░██░    ▓█   ▓██▒▒██░   ▓██░ ▓█   ▓██▒░██████▒▒██▒ ░  ░
    ▒▒   ▓▒█░░▓      ▒▒   ▓▒█░░ ▒░   ▒ ▒  ▒▒   ▓▒█░░ ▒░▓  ░▒▓▒░ ░  ░
     ▒   ▒▒ ░ ▒ ░     ▒   ▒▒ ░░ ░░   ░ ▒░  ▒   ▒▒ ░░ ░ ▒  ░░▒ ░     
     ░   ▒    ▒ ░     ░   ▒      ░   ░ ░   ░   ▒     ░ ░   ░░       
         ░  ░ ░           ░  ░         ░       ░  ░    ░  ░         
                      ╔══════════════════════════╗
                      ║  Intelligent Analysis   ║
                      ╚══════════════════════════╝'''

ascii_art_simple = '''
╔═══════════════════════════════╗
║       AI ANALYSIS v1.0        ║
║    Intelligent Analysis       ║
╚═══════════════════════════════╝
'''

st.markdown(f'''
<div class="ascii-logo">
<div class="ascii-logo-full">{ascii_art_full}</div>
<div class="ascii-logo-simple" style="display: none;">{ascii_art_simple}</div>
</div>
''', unsafe_allow_html=True)

st.sidebar.header("Navigation")
app_mode = st.sidebar.selectbox("Choose Mode", ["Web Browser", "Text Analysis", "Vision Analysis"])

# Initialize session state
if 'conversation' not in st.session_state:
    st.session_state.conversation = []

if 'text_chat_history' not in st.session_state:
    st.session_state.text_chat_history = []

if 'vision_chat_history' not in st.session_state:
    st.session_state.vision_chat_history = []

if app_mode == "Web Browser":
    st.subheader(" Web Browser AI Assistant")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        url = st.text_input("Enter URL to browse:", placeholder="https://example.com", key="url_input")
    with col2:
        query = st.text_input("Your question:", placeholder="What is this page about?", key="query_input")

    if st.button(" Browse & Ask", key="browse_button"):
        if url and query:
            with st.spinner(" Browsing website and analyzing content..."):
                try:
                    import os
                    api_base_url = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
                    response = requests.post(
                        f"{api_base_url}/browse",
                        json={"url": url, "query": query},
                        timeout=60
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        st.session_state.conversation.append({
                            "url": url,
                            "query": query,
                            "response": result.get("response", "No response received"),
                            "screenshot_base64": result.get("screenshot_base64"),
                            "timestamp": "Just now"
                        })
                    else:
                        st.error(f" Error: {response.status_code} - {response.text}")
                        
                except requests.exceptions.Timeout:
                    st.error(" Request timed out. The website may be taking too long to load.")
                except requests.exceptions.ConnectionError:
                    st.error(" Could not connect to the server. Make sure the FastAPI server is running.")
                except Exception as e:
                    st.error(f" An error occurred: {str(e)}")
        else:
            st.warning("⚠️ Please enter both URL and question.")

    # Display conversation
    st.subheader("💬 Conversation History")
    for i, item in enumerate(st.session_state.conversation):
        with st.container():
            st.markdown(f'<div class="response-box">', unsafe_allow_html=True)
            st.markdown(f"** URL:** {item['url']}")
            st.markdown(f"** Question:** {item['query']}")
            st.markdown(f"** AI Response:** {item['response']}")
            
            if item['screenshot_base64']:
                try:
                    # Decode base64 image
                    image_data = base64.b64decode(item['screenshot_base64'])
                    image = Image.open(BytesIO(image_data))
                    st.image(image, caption="📸 Website Screenshot", use_column_width=True)
                except Exception as e:
                    st.error(f"Could not display image: {str(e)}")
            
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("---")

elif app_mode == "Text Analysis":
    st.subheader("Text Analysis Chat")
    
    uploaded_pdf = st.file_uploader("Upload a PDF for context", type=["pdf"], key="pdf_uploader")
    pdf_content = None
    
    if uploaded_pdf is not None:
        import PyPDF2
        pdf_reader = PyPDF2.PdfReader(uploaded_pdf)
        pdf_content = ""
        for page in pdf_reader.pages:
            pdf_content += page.extract_text() + "\n"
        st.success(f"PDF loaded successfully! Extracted {len(pdf_content)} characters.")
    
    # Display chat messages
    chat_container = st.container()
    with chat_container:
        for i, message in enumerate(st.session_state.text_chat_history):
            if message['role'] == 'user':
                st.markdown(f'<div class="chat-message-user"><strong>You:</strong> {message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message-assistant"><strong>🤖 AI:</strong> {message["content"]}</div>', unsafe_allow_html=True)
    
    with st.form(key='text_chat_form', clear_on_submit=True):
        col1, col2 = st.columns([4, 1])
        with col1:
            user_input = st.text_input("Type your message here...", key="text_chat_input")
        with col2:
            text_mode = st.radio("Model", ["Local", "Online"], key="text_model_choice")
        
        submit_button = st.form_submit_button("Send ")
        
        if submit_button and user_input:
            # Add user message to chat
            st.session_state.text_chat_history.append({'role': 'user', 'content': user_input})
            
            with st.spinner("Thinking..."):
                try:
                    payload = {
                        "prompt": user_input,
                        "use_local": text_mode.lower() == "local",
                        "context": st.session_state.text_chat_history
                    }
                    
                    if pdf_content:
                        payload["pdf_content"] = pdf_content
                    
                    import os
                    api_base_url = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
                    
                    response = requests.post(
                        f"{api_base_url}/text-analyze",
                        json=payload,
                        timeout=60
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        response_text = result.get("response", "No response received")
                    else:
                        response_text = f"Error: {response.status_code} - {response.text}"
                    
                    # Add AI response to chat
                    st.session_state.text_chat_history.append({'role': 'assistant', 'content': response_text})
                    
                    # Force a rerun to update the chat display
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error in text analysis: {str(e)}")

elif app_mode == "Vision Analysis":
    st.subheader("👁️ Vision Analysis Chat")
    
    # Display chat messages
    chat_container = st.container()
    with chat_container:
        for i, message in enumerate(st.session_state.vision_chat_history):
            if message['role'] == 'user':
                st.markdown(f'<div class="chat-message-user"><strong>You:</strong> {message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message-assistant"><strong>🤖 AI:</strong> {message["content"]}</div>', unsafe_allow_html=True)
    
    # Vision input
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='Uploaded Image', use_column_width=True)
        
        with st.form(key='vision_chat_form', clear_on_submit=True):
            col1, col2 = st.columns([4, 1])
            with col1:
                vision_query = st.text_input("Ask about the image...", placeholder="Describe this image...", key="vision_chat_input")
            with col2:
                vision_mode = st.radio("Model", ["Local", "Online"], key="vision_model_choice")
            
            submit_button = st.form_submit_button("Send 📤")
            
            if submit_button and vision_query:
                st.session_state.vision_chat_history.append({'role': 'user', 'content': f"[Image uploaded] {vision_query}"})
                
                with st.spinner("👀 Analyzing image..."):
                    try:
                        # Convert image to base64
                        buffered = BytesIO()
                        image.save(buffered, format="PNG")
                        img_str = base64.b64encode(buffered.getvalue()).decode()
                        
                        import os
                        api_base_url = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
                        
                        response = requests.post(
                            f"{api_base_url}/vision-analyze",
                            json={
                                "image_data": img_str,
                                "prompt": vision_query,
                                "use_local": vision_mode.lower() == "local",
                                "context": st.session_state.vision_chat_history
                            },
                            timeout=60
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            response_text = result.get("response", "No response received")
                        else:
                            response_text = f"Error: {response.status_code} - {response.text}"
                        
                        # Add AI response to chat
                        st.session_state.vision_chat_history.append({'role': 'assistant', 'content': response_text})
                        
                        # Force a rerun to update the chat display
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error in vision analysis: {str(e)}")

with st.expander("ℹ️ Instructions"):
    st.write("""
    **Web Browser Mode:**
    1. Make sure the FastAPI server is running (python -m uvicorn server:app --host 127.0.0.1 --port 8001)
    2. Enter a URL and your question about the page
    3. Click 'Browse & Ask' to analyze the website content
    4. View the AI response and screenshot of the website

    For deployment (Render/Docker):
    - Set environment variable API_BASE_URL to point to your backend server
    - Configure API keys (OPENROUTER_API_KEY, etc.) in your backend server environment

    **Text Analysis Mode:**
    1. Select whether to use Local or Online models
    2. Type your message in the input field
    3. Click 'Send' to get AI response in a chat-like interface

    **Vision Analysis Mode:**
    1. Upload an image file (JPG, PNG)
    2. Type your question about the image
    3. Select whether to use Local or Online models
    4. Click 'Send' to get AI response in a chat-like interface
    """)
    
st.sidebar.markdown("---")
st.sidebar.markdown("**AI Analysis v1.0**")
st.sidebar.markdown("Powered by AI ")