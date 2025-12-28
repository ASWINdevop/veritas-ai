import streamlit as st
import trafilatura
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import time
import base64
import os
import subprocess
import uuid
import re 
from transformers import pipeline
from youtube_transcript_api import YouTubeTranscriptApi 

# --- 0. WHISPER MODEL (Cached) ---
@st.cache_resource
def load_whisper_model():
    return pipeline(
        "automatic-speech-recognition",
        model="openai/whisper-tiny", 
        chunk_length_s=30,
        stride_length_s=5,
        return_timestamps=True,
    )

asr_pipeline = load_whisper_model()

# --- 1. FONT SETUP ---
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        return None

# Load Custom Font (Varino)
font_base64 = get_base64_of_bin_file("fonts/Varino - Normal.otf")
font_format = "opentype" if font_base64 else "truetype"
if not font_base64: font_base64 = get_base64_of_bin_file("fonts/Varino - Normal.ttf")

if font_base64:
    font_face_css = f"""
    @font-face {{
        font-family: 'Varino';
        src: url('data:font/{font_format};base64,{font_base64}') format('{font_format}');
        font-weight: normal;
        font-style: normal;
    }}
    """
else:
    font_face_css = ""

# --- 2. PAGE CONFIG ---
st.set_page_config(page_title="VERITAS AI", page_icon="👁️‍🗨️", layout="wide", initial_sidebar_state="expanded")

# --- 3. ADVANCED CSS (ANIMATIONS & GLOW) ---
st.markdown(f"""
<style>
    /* 1. IMPORTS & BACKGROUND */
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Exo+2:wght@300;400;700&display=swap');
    
    [data-testid="stAppViewContainer"] {{
        background-color: #030712;
        background-image: 
            linear-gradient(rgba(0, 255, 255, 0.03) 1px, transparent 1px), 
            linear-gradient(90deg, rgba(0, 255, 255, 0.03) 1px, transparent 1px);
        background-size: 30px 30px; 
        background-attachment: fixed;
    }}
    [data-testid="stHeader"] {{ background: rgba(0,0,0,0); }}

    /* 2. TYPOGRAPHY & CUSTOM FONT */
    {font_face_css}

    h1 {{
        font-family: 'Varino', sans-serif !important;
        letter-spacing: 4px;
        color: #82cfff !important;
        text-transform: uppercase;
        font-weight: normal;
        text-shadow: 0 0 25px rgba(130, 207, 255, 0.6);
        animation: glow 3s ease-in-out infinite alternate;
    }}
    
    @keyframes glow {{
        from {{ text-shadow: 0 0 10px rgba(130, 207, 255, 0.4); }}
        to {{ text-shadow: 0 0 30px rgba(130, 207, 255, 0.9), 0 0 10px #2eaae6; }}
    }}

    h2, h3 {{
        font-family: 'Orbitron', sans-serif !important;
        letter-spacing: 2px;
        color: #2eaae6 !important;
        text-transform: uppercase;
    }}
    p, div, span, input, button, label {{
        font-family: 'Exo 2', sans-serif;
    }}

    /* 3. INPUT FIELD */
    .stTextInput input {{
        background-color: rgba(0, 15, 30, 0.9) !important;
        border: 1px solid #005577 !important;
        color: #00f2ff !important;
        padding: 15px !important;
        height: 45px !important;
        border-radius: 8px !important;
        transition: all 0.3s ease;
        box-shadow: 0 0 10px rgba(0, 242, 255, 0.05);
    }}
    .stTextInput input:focus {{
        border-color: #00f2ff !important;
        box-shadow: 0 0 20px rgba(0, 242, 255, 0.3);
        background-color: rgba(0, 20, 40, 1) !important;
    }}

    /* 4. ANIMATED BUTTON */
    div.stButton > button {{
        background: transparent;
        border: 2px solid #00f2ff;
        color: #00f2ff;
        font-family: 'Orbitron', sans-serif;
        font-weight: 900;
        letter-spacing: 2px;
        height: 45px !important;
        border-radius: 8px !important;
        margin-top: 0px !important;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        position: relative;
        overflow: hidden;
        z-index: 1;
    }}
    div.stButton > button::before {{
        content: "";
        position: absolute;
        top: 0; left: 0; width: 0; height: 100%;
        background: #00f2ff;
        z-index: -1;
        transition: all 0.4s ease;
    }}
    div.stButton > button:hover {{
        color: #000;
        box-shadow: 0 0 35px rgba(0, 242, 255, 0.6);
        transform: scale(1.02);
    }}
    div.stButton > button:hover::before {{
        width: 100%;
    }}

    /* 5. NEURAL CARDS (GLOW ON HOVER) */
    .neural-card {{
        background: rgba(10, 20, 30, 0.6);
        border: 1px solid rgba(0, 242, 255, 0.15);
        padding: 25px;
        margin-bottom: 20px;
        backdrop-filter: blur(10px);
        border-radius: 12px;
        transition: all 0.4s ease;
        position: relative;
    }}
    .neural-card:hover {{
        transform: translateY(-5px) scale(1.01);
        border-color: rgba(0, 242, 255, 0.5);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5), 0 0 20px rgba(0, 242, 255, 0.1);
        background: rgba(15, 30, 45, 0.8);
    }}

    /* 6. SIDEBAR & PROGRESS */
    section[data-testid="stSidebar"] {{
        background-color: #020408;
        border-right: 1px solid #002233;
    }}
    .sidebar-stat {{
        background: rgba(0, 255, 255, 0.05);
        border-left: 3px solid #00f2ff;
        padding: 12px;
        margin-bottom: 12px;
        font-size: 0.85rem;
        color: #aaddff;
        border-radius: 0 8px 8px 0;
    }}
    .stProgress > div > div > div > div {{
        background: linear-gradient(90deg, #00ff88, #00cc44);
        box-shadow: 0 0 15px rgba(0, 255, 136, 0.4);
    }}
    
    /* 7. SCROLLBAR */
    ::-webkit-scrollbar {{ width: 10px; }}
    ::-webkit-scrollbar-track {{ background: #020408; }}
    ::-webkit-scrollbar-thumb {{ background: #004455; border-radius: 5px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: #00f2ff; }}

</style>
""", unsafe_allow_html=True)

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("### 👁️‍🗨️ SYSTEM CONTROL")
    
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
        st.success("API KEY: CONNECTED")
    else:
        api_key = st.text_input("ENTER API KEY", type="password")
    
    if not api_key: st.stop()
    
    st.markdown("---")
    st.markdown("### 🎛️ CONFIGURATION")
    
    max_claims = st.slider("MAX CLAIMS TO ANALYZE", min_value=1, max_value=10, value=3)
    
    st.markdown("---")
    st.markdown("**ACTIVE AGENTS**")
    st.markdown("""
    <div class="sidebar-stat">🕷️ CRAWLER: <b>STANDBY</b></div>
    <div class="sidebar-stat">🧠 ANALYZER: <b>ONLINE</b></div>
    <div class="sidebar-stat">⚖️ VERIFIER: <b>READY</b></div>
    """, unsafe_allow_html=True)
    
    st.markdown("**SYSTEM INTEGRITY**")
    st.progress(100)
    st.caption("VERITAS ENGINE // V15.0")

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.5-flash")

# --- 5. ROBUST FUNCTIONS (With Plain Text Support) ---

def download_youtube_audio(url):
    output_filename = f"audio_{uuid.uuid4().hex}"
    # HARDCODED FFMPEG PATH
    ffmpeg_location = "C:/ffmpeg/bin" 

    cmd = [
        "yt-dlp",
        "--ffmpeg-location", ffmpeg_location,
        "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "-f", "bestaudio/best",
        "-x", "--audio-format", "mp3",
        "-o", f"{output_filename}.%(ext)s",
        url
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"YT-DLP Error: {result.stderr}")
    return f"{output_filename}.mp3"

def transcribe_audio(path):
    if not os.path.exists(path): return "Error: Audio file missing."
    
    try:
        # Try to run the heavy AI task
        result = asr_pipeline(path)
        text_output = result["text"]
        return text_output
        
    except Exception as e:
        # If AI crashes, return the error
        return f"Error during transcription: {str(e)}"
        
    finally:
        # THIS BLOCK RUNS NO MATTER WHAT (Success or Crash)
        try:
            if os.path.exists(path):
                os.remove(path)
                print(f"Deleted temp file: {path}") # Optional log
        except:
            pass

def get_input_content(user_input):
    """
    Intelligent Router:
    1. Video URL -> Audio Transcript
    2. Article URL -> Scraped Text
    3. Plain Text -> Passed Directly
    """
    
    # 1. VIDEO CHECK (YouTube, Instagram, etc.)
    video_domains = ["youtube.com", "youtu.be", "instagram.com/reel", "tiktok.com", "vimeo.com"]
    if any(x in user_input for x in video_domains):
        # Try Captions (YouTube)
        if "youtube.com" in user_input or "youtu.be" in user_input:
            try:
                vid_match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', user_input)
                if vid_match:
                    vid = vid_match.group(1)
                    t = YouTubeTranscriptApi.get_transcript(vid)
                    text = " ".join([i['text'] for i in t])
                    return f"TRANSCRIPT:\n{text}"
            except: pass 

        # Try Audio
        try:
            audio_path = download_youtube_audio(user_input)
            text = transcribe_audio(audio_path)
            return f"TRANSCRIPT:\n{text}"
        except Exception as e:
            st.error(f"❌ Audio Extraction Failed: {str(e)}")
            return None

    # 2. ARTICLE CHECK (Starts with http/https)
    if user_input.startswith("http://") or user_input.startswith("https://") or user_input.startswith("www."):
        try:
            d = trafilatura.fetch_url(user_input)
            if d: 
                text = trafilatura.extract(d)
                if text: return text
            
            # Fallback to Requests
            h = {'User-Agent': 'Mozilla/5.0'}
            r = requests.get(user_input, headers=h, timeout=10)
            if r.status_code == 200:
                s = BeautifulSoup(r.content, 'html.parser')
                text = s.get_text(separator=' ', strip=True)
                if len(text) > 100: return text
            return None
        except: return None

    # 3. PLAIN TEXT (If not a URL)
    # Assume it is raw text if it doesn't match above checks
    return user_input

def extract_claims(user_input, model):
    content = get_input_content(user_input)
    
    if not content: return []
    if "YT-DLP Error" in content[:50]:
        st.error(content)
        return []

    # If content is very short (e.g., "Hello"), don't process
    if len(content) < 50:
        st.warning("⚠️ Input too short for analysis.")
        return []

    prompt = f"Extract {max_claims + 2} factual claims from the text below. Output ONLY bullet points. TEXT: {content[:15000]}"
    try:
        resp = model.generate_content(prompt)
        claims = []
        for line in resp.text.split("\n"):
            clean = line.strip().lstrip("*-•1234567890. ")
            if len(clean) > 5: 
                claims.append({"claim": clean})
        return claims
    except: return []


def process_claims(claims, model):
    results = []
    p_bar = st.progress(0)
    for i, c in enumerate(claims):
        prompt = f"Verify: '{c['claim']}'. Status: SUPPORTED/CONTRADICTED/INCONCLUSIVE. Reason: 1 sentence."
        
        try:
            resp = model.generate_content(prompt)
            status, reason = "INCONCLUSIVE", "Unable to verify."
            for line in resp.text.split("\n"):
                if "Status:" in line: status = line.split(":")[1].strip().upper().replace("*","")
                if "Reason:" in line: reason = line.split(":")[1].strip()
            
            if "SUPPORT" in status: status = "SUPPORTED"
            elif "CONTRADICT" in status: status = "CONTRADICTED"
            else: status = "INCONCLUSIVE"
            results.append({"claim": c['claim'], "status": status, "reason": reason})
        except:
            results.append({"claim": c['claim'], "status": "INCONCLUSIVE", "reason": "API Error."})
            
        p_bar.progress((i+1)/len(claims))
    p_bar.empty()
    return results

def generate_report(results, model):
    try:
        data = "\n".join([f"- {r['claim']} ({r['status']})" for r in results])
        return model.generate_content(f"Write a short, high-tech intel summary of these findings:\n{data}").text
    except: return "Summary generation failed."

# --- 6. MAIN UI ---
st.markdown("""<div style="text-align: center; margin-bottom: 50px;"><h1 style="font-size: 4.5rem;">VERITAS AI</h1></div>""", unsafe_allow_html=True)
c1, c2 = st.columns([5, 1], gap="small")
with c1: 
    # Updated Placeholder to indicate both URL and Text support
    user_input = st.text_input("", placeholder="PASTE URL OR RAW TEXT...", label_visibility="collapsed")
with c2: 
    btn = st.button("INITIALIZE")

if btn and user_input:
    with st.spinner("⚡ ESTABLISHING NEURAL LINK..."):
        all_claims = extract_claims(user_input, model)
    
    if all_claims:
        claims_to_check = all_claims[:max_claims]
        
        st.markdown(f"### /// ANALYSIS MATRIX ({len(claims_to_check)} CLAIMS)")
        results = process_claims(claims_to_check, model)
        
        for r in results:
            col = "#00ff88" if r['status'] == "SUPPORTED" else "#ff0055" if r['status'] == "CONTRADICTED" else "#ffcc00"
            st.markdown(f"""
            <div class="neural-card" style="border-left: 3px solid {col};">
                <div style="color:{col};font-weight:900; letter-spacing:1px; margin-bottom:8px;">[{r['status']}]</div>
                <div style="color:#e0f0ff;font-size:1.1rem; margin-bottom:12px;">"{r['claim']}"</div>
                <div style="background:rgba(0,0,0,0.3); padding:10px; border-radius:5px; color:#8899aa; font-size:0.9rem;">
                    > {r['reason']}
                </div>
            </div>""", unsafe_allow_html=True)
            
        summary = generate_report(results, model)
        st.markdown(f"""
        <div style="margin-top: 40px; border: 1px solid #005577; padding: 25px; background: rgba(2, 5, 10, 0.9); border-radius: 12px;">
            <div style="color: #00f2ff; font-family: 'Orbitron'; margin-bottom: 10px; letter-spacing: 1px;">>> INTELLIGENCE SUMMARY</div>
            <div style="color: #aaddff; line-height: 1.6;">{summary}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.error("NO DATA DETECTED. The input may be empty or unreadable.")