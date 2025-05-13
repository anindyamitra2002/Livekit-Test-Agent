import streamlit as st
import subprocess
import os
import re
from pinecone import Pinecone, ServerlessSpec
import tempfile
from dotenv import load_dotenv
import random
import time
import json
import pandas as pd
import hashlib
from datetime import datetime

# Load environment variables
load_dotenv()

# Set page config first thing
st.set_page_config(
    page_title="Livekit Telephonic Agent",
    page_icon="📞",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Remove top padding in the main area (applied once right after page config)
st.markdown("""
    <style>
        .block-container {
            padding-top: 4rem;
            padding-bottom: 0rem;
        }
        div[data-testid="stVerticalBlock"] {
            gap: 0.5rem;
        }
        div.stButton > button {
            width: 100%;
        }
        div[data-testid="stDataFrameResizable"] {
            overflow: auto;
        }
        
        /* Configuration section styling */
        .config-section {
            margin-bottom: 0.5rem;
        }
        .config-title {
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid #e0e0e0;
        }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------------
# User Authentication System
# ---------------------------------------------------------------------------------

# Initialize session state for authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user' not in st.session_state:
    st.session_state.user = None
if 'users_db' not in st.session_state:
    # Initialize with a default admin user (in a real app, this would be stored in a database)
    st.session_state.users_db = {
        "admin@gamil.com": {
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
    """Authenticate user with username and password"""
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
    """Log out the current user"""
    st.session_state.authenticated = False
    st.session_state.user = None
    st.rerun()

# Show login page if not authenticated
if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.title("Livekit Telephonic Agent")
        st.markdown("Please log in to access the application")
        
        # Login form
        with st.form("login_form"):
            username = st.text_input("Email", placeholder="Enter your email")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            login_button = st.form_submit_button("Login")
            
            if login_button:
                if authenticate(username, password):
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid email or password")
        
        # # Demo credentials
        # with st.expander("Demo Credentials"):
        #     st.markdown("""
        #     **Admin User**
        #     - Email: admin@vedantu.com
        #     - Password: admin123
            
        #     **Regular User**
        #     - Email: user@vedantu.com
        #     - Password: user123
        #     """)

# If authenticated, show the main application
else:
    # Initialize Pinecone with API key
    api_key = os.getenv("PINECONE_API_KEY")
    pc = Pinecone(api_key=api_key)

    # Define Pinecone index name and parameters
    INDEX_NAME = "parameters"
    VECTOR_DIMENSION = 384  # Match the dimension from reference code
    DUMMY_VECTOR = [0.5] * VECTOR_DIMENSION  # Dummy vector for metadata storage

    # Ensure Pinecone index exists
    if not pc.has_index(INDEX_NAME):
        pc.create_index(
            name=INDEX_NAME,
            dimension=VECTOR_DIMENSION,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
    index = pc.Index(INDEX_NAME)

    # Initialize Pinecone Assistant
    assistant = pc.assistant.Assistant(assistant_name="vedantu-rag")

    # Component configurations
    CONFIG = {
        "STT": {
            "provider": {
                "type": "string",
                "enum": ["azure", "sarvam"]
            },
            "model": {
                "type": "string",
                "enum": [
                    "azure:default",
                    "sarvam:saarika:v2",
                    "sarvam:saaras:v2",
                ]
            },
            "language": {
                "type": "string",
                "enum": ["hi-IN", "mr-IN", "en-IN", "ta-IN", "bn-IN", "gu-IN", "te-IN", "ml-IN", "kn-IN", "od-IN"]
            }
        },
        "LLM": {
            "provider": {
                "type": "string",
                "enum": ["openai",]
            },
            "model": {
                "type": "string",
                "enum": [
                    "openai:gpt-4o",
                    "openai:gpt-4o-mini",
                    "openai:gpt-4.1",
                    "openai:gpt-4.1-mini",
                    "openai:gpt-4.1-nano",
                ]
            },
            "system_prompt": {
                "type": "string",
                "description": "The initial system or assistant prompt to steer the model"
            },
            "temperature": {
                "type": "number",
                "minimum": 0.0,
                "maximum": 1.0,
                "description": "Controls randomness: 0.0 = deterministic, 1.0 = maximum randomness"
            }
        },
        "TTS": {
            "provider": {
                "type": "string",
                "enum": ["azure", "sarvam"]
            },
            "voice": {
                "type": "string",
                "enum": [
                    "azure:hi-IN-AaravNeural",
                    "azure:hi-IN-AnanyaNeural",
                    "azure:hi-IN-AartiNeural",
                    "azure:hi-IN-ArjunNeural",
                    "azure:hi-IN-KavyaNeural",
                    "azure:hi-IN-KunalNeural",
                    "azure:hi-IN-RehaanNeural",
                    "azure:hi-IN-SwaraNeural",
                    "azure:hi-IN-MadhurNeural",

                    "azure:mr-IN-AarohiNeural",
                    "azure:mr-IN-ManoharNeural",

                    "azure:en-IN-AaravNeural",
                    "azure:en-IN-AashiNeural",
                    "azure:en-IN-AartiNeural",
                    "azure:en-IN-ArjunNeural",
                    "azure:en-IN-AnanyaNeural",
                    "azure:en-IN-KavyaNeural",
                    "azure:en-IN-KunalNeural",
                    "azure:en-IN-NeerjaNeural",
                    "azure:en-IN-PrabhatNeural",
                    "azure:en-IN-RehaanNeural",

                    "azure:ta-IN-PallaviNeural",
                    "azure:ta-IN-ValluvarNeural",

                    "azure:bn-IN-TanishaaNeural",
                    "azure:bn-IN-BashkarNeural",

                    "azure:gu-IN-DhwaniNeural",
                    "azure:gu-IN-NiranjanNeural",

                    "azure:te-IN-ShrutiNeural",
                    "azure:te-IN-MohanNeural",

                    "azure:ml-IN-SobhanaNeural",
                    "azure:ml-IN-MidhunNeural",

                    "azure:kn-IN-SapnaNeural",
                    "azure:kn-IN-GaganNeural",

                    "azure:or-IN-SubhasiniNeural",
                    "azure:or-IN-SukantNeural",

                    "sarvam:Diya",
                    "sarvam:Maya",
                    "sarvam:Meera",
                    "sarvam:Pavithra",
                    "sarvam:Maitreyi",
                    "sarvam:Misha",
                    "sarvam:Amol",
                    "sarvam:Arjun",
                    "sarvam:Amartya",
                    "sarvam:Arvind",
                    "sarvam:Neel",
                    "sarvam:Vian"
                    ]

            },
            "language": {
                "type": "string",
                "enum": ["hi-IN", "mr-IN", "en-US", "ta-IN", "bn-IN", "gu-IN"]
            },
        }
    }

    # Create provider-dependent model mappings
    PROVIDER_MODEL_MAPPING = {
        "STT": {
            "azure": [model for model in CONFIG["STT"]["model"]["enum"] if model.startswith("azure:")],
            "sarvam": [model for model in CONFIG["STT"]["model"]["enum"] if model.startswith("sarvam:")]
        },
        "LLM": {
            "openai": [model for model in CONFIG["LLM"]["model"]["enum"] if model.startswith("openai:")],
            "anthropic": [model for model in CONFIG["LLM"]["model"]["enum"] if model.startswith("anthropic:")],
            "cohere": [model for model in CONFIG["LLM"]["model"]["enum"] if model.startswith("cohere:")]
        },
        "TTS": {
            "azure": [voice for voice in CONFIG["TTS"]["voice"]["enum"] if voice.startswith("azure:")],
            "sarvam": [voice for voice in CONFIG["TTS"]["voice"]["enum"] if voice.startswith("sarvam:")]
        }
    }

    # Language mapping dictionary for display
    LANGUAGE_MAPPING = {
        'bn-IN': 'Bengali',
        'en-IN': 'English',
        'gu-IN': 'Gujarati',
        'hi-IN': 'Hindi',
        'kn-IN': 'Kannada',
        'ml-IN': 'Malayalam',
        'mr-IN': 'Marathi',
        'od-IN': 'Odia',
        'pa-IN': 'Punjabi',
        'ta-IN': 'Tamil',
        'te-IN': 'Telugu'
    }
    
    # Function to validate phone number
    def validate_phone_number(phone):
        pattern = r'^\+91\d{10}$'
        return bool(re.match(pattern, phone))

    # Function to beautify model/voice names for display
    def beautify_name(name):
        if not name or ":" not in name:
            return name
        provider, model = name.split(":", 1)
        return f"{model} ({provider.capitalize()})"

    # Top navigation bar with user info and logout
    nav_col1, nav_col2 = st.columns([6, 1])
    with nav_col1:
        st.title("📞 Livekit Telephonic Agent")
    with nav_col2:
        st.markdown(f"""
        <div style="text-align: center; margin-bottom: 3px;">
            <small>{st.session_state.user['name']} ({st.session_state.user['role']})</small>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Logout", type="primary"):
            logout()

    # Create tabs for different sections
    tabs = st.tabs(["Document Upload", "Configuration", "Call Initiation"])

    # Document Upload Tab
    with tabs[0]:
        st.header("Document Upload")
        st.markdown("Upload documents to be used by the counselling agent.")
        
        # File uploader widget
        uploaded_file = st.file_uploader("Upload a file", type=["txt", "pdf", "docx", "md"])
        
        col1, col2 = st.columns([1, 5])
        with col1:
            upload_button = st.button("Upload File")
        
        if upload_button:
            if uploaded_file is not None:
                # Use a temporary directory to save the file with its original name
                with tempfile.TemporaryDirectory() as tmpdirname:
                    original_filename = uploaded_file.name
                    file_path = os.path.join(tmpdirname, original_filename)
                    # Write the uploaded file to the temporary directory
                    with open(file_path, 'wb') as f:
                        f.write(uploaded_file.getvalue())
                    try:
                        # Upload the file to Pinecone using the path with the original filename
                        with st.spinner(f"Uploading {original_filename}..."):
                            response = assistant.upload_file(file_path=file_path)
                            st.success(f"Uploaded file '{original_filename}' with ID '{response['id']}'")
                    except Exception as e:
                        st.error(f"Error uploading file: {str(e)}")
            else:
                st.warning("Please select a file to upload.")
        
        # Display uploaded files
        st.subheader("Uploaded Files")
        try:
            with st.spinner("Loading files..."):
                files_response = assistant.list_files()
                files = files_response
                
                if files:
                    for file in files:
                        col1, col2, col3 = st.columns([3, 1, 1])
                        with col1:
                            status_color = "green" if file.status == "complete" else "orange"
                            st.markdown(f"**{file.name}** - Status: <span style='color:{status_color}'>{file.status}</span>", unsafe_allow_html=True)
                        with col3:
                            if st.button("Delete", key=f"delete_{file.id}"):
                                try:
                                    with st.spinner(f"Deleting {file.name}..."):
                                        assistant.delete_file(file.id)
                                        st.success(f"Deleted file '{file.name}'")
                                        st.rerun()
                                except Exception as e:
                                    st.error(f"Error deleting file: {str(e)}")
                else:
                    st.info("No files uploaded to the assistant yet.")
        except Exception as e:
            st.error(f"Error listing files: {str(e)}")

    # Configuration Tab - REORGANIZED INTO ROWS
    with tabs[1]:
        st.header("Assistant Configuration")
        
        # Initialize session state for selected providers if not already done
        if 'stt_provider' not in st.session_state:
            st.session_state.stt_provider = CONFIG["STT"]["provider"]["enum"][0]
        if 'llm_provider' not in st.session_state:
            st.session_state.llm_provider = CONFIG["LLM"]["provider"]["enum"][0]
        if 'tts_provider' not in st.session_state:
            st.session_state.tts_provider = CONFIG["TTS"]["provider"]["enum"][0]
        
        # STT Configuration Section
        st.markdown('<div class="config-section">', unsafe_allow_html=True)
        st.markdown('<h3 class="config-title">Speech-to-Text (STT) Configuration</h3>', unsafe_allow_html=True)
        st.markdown("Configure speech recognition settings")
        
        # STT Provider selection
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            def update_stt_provider():
                st.session_state.stt_provider = st.session_state.stt_provider_select
                
            stt_provider = st.selectbox(
                "Provider",
                options=CONFIG["STT"]["provider"]["enum"],
                format_func=lambda x: x.capitalize(),
                key="stt_provider_select",
                on_change=update_stt_provider
            )
            
        with col2:
            # STT Model selection based on provider
            stt_model_options = PROVIDER_MODEL_MAPPING["STT"][st.session_state.stt_provider]
            stt_model = st.selectbox(
                "Model",
                options=stt_model_options,
                format_func=beautify_name,
                key="stt_model_select"
            )
            
        with col3:
            # STT Language selection
            stt_language = st.selectbox(
                "Language",
                options=CONFIG["STT"]["language"]["enum"],
                format_func=lambda x: LANGUAGE_MAPPING.get(x, x),
                key="stt_language_select"
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # LLM Configuration Section
        st.markdown('<div class="config-section">', unsafe_allow_html=True)
        st.markdown('<h3 class="config-title">Language Model (LLM) Configuration</h3>', unsafe_allow_html=True)
        st.markdown("Configure AI language model settings")
        
        # Top row for LLM Provider and Model
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            # LLM Provider selection
            def update_llm_provider():
                st.session_state.llm_provider = st.session_state.llm_provider_select
                
            llm_provider = st.selectbox(
                "Provider",
                options=CONFIG["LLM"]["provider"]["enum"],
                format_func=lambda x: x.capitalize(),
                key="llm_provider_select",
                on_change=update_llm_provider
            )
        
        with col2:
            # LLM Model selection based on provider
            llm_model_options = PROVIDER_MODEL_MAPPING["LLM"][st.session_state.llm_provider]
            llm_model = st.selectbox(
                "Model",
                options=llm_model_options,
                format_func=beautify_name,
                key="llm_model_select"
            )
        
        with col3:
            # LLM Temperature
            llm_temperature = st.slider(
                "Temperature",
                min_value=CONFIG["LLM"]["temperature"]["minimum"],
                max_value=CONFIG["LLM"]["temperature"]["maximum"],
                value=0.7,
                step=0.1,
                help=CONFIG["LLM"]["temperature"]["description"],
                key="llm_temperature"
            )
        
        # Second row just for the system prompt (LARGER TEXT AREA)
        # System Prompt - LARGER
        st.markdown("<p style='margin-top: 20px; margin-bottom: 5px; font-weight: 500;'>System Prompt</p>", unsafe_allow_html=True)
        llm_system_prompt = st.text_area(
            "",
            placeholder="Enter instructions for the AI assistant...",
            height=200,  # Increased height
            help=CONFIG["LLM"]["system_prompt"]["description"],
            key="llm_system_prompt"
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # TTS Configuration Section
        st.markdown('<div class="config-section">', unsafe_allow_html=True)
        st.markdown('<h3 class="config-title">Text-to-Speech (TTS) Configuration</h3>', unsafe_allow_html=True)
        st.markdown("Configure voice synthesis settings")
        
        # First row for TTS provider, voice and language
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            # TTS Provider selection
            def update_tts_provider():
                st.session_state.tts_provider = st.session_state.tts_provider_select
                
            tts_provider = st.selectbox(
                "Provider",
                options=CONFIG["TTS"]["provider"]["enum"],
                format_func=lambda x: x.capitalize(),
                key="tts_provider_select",
                on_change=update_tts_provider
            )
        
        with col2:
            # TTS Voice selection based on provider
            tts_voice_options = PROVIDER_MODEL_MAPPING["TTS"][st.session_state.tts_provider]
            tts_voice = st.selectbox(
                "Voice",
                options=tts_voice_options,
                format_func=beautify_name,
                key="tts_voice_select"
            )
        
        with col3:
            # TTS Language
            tts_language = st.selectbox(
                "Language",
                options=CONFIG["TTS"]["language"]["enum"],
                format_func=lambda x: LANGUAGE_MAPPING.get(x, x),
                key="tts_language_select"
            )
        
        st.markdown('</div>', unsafe_allow_html=True)

    # Call Initiation Tab
    with tabs[2]:
        st.header("Call Initiation")
        st.markdown("Enter the details to initiate a counselling call")

        # Call details form
        with st.form("call_form"):
            # Phone number input
            phone_number = st.text_input(
                "Phone Number", 
                placeholder="+91XXXXXXXXXX",
                help="Enter a valid Indian phone number starting with +91 followed by 10 digits"
            )
            
            # First message
            first_message = st.text_area(
                "First Message", 
                placeholder="Enter the first message that will be spoken to the user when they answer the call",
                height=100
            )
            
            # Submit button
            submit_button = st.form_submit_button("Initiate Call")
        
        if submit_button:
            if not phone_number or not first_message:
                st.error("Please fill all required fields")
            elif not validate_phone_number(phone_number):
                st.error("Invalid phone number format. Please enter a valid Indian phone number starting with +91 followed by 10 digits.")
            else:
                try:
                    # Construct metadata dictionary
                    metadata = {
                    'phone_number': phone_number,
                    'first_message': first_message,
                    'STT_provider': st.session_state.stt_provider,
                    'STT_model': stt_model.split("sarvam:")[-1],
                    'STT_language': stt_language,
                    'LLM_provider': st.session_state.llm_provider,
                    'LLM_model': llm_model.split(":")[-1],
                    'LLM_system_prompt': llm_system_prompt,
                    'LLM_temperature': llm_temperature,
                    'TTS_provider': st.session_state.tts_provider,
                    'TTS_voice': tts_voice.split(":")[-1],
                    'TTS_language': tts_language,
                    }


                    # Generate a unique vector ID
                    vector_id = f"call-{phone_number}-{int(time.time())}-{random.randint(100000, 999999)}"

                    # Display confirmation with details
                    st.success("Call configured successfully!")
                    
                    with st.expander("Review Configuration"):
                        st.json(metadata)
                    
                    # Upsert metadata to Pinecone
                    with st.spinner("Sending call metadata..."):
                        index.upsert(
                            vectors=[
                                {"id": vector_id, "values": DUMMY_VECTOR, "metadata": metadata}
                            ],
                            namespace=""
                        )
                        time.sleep(1)

                    command = f'lk dispatch create --new-room --agent-name "teliphonic-rag-agent-dev" --metadata "{vector_id}"'

                    try:
                        # Execute the command
                        with st.spinner("Initiating call..."):
                            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                            stdout, stderr = process.communicate()
                            
                            if process.returncode == 0:
                                st.success("Call initiated successfully!")
                                st.text("Command output:")
                                st.code(stdout.decode())
                            else:
                                st.error("Error initiating call:")
                                st.code(stderr.decode())
                    except Exception as e:
                        st.error(f"An error occurred while executing command: {str(e)}")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

    # Add footer
    st.markdown("---")
    st.markdown(f"<div style='text-align: center; color: gray;'>Livekit Telephonic Agent System • v1.0.0 • Logged in as {st.session_state.user['name']}</div>", unsafe_allow_html=True)