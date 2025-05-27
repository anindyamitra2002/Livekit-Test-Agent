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
    page_title="StackVoice Telephonic Agent",
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
    return f"{model} ({provider.upper() + '(Experimental)' if provider == 'iitm' else provider.capitalize()})"

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
                <h2>📞 StackVoice Telephonic Agent</h2>
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
            # "google": [model for model in CONFIG["STT"]["model"]["enum"] if model.startswith("google:")],
            "openai": [model for model in CONFIG["STT"]["model"]["enum"] if model.startswith("openai:")],
            "iitm": [model for model in CONFIG["STT"]["model"]["enum"] if model.startswith("iitm:")],
            "groq": [model for model in CONFIG["STT"]["model"]["enum"] if model.startswith("groq:")],
        },
        "LLM": {
            "openai": [model for model in CONFIG["LLM"]["model"]["enum"] if model.startswith("openai:")],
            # "deepseek": [model for model in CONFIG["LLM"]["model"]["enum"] if model.startswith("deepseek:")],
            # "google": [model for model in CONFIG["LLM"]["model"]["enum"] if model.startswith("google:")],
            # "groq": [model for model in CONFIG["LLM"]["model"]["enum"] if model.startswith("groq:")],
            "togetherai": [model for model in CONFIG["LLM"]["model"]["enum"] if model.startswith("togetherai:")],
        },
        "TTS": {
            "azure": [voice for voice in CONFIG["TTS"]["voice"]["enum"] if voice.startswith("azure:")],
            "sarvam": [voice for voice in CONFIG["TTS"]["voice"]["enum"] if voice.startswith("sarvam:")],
            "elevenlabs": [voice for voice in CONFIG["TTS"]["voice"]["enum"] if voice.startswith("elevenlabs:")],
            "cartesia": [voice for voice in CONFIG["TTS"]["voice"]["enum"] if voice.startswith("cartesia:")],
            "groq": [voice for voice in CONFIG["TTS"]["voice"]["enum"] if voice.startswith("groq:")],
        }
    }

    # Language mapping
    LANGUAGE_MAPPING = {
        'bn-IN': 'Bengali', 'en-IN': 'English', 'en-US': 'English (US)', 'gu-IN': 'Gujarati',
        'hi-IN': 'Hindi', 'kn-IN': 'Kannada', 'ml-IN': 'Malayalam', 'mr-IN': 'Marathi',
        'od-IN': 'Odia', 'pa-IN': 'Punjabi', 'ta-IN': 'Tamil', 'te-IN': 'Telugu'
    }

    def _rerun():
        # Calculate total cost
        stt_cost = costs_per_min["STT"].get(st.session_state.stt_model_select, None)
        llm_cost = costs_per_min["LLM"].get(st.session_state.llm_model_select, None)
        tts_cost = costs_per_min["TTS"].get(st.session_state.tts_provider, None)
        print(st.session_state.stt_model_select, st.session_state.llm_model_select, st.session_state.tts_provider)
        costs = [stt_cost, llm_cost, tts_cost]
        cost_display = f"${sum(costs):.4f}/min" if all(c is not None for c in costs) else "N/A"
        st.session_state.cost_display = cost_display
    
    def get_models_for_language_provider(component: str, language: str, provider: str) -> list:
        """Get list of models/voices that support a given language and provider."""
        if component == "STT":
            return PROVIDER_MODEL_MAPPING[component][provider]
        else:  # TTS
            all_voices = PROVIDER_MODEL_MAPPING[component][provider]
            if provider in ("azure", "elevenlabs", "cartesia"):
                short = language.split("-")[0]
                pattern = re.compile(rf"^{provider}:{short}(-|_)")
                return [v for v in all_voices if pattern.search(v)]
            return all_voices
    
    def update_llm_provider():
        """Update LLM model when provider changes."""
        st.session_state.llm_provider = st.session_state["llm_provider_select"]
        # Update model selection based on new provider
        default_models = PROVIDER_MODEL_MAPPING["LLM"][st.session_state.llm_provider]
        st.session_state.llm_model_select = default_models[0] if default_models else ""
        _rerun()

    def update_llm_model():
        """Update price when LLM model changes."""
        _rerun()

    def update_stt_provider():
        st.session_state.stt_provider = st.session_state["stt_provider_select"]
        # Update model selection based on new provider and language
        if st.session_state.stt_provider:
            stt_model_options = get_models_for_language_provider(
                "STT",
                st.session_state.stt_language_select,
                st.session_state.stt_provider
            )
            st.session_state.stt_model_select = stt_model_options[0] if stt_model_options else ""
        _rerun()

    def update_tts_provider():
        st.session_state.tts_provider = st.session_state["tts_provider_select"]
        # Update voice selection based on new provider and language
        if st.session_state.tts_provider:
            voice_options = get_models_for_language_provider(
                "TTS",
                st.session_state.tts_language_select,
                st.session_state.tts_provider
            )
            st.session_state.tts_voice_select = voice_options[0] if voice_options else ""
        _rerun()

    def update_tts_voice():
        provider = st.session_state["tts_provider"]
        voice = st.session_state["tts_voice_select"]
        if provider in ("azure", "elevenlabs", "cartesia"):
            st.session_state["tts_language_select"] = extract_lang_from_voice(voice, provider)
        _rerun()

    def extract_lang_from_voice(voice: str, provider: str) -> str:
        try:
            if not voice or ":" not in voice:
                return st.session_state.tts_language_select
            _, rest = voice.split(":", 1)
            prefix = rest.split("-")[0]
            return prefix if provider == "azure" and "-" in prefix else f"{prefix}-IN"
        except Exception:
            return st.session_state.tts_language_select

    # Initialize session state with default values
    def initialize_default_values():
        # STT defaults
        all_stt_languages = set()
        for provider in CONFIG["STT"]["provider"]["enum"]:
            all_stt_languages.update(CONFIG["STT"]["language"][provider])
        default_stt_lang = sorted(list(all_stt_languages))[0] if all_stt_languages else ""
        
        # Get first provider that supports the default language
        default_stt_provider = next(
            (p for p in CONFIG["STT"]["provider"]["enum"] 
             if default_stt_lang in CONFIG["STT"]["language"][p]),
            CONFIG["STT"]["provider"]["enum"][0]
        )
        
        # Get first model for the default provider
        default_stt_model = PROVIDER_MODEL_MAPPING["STT"][default_stt_provider][0] if PROVIDER_MODEL_MAPPING["STT"][default_stt_provider] else ""

        # TTS defaults
        all_tts_languages = set()
        for provider in CONFIG["TTS"]["provider"]["enum"]:
            all_tts_languages.update(CONFIG["TTS"]["language"][provider])
        default_tts_lang = sorted(list(all_tts_languages))[0] if all_tts_languages else ""
        
        # Get first provider that supports the default language
        default_tts_provider = next(
            (p for p in CONFIG["TTS"]["provider"]["enum"] 
             if default_tts_lang in CONFIG["TTS"]["language"][p]),
            CONFIG["TTS"]["provider"]["enum"][0]
        )
        
        # Get first voice for the default provider and language
        default_tts_voice = get_models_for_language_provider("TTS", default_tts_lang, default_tts_provider)[0] if get_models_for_language_provider("TTS", default_tts_lang, default_tts_provider) else ""

        return {
            "stt_language_select": default_stt_lang,
            "stt_provider": default_stt_provider,
            "stt_provider_select": default_stt_provider,
            "stt_model_select": default_stt_model,
            "tts_language_select": default_tts_lang,
            "tts_provider": default_tts_provider,
            "tts_provider_select": default_tts_provider,
            "tts_voice_select": default_tts_voice
        }

    # Initialize session state
    if "stt_provider" not in st.session_state:
        defaults = initialize_default_values()
        for key, value in defaults.items():
            st.session_state[key] = value

    if "llm_provider" not in st.session_state:
        st.session_state.llm_provider = CONFIG["LLM"]["provider"]["enum"][0]
    if "llm_model_select" not in st.session_state:
        default_models = PROVIDER_MODEL_MAPPING["LLM"][st.session_state.llm_provider]
        st.session_state.llm_model_select = default_models[0] if default_models else ""
    if "cost_display" not in st.session_state:
        st.session_state.cost_display = "N/A"

    _rerun()  # Initial cost calculation
    # TTS helper functions
    def validate_phone_number(phone):
        return bool(re.match(r'^\+91\d{10}$', phone))

    # Helper functions for language-based provider selection
    def get_providers_for_language(component: str, language: str) -> list:
        """Get list of providers that support a given language for a component."""
        providers = []
        for provider in CONFIG[component]["provider"]["enum"]:
            if language in CONFIG[component]["language"][provider]:
                providers.append(provider)
        return providers

    def update_stt_language():
        """Update STT provider and model when language changes."""
        # Get providers that support the new language
        available_providers = get_providers_for_language("STT", st.session_state.stt_language_select)
        if available_providers:
            # Set the first available provider
            st.session_state.stt_provider = available_providers[0]
            st.session_state.stt_provider_select = available_providers[0]
            # Update model selection
            stt_model_options = get_models_for_language_provider(
                "STT",
                st.session_state.stt_language_select,
                st.session_state.stt_provider
            )
            if stt_model_options:
                st.session_state.stt_model_select = stt_model_options[0]
        _rerun()

    def update_tts_language():
        """Update TTS provider and voice when language changes."""
        # Get providers that support the new language
        available_providers = get_providers_for_language("TTS", st.session_state.tts_language_select)
        if available_providers:
            # Set the first available provider
            st.session_state.tts_provider = available_providers[0]
            st.session_state.tts_provider_select = available_providers[0]
            # Update voice selection
            voice_options = get_models_for_language_provider(
                "TTS",
                st.session_state.tts_language_select,
                st.session_state.tts_provider
            )
            if voice_options:
                st.session_state.tts_voice_select = voice_options[0]
        _rerun()

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
                <h1>📞 StackVoice Telephonic Agent</h1>
                <div class="cost-badge">
                    💰 Total Cost: {cost_display}
                </div>
            </div>
        </div>
    """.format(cost_display=st.session_state.cost_display), unsafe_allow_html=True)

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
    tab1, tab2, tab3, tab4 = st.tabs(["🤖 LLM Configuration", "🎤 STT Configuration", "🔊 TTS Configuration", "⚙️ Additional Settings"])

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
            llm_provider = st.selectbox(
                "🏢 Provider",
                options=CONFIG["LLM"]["provider"]["enum"],
                format_func=lambda x: x.capitalize(),
                key="llm_provider_select",
                index=0,
                on_change=update_llm_provider
            )
        with col2:
            llm_model_options = PROVIDER_MODEL_MAPPING["LLM"][st.session_state.llm_provider]
            llm_model = st.selectbox(
                "🧠 Model",
                options=llm_model_options,
                format_func=format_llm_model,
                key="llm_model_select",
                index=0,
                on_change=update_llm_model
            )
        with col3:
            llm_temperature = st.slider(
                "🌡️ Temperature",
                min_value=CONFIG["LLM"]["temperature"]["minimum"],
                max_value=CONFIG["LLM"]["temperature"]["maximum"],
                value=0.5,
                step=0.01,
                help=CONFIG["LLM"]["temperature"]["description"],
                key="llm_temperature",
                on_change=_rerun
            )
    

    # STT Tab
    with tab2:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            # Get all available languages across all providers
            all_stt_languages = set()
            for provider in CONFIG["STT"]["provider"]["enum"]:
                all_stt_languages.update(CONFIG["STT"]["language"][provider])
            stt_language = st.selectbox(
                "🌐 Language",
                options=sorted(list(all_stt_languages)),
                format_func=lambda x: LANGUAGE_MAPPING.get(x, x),
                key="stt_language_select",
                on_change=lambda: update_stt_language()
            )
        with col2:
            # Get providers that support the selected language
            available_providers = get_providers_for_language("STT", st.session_state.stt_language_select)
            stt_provider = st.selectbox(
                "🏢 Provider",
                options=available_providers,
                format_func=lambda x: x.upper() + '(Experimental)' if x == "iitm" else x.capitalize(),
                key="stt_provider_select",
                index=0,
                on_change=update_stt_provider
            )
        with col3:
            stt_model_options = get_models_for_language_provider(
                "STT", 
                st.session_state.stt_language_select,
                st.session_state.stt_provider
            ) if st.session_state.stt_provider else []
            stt_model = st.selectbox(
                "🎯 Model",
                options=stt_model_options,
                format_func=format_stt_model,
                key="stt_model_select",
                index=0,
                on_change=_rerun
            )

    # TTS Tab
    with tab3:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            # Get all available languages across all providers
            all_tts_languages = set()
            for provider in CONFIG["TTS"]["provider"]["enum"]:
                all_tts_languages.update(CONFIG["TTS"]["language"][provider])
            tts_language = st.selectbox(
                "🌐 Language",
                options=sorted(list(all_tts_languages)),
                format_func=lambda x: LANGUAGE_MAPPING.get(x, x),
                key="tts_language_select",
                on_change=lambda: update_tts_language()
            )
        with col2:
            # Get providers that support the selected language
            available_providers = get_providers_for_language("TTS", st.session_state.tts_language_select)
            tts_provider = st.selectbox(
                "🏢 Provider",
                options=available_providers,
                format_func=lambda x: x.capitalize(),
                key="tts_provider_select",
                index=0,
                on_change=update_tts_provider
            )
        with col3:
            voice_options = get_models_for_language_provider(
                "TTS",
                st.session_state.tts_language_select,
                st.session_state.tts_provider
            ) if st.session_state.tts_provider else []
            tts_voice = st.selectbox(
                "🎵 Voice",
                options=voice_options,
                format_func=format_tts_voice,
                key="tts_voice_select",
                index=0,
                on_change=update_tts_voice
            )

        # Show warning if STT and TTS languages don't match
        if 'stt_language_select' in st.session_state and 'tts_language_select' in st.session_state:
            if st.session_state.stt_language_select != st.session_state.tts_language_select:
                st.warning("⚠️ Warning: STT and TTS languages do not match. This may affect the conversation quality.")

    # Additional Settings Tab
    with tab4:
        st.markdown("##### 🛠️ Agent Configuration")
        
        # Create a container for better styling
        with st.container():
            # Use columns for better layout
            col1, col2 = st.columns(2)
            
            with col1:
                use_retrieval = st.checkbox(
                    "📚 Use Knowledge Base",
                    value=False,
                    help="Enable the agent to use uploaded documents for answering questions",
                    key="use_retrieval"
                )
                
                auto_end_call = st.checkbox(
                    "⏱️ Auto End Call",
                    value=False,
                    help="Automatically end the call after a period of silence",
                    key="auto_end_call"
                )

                is_allow_interruptions = st.checkbox(
                    "🗣️ Allow Interruptions",
                    value=True,
                    help="Allow the user to interrupt the agent while it's speaking",
                    key="is_allow_interruptions"
                )
            
            with col2:
                background_sound = st.checkbox(
                    "🎵 Enable Background Sound",
                    value=True,
                    help="Add office noise backgroundsound during the call",
                    key="background_sound"
                )

                vad_min_silence = st.slider(
                    "🔇 Minimum Silence Duration (seconds)",
                    min_value=0.0,
                    max_value=3.0,
                    value=0.65,
                    step=0.01,
                    help="Minimum duration of silence required to detect end of speech",
                    key="vad_min_silence"
                )

    # Handle Call Initiation
    if initiate_call:
        if not phone_number or not st.session_state.get('first_message'):
            st.error("❌ Please fill in the phone number and first message")
        elif not validate_phone_number(phone_number):
            st.error("❌ Invalid phone number format. Please enter a valid Indian phone number starting with +91 followed by 10 digits.")
        else:
            try:
                # Calculate costs
                stt_cost = costs_per_min["STT"].get(st.session_state.stt_model_select, None)
                llm_cost = costs_per_min["LLM"].get(st.session_state.llm_model_select, None)
                tts_cost = costs_per_min["TTS"].get(st.session_state.tts_provider, None)
                costs = [stt_cost, llm_cost, tts_cost]
                cost_display = f"${sum(costs):.4f}/min" if all(c is not None for c in costs) else "N/A"
                st.session_state.cost_display = cost_display

                metadata = {
                    'phone_number': phone_number,
                    'first_message': st.session_state.get('first_message'),
                    'STT_provider': st.session_state.stt_provider,
                    'STT_model': stt_model.split("sarvam:")[-1] if stt_model.startswith("sarvam") else stt_model.split(":")[-1],
                    'STT_language': stt_language,
                    'STT_cost_per_min': stt_cost,
                    'LLM_provider': st.session_state.llm_provider,
                    'LLM_model': llm_model.split(":")[-1],
                    'LLM_system_prompt': st.session_state.get('llm_system_prompt', ''),
                    'LLM_temperature': llm_temperature,
                    'LLM_cost_per_min': llm_cost,
                    'TTS_provider': st.session_state.tts_provider,
                    'TTS_voice': tts_voice.split(":")[-1],
                    'TTS_language': tts_language,
                    'TTS_cost_per_min': tts_cost,
                    'total_cost_per_min': sum(costs) if all(c is not None for c in costs) else None,
                    # Add new configuration options
                    'use_retrieval': st.session_state.get('use_retrieval', False),
                    'auto_end_call': st.session_state.get('auto_end_call', False),
                    'background_sound': st.session_state.get('background_sound', False),
                    'vad_min_silence': st.session_state.get('vad_min_silence', 0.65),
                    'is_allow_interruptions': st.session_state.get('is_allow_interruptions', False),
                }
                
                vector_id = f"call-{phone_number}-{int(time.time())}-{random.randint(100000, 999999)}"
                
                st.success("✅ Call configured successfully!")
                
                with st.expander("📊 Review Configuration"):
                    st.json(metadata)
                    
                data_verified = False
                with st.spinner("📤 Sending call metadata..."):
                    index.upsert(
                        vectors=[{"id": vector_id, "values": DUMMY_VECTOR, "metadata": metadata}],
                        namespace=""
                    )
                    
                    # Verify data was stored successfully
                    max_retries = 15
                    retry_count = 0
                    
                    while not data_verified and retry_count < max_retries:
                        try:
                            resp = index.fetch(ids=[vector_id], namespace="")
                            if vector_id in resp.vectors:
                                fetched_meta = resp.vectors[vector_id].metadata
                                if fetched_meta == metadata:
                                    data_verified = True
                                    break
                        except Exception as e:
                            st.warning(f"Attempt {retry_count + 1}: Waiting for data to be available...")
                        
                        time.sleep(1)
                        retry_count += 1
                    
                if not data_verified:
                    st.error("❌ Failed to verify metadata storage. Try Initiate call again.")
                    st.stop()
                
                st.success("✅ Metadata successfully stored and verified!")
                
                command = f'lk dispatch create --new-room --agent-name "teliphonic-rag-agent-testing" --metadata "{vector_id}"'
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
            <strong>StackVoice Telephonic Agent System</strong> • v1.0.0 • 
            Powered by 💜 Sample Set
        </div>
    """, unsafe_allow_html=True)