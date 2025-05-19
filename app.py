import streamlit as st
import subprocess
import os
import re
from pinecone import Pinecone, ServerlessSpec
import tempfile
from dotenv import load_dotenv
import random
import time
import hashlib
from config import CONFIG, costs_per_min

# Load environment variables
load_dotenv()

# Set page config first thing
st.set_page_config(
    page_title="Livekit Telephonic Agent",
    page_icon="📞",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
    <style>
        .main-header {
            background: linear-gradient(90deg, #46d4e5 0%, #4e08c7 100%);
            border-radius: 10px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            padding: 1rem;
            margin-bottom: 1rem
        }   
        .block-container {
            padding-top: 4rem;
            padding-bottom: 0rem;
        }
        div.stButton > button {
            width: 100%;
        }
        div[data-testid="stDataFrameResizable"] {
            overflow: auto;
        }
        .config-title {
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid #e0e0e0;
        }
        .cost-badge {
            background: rgba(255, 255, 255, 0.2);
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-weight: 700;
            backdrop-filter: blur(10px);
        }
        div[data-testid="stFileUploader"] {
            padding: 1rem;
            border-radius: 8px;
            border: 2px dashed #cbd5e1;
        }
    </style>
""", unsafe_allow_html=True)

# Helper function to beautify names
def beautify_name(name):
    if not name or ":" not in name:
        return name
    provider, model = name.split(":", 1)
    return f"{model} ({provider.upper() if provider == "iitm" else provider.capitalize()})"

# Format functions with badge-like cost display
def format_stt_model(name):
    cost = costs_per_min["STT"].get(name, None)
    display_name = beautify_name(name)
    return f"{display_name} - [{'$'+str(cost)+'/min' if cost is not None else 'Cost N/A'}]"

def format_llm_model(name):
    cost = costs_per_min["LLM"].get(name, None)
    display_name = beautify_name(name)
    return f"{display_name} - [{'$'+str(cost)+'/min' if cost is not None else 'Cost N/A'}]"

def format_tts_voice(name):
    provider = st.session_state.tts_provider
    cost = costs_per_min["TTS"].get(provider, None)
    display_name = beautify_name(name)
    return f"{display_name} - [{'$'+str(cost)+'/min' if cost is not None else 'Cost N/A'}]"

# User Authentication System
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user' not in st.session_state:
    st.session_state.user = None
if 'users_db' not in st.session_state:
    st.session_state.users_db = {
        "admin@gmail.com": {
            "password": hashlib.sha256("admin123".encode()).hexdigest(),
            "name": "Admin User",
            "role": "admin"
        },
        "user@gmail.com": {
            "password": hashlib.sha256("user123".encode()).hexdigest(),
            "name": "Demo User",
            "role": "user"
        }
    }

def authenticate(username, password):
    if username in st.session_state.users_db:
        stored_password = st.session_state.users_db[username]["password"]
        hashed_input_pwd = hashlib.sha256(password.encode()).hexdigest()
        if stored_password == hashed_input_pwd:
            st.session_state.authenticated = True
            st.session_state.user = {
                "email": username,
                "name": st.session_state.users_db[username]["name"],
                "role": st.session_state.users_db[username]["role"]
            }
            return True
    return False

def logout():
    st.session_state.authenticated = False
    st.session_state.user = None
    st.rerun()

# Show login page if not authenticated
if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
            <div style="text-align: center;">
                <h2>📞 Livekit Telephonic Agent</h2>
                <p style="color: #64748b;">Please log in to access the application</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.container():
            with st.form("login_form"):
                username = st.text_input("📧 Email", placeholder="Enter your email")
                password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
                login_button = st.form_submit_button("🚀 Login", use_container_width=True)
                
                if login_button:
                    if authenticate(username, password):
                        st.success("✅ Login successful!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid email or password")
else:
    # Initialize Pinecone
    api_key = os.getenv("PINECONE_API_KEY")
    pc = Pinecone(api_key=api_key)
    INDEX_NAME = "parameters"
    VECTOR_DIMENSION = 384
    DUMMY_VECTOR = [0.5] * VECTOR_DIMENSION
    if not pc.has_index(INDEX_NAME):
        pc.create_index(
            name=INDEX_NAME,
            dimension=VECTOR_DIMENSION,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
    index = pc.Index(INDEX_NAME)
    assistant = pc.assistant.Assistant(assistant_name="test-rag")

    # Provider-dependent model mappings
    PROVIDER_MODEL_MAPPING = {
        "STT": {
            "azure": [model for model in CONFIG["STT"]["model"]["enum"] if model.startswith("azure:")],
            "sarvam": [model for model in CONFIG["STT"]["model"]["enum"] if model.startswith("sarvam:")],
            "deepgram": [model for model in CONFIG["STT"]["model"]["enum"] if model.startswith("deepgram:")],
            "google": [model for model in CONFIG["STT"]["model"]["enum"] if model.startswith("google:")],
            "openai": [model for model in CONFIG["STT"]["model"]["enum"] if model.startswith("openai:")],
            "iitm": [model for model in CONFIG["STT"]["model"]["enum"] if model.startswith("iitm:")],
        },
        "LLM": {
            "openai": [model for model in CONFIG["LLM"]["model"]["enum"] if model.startswith("openai:")],
            "deepseek": [model for model in CONFIG["LLM"]["model"]["enum"] if model.startswith("deepseek:")],
            "google": [model for model in CONFIG["LLM"]["model"]["enum"] if model.startswith("google:")]
        },
        "TTS": {
            "azure": [voice for voice in CONFIG["TTS"]["voice"]["enum"] if voice.startswith("azure:")],
            "sarvam": [voice for voice in CONFIG["TTS"]["voice"]["enum"] if voice.startswith("sarvam:")],
            "elevenlabs": [voice for voice in CONFIG["TTS"]["voice"]["enum"] if voice.startswith("elevenlabs:")],
            "cartesia": [voice for voice in CONFIG["TTS"]["voice"]["enum"] if voice.startswith("cartesia:")],
        }
    }

    # Language mapping
    LANGUAGE_MAPPING = {
        'bn-IN': 'Bengali', 'en-IN': 'English', 'en-US': 'English (US)', 'gu-IN': 'Gujarati',
        'hi-IN': 'Hindi', 'kn-IN': 'Kannada', 'ml-IN': 'Malayalam', 'mr-IN': 'Marathi',
        'od-IN': 'Odia', 'pa-IN': 'Punjabi', 'ta-IN': 'Tamil', 'te-IN': 'Telugu'
    }

    # Initialize session state
    if "stt_provider" not in st.session_state:
        st.session_state.stt_provider = CONFIG["STT"]["provider"]["enum"][0]
    if "stt_model_select" not in st.session_state:
        default_models = PROVIDER_MODEL_MAPPING["STT"][st.session_state.stt_provider]
        st.session_state.stt_model_select = default_models[0] if default_models else ""
    if "stt_language_select" not in st.session_state:
        default_langs = CONFIG["STT"]["language"][st.session_state.stt_provider]
        st.session_state.stt_language_select = default_langs[0] if default_langs else ""

    if "llm_provider" not in st.session_state:
        st.session_state.llm_provider = CONFIG["LLM"]["provider"]["enum"][0]
    if "llm_model_select" not in st.session_state:
        default_models = PROVIDER_MODEL_MAPPING["LLM"][st.session_state.llm_provider]
        st.session_state.llm_model_select = default_models[0] if default_models else ""

    if "tts_provider" not in st.session_state:
        st.session_state.tts_provider = CONFIG["TTS"]["provider"]["enum"][0]
    if "tts_provider_select" not in st.session_state:
        st.session_state.tts_provider_select = st.session_state.tts_provider
    if "tts_language_select" not in st.session_state:
        default_langs = CONFIG["TTS"]["language"][st.session_state.tts_provider]
        st.session_state.tts_language_select = default_langs[0] if default_langs else ""
    if "tts_voice_select" not in st.session_state:
        default_voices = PROVIDER_MODEL_MAPPING["TTS"][st.session_state.tts_provider]
        st.session_state.tts_voice_select = default_voices[0] if default_voices else ""

    # TTS helper functions
    def extract_lang_from_voice(voice: str, provider: str) -> str:
        _, rest = voice.split(":", 1)
        prefix = rest.split("-")[0]
        return prefix if provider == "azure" and "-" in prefix else f"{prefix}-IN"

    def update_tts_provider():
        st.session_state.tts_provider = st.session_state.tts_provider_select
        for key in ["tts_voice_select", "tts_language_select"]:
            if key in st.session_state:
                del st.session_state[key]

    def update_tts_language():
        provider = st.session_state.tts_provider
        lang = st.session_state.tts_language_select
        voices = PROVIDER_MODEL_MAPPING["TTS"][provider]
        if provider in ("azure", "elevenlabs", "cartesia"):
            code = lang
            short = code.split("-")[0]
            pattern = re.compile(rf"^{provider}:{short}(-|_)")
            filtered = [v for v in voices if pattern.search(v)]
            st.session_state.tts_voice_select = filtered[0] if filtered else voices[0]

    def update_tts_voice():
        provider = st.session_state.tts_provider
        voice = st.session_state.tts_voice_select
        if provider in ("azure", "elevenlabs", "cartesia"):
            st.session_state.tts_language_select = extract_lang_from_voice(voice, provider)

    def validate_phone_number(phone):
        return bool(re.match(r'^\+91\d{10}$', phone))

    # Calculate total cost
    stt_cost = costs_per_min["STT"].get(st.session_state.get('stt_model_select', ''), None)
    llm_cost = costs_per_min["LLM"].get(st.session_state.get('llm_model_select', ''), None)
    tts_cost = costs_per_min["TTS"].get(st.session_state.get('tts_provider', ''), None)
    costs = [stt_cost, llm_cost, tts_cost]
    cost_display = f"${sum(costs):.4f}/min" if all(c is not None for c in costs) else "N/A"

    # SIDEBAR - File Upload and User Info
    with st.sidebar:
        # st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("### 📄 Knowledge Base Management")
        
        # File Upload
        uploaded_file = st.file_uploader(
            "Upload documents for the agent",
            type=["txt", "pdf", "docx", "md"],
            help="Upload documents to be used by the agent"
        )
        
        upload_button = st.button("📤 Upload", use_container_width=True)
        
        if upload_button:
            if uploaded_file is not None:
                with tempfile.TemporaryDirectory() as tmpdirname:
                    original_filename = uploaded_file.name
                    file_path = os.path.join(tmpdirname, original_filename)
                    with open(file_path, 'wb') as f:
                        f.write(uploaded_file.getvalue())
                    try:
                        with st.spinner(f"Uploading {original_filename}..."):
                            response = assistant.upload_file(file_path=file_path)
                            st.success(f"✅ Uploaded '{original_filename}'")
                    except Exception as e:
                        st.error(f"❌ Error uploading file: {str(e)}")
            else:
                st.warning("Please select a file to upload.")
        
        
        # Uploaded Files List
        st.markdown("#### 📋 Uploaded Files")
        try:
            with st.spinner("Loading files..."):
                files = assistant.list_files()
                if files:
                    for file in files:
                        with st.container():
                            col1, col2 = st.columns([2, 1], vertical_alignment="center")
                            with col1:
                                status_color = "🟢" if file.status in ["Available"] else "🟡"
                                st.markdown(f"{status_color} **{file.name if len(file.name) <= 10 else file.name[:8] + '...'}**"
)
                            with col2:
                                if st.button("Delete", key=f"delete_{file.id}", help="Delete file"):
                                    try:
                                        with st.spinner(f"Deleting {file.name}..."):
                                            assistant.delete_file(file.id)
                                            st.success(f"Deleted '{file.name}'")
                                            st.rerun()
                                    except Exception as e:
                                        st.error(f"Error deleting file: {str(e)}")
                else:
                    st.info("No files uploaded yet.")
        except Exception as e:
            st.error(f"Error listing files: {str(e)}")
        
        # User Info at Bottom
        st.markdown(f"**👤 {st.session_state.user['name']}**")
        if st.button("🚪 Logout", type="primary", use_container_width=True):
            logout()

    # MAIN CONTENT
    # Header
    st.markdown("""
        <div class="main-header">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h1>📞 Livekit Telephonic Agent</h1>
                <div class="cost-badge">
                    💰 Total Cost: {cost_display}
                </div>
            </div>
        </div>
    """.format(cost_display=cost_display), unsafe_allow_html=True)

    # Phone Number Input and Call Initiation
    # st.markdown("### 📱 Call Initiation")
    
    col1, col2 = st.columns([3, 1], vertical_alignment="bottom")
    with col1:
        phone_number = st.text_input(
            "Reciever Phone Number",
            placeholder="+91XXXXXXXXXX",
        )
    with col2:
        initiate_call = st.button("📞 Initiate Call", type="primary", use_container_width=True)
    

    # Configuration Tabs
    tab1, tab2, tab3 = st.tabs(["🤖 LLM Configuration", "🎤 STT Configuration", "🔊 TTS Configuration"])

    # LLM Tab
    with tab1:
        # First Message Input
        st.markdown("##### 💬 First Message")
        first_message = st.text_input(
            "Enter the first message that will be spoken to the user when they pickup the call",
            placeholder="Hello! This is your assistant. How can I help you today?",
            key="first_message"
        )
        
        # System Prompt
        st.markdown("##### 📋 System Prompt")
        llm_system_prompt = st.text_area(
            "Enter instructions for the AI assistant",
            placeholder="You are a helpful assistant...",
            height=200,
            help=CONFIG["LLM"]["system_prompt"]["description"],
            key="llm_system_prompt"
        )
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            def update_llm_provider():
                st.session_state.llm_provider = st.session_state.llm_provider_select
            llm_provider = st.selectbox(
                "🏢 Provider",
                options=CONFIG["LLM"]["provider"]["enum"],
                format_func=lambda x: x.capitalize(),
                key="llm_provider_select",
                on_change=update_llm_provider
            )
        with col2:
            llm_model_options = PROVIDER_MODEL_MAPPING["LLM"][st.session_state.llm_provider]
            llm_model = st.selectbox(
                "🧠 Model",
                options=llm_model_options,
                format_func=format_llm_model,
                key="llm_model_select"
            )
        with col3:
            llm_temperature = st.slider(
                "🌡️ Temperature",
                min_value=CONFIG["LLM"]["temperature"]["minimum"],
                max_value=CONFIG["LLM"]["temperature"]["maximum"],
                value=0.5,
                step=0.01,
                help=CONFIG["LLM"]["temperature"]["description"],
                key="llm_temperature"
            )
    

    # STT Tab
    with tab2:
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            def update_stt_provider():
                st.session_state.stt_provider = st.session_state.stt_provider_select
                if 'stt_language_select' in st.session_state:
                    st.session_state.pop('stt_language_select')
            stt_provider = st.selectbox(
                "🏢 Provider",
                options=CONFIG["STT"]["provider"]["enum"],
                format_func=lambda x: x.upper() if x == "iitm" else x.capitalize(),
                key="stt_provider_select",
                on_change=update_stt_provider
            )
        with col2:
            stt_model_options = PROVIDER_MODEL_MAPPING["STT"][st.session_state.stt_provider]
            stt_model = st.selectbox(
                "🎯 Model",
                options=stt_model_options,
                format_func=format_stt_model,
                key="stt_model_select"
            )
        with col3:
            available_stt_languages = CONFIG["STT"]["language"][st.session_state.stt_provider]
            stt_language = st.selectbox(
                "🌐 Language",
                options=available_stt_languages,
                format_func=lambda x: LANGUAGE_MAPPING.get(x, x),
                key="stt_language_select"
            )


    # TTS Tab
    with tab3:
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            tts_provider = st.selectbox(
                "🏢 Provider",
                options=CONFIG["TTS"]["provider"]["enum"],
                format_func=lambda x: x.capitalize(),
                key="tts_provider_select",
                on_change=update_tts_provider
            )
        with col2:
            available_tts_languages = CONFIG["TTS"]["language"][st.session_state.tts_provider]
            tts_language = st.selectbox(
                "🌐 Language",
                options=available_tts_languages,
                format_func=lambda x: LANGUAGE_MAPPING.get(x, x),
                key="tts_language_select",
                on_change=update_tts_language
            )
        with col3:
            all_voices = PROVIDER_MODEL_MAPPING["TTS"][st.session_state.tts_provider]
            if st.session_state.tts_provider in ("azure", "elevenlabs", "cartesia"):
                lang = st.session_state.tts_language_select
                short = lang.split("-")[0]
                regex = re.compile(rf"^{st.session_state.tts_provider}:{short}(-|_)")
                voice_options = [v for v in all_voices if regex.search(v)]
            else:
                voice_options = all_voices
            tts_voice = st.selectbox(
                "🎵 Voice",
                options=voice_options,
                format_func=format_tts_voice,
                key="tts_voice_select",
                on_change=update_tts_voice
            )

    # Handle Call Initiation
    if initiate_call:
        if not phone_number or not st.session_state.get('first_message'):
            st.error("❌ Please fill in the phone number and first message")
        elif not validate_phone_number(phone_number):
            st.error("❌ Invalid phone number format. Please enter a valid Indian phone number starting with +91 followed by 10 digits.")
        else:
            try:
                metadata = {
                    'phone_number': phone_number,
                    'first_message': st.session_state.get('first_message'),
                    'STT_provider': st.session_state.stt_provider,
                    'STT_model': stt_model.split("sarvam:")[-1] if stt_model.startswith("sarvam") else stt_model.split(":")[-1],
                    'STT_language': stt_language,
                    'LLM_provider': st.session_state.llm_provider,
                    'LLM_model': llm_model.split(":")[-1],
                    'LLM_system_prompt': st.session_state.get('llm_system_prompt', ''),
                    'LLM_temperature': llm_temperature,
                    'TTS_provider': st.session_state.tts_provider,
                    'TTS_voice': tts_voice.split(":")[-1],
                    'TTS_language': tts_language,
                }
                vector_id = f"call-{phone_number}-{int(time.time())}-{random.randint(100000, 999999)}"
                
                st.success("✅ Call configured successfully!")
                
                with st.expander("📊 Review Configuration"):
                    st.json(metadata)
                
                with st.spinner("📤 Sending call metadata..."):
                    index.upsert(
                        vectors=[{"id": vector_id, "values": DUMMY_VECTOR, "metadata": metadata}],
                        namespace=""
                    )
                    time.sleep(3)
                
                command = f'lk dispatch create --new-room --agent-name "teliphonic-rag-agent-test" --metadata "{vector_id}"'
                try:
                    with st.spinner("📞 Initiating call..."):
                        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        stdout, stderr = process.communicate()
                        if process.returncode == 0:
                            st.success("🎉 Call initiated successfully!")
                            with st.expander("📋 Command output"):
                                st.code(stdout.decode())
                        else:
                            st.error("❌ Error initiating call:")
                            st.code(stderr.decode())
                except Exception as e:
                    st.error(f"❌ An error occurred while executing command: {str(e)}")
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")

    # Footer
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: #64748b; padding: 1rem 0;'>
            <strong>Livekit Telephonic Agent System</strong> • v1.0.0 • 
            Powered by 💜 Sample Set
        </div>
    """, unsafe_allow_html=True)