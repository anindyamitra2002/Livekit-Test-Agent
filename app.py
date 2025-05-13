import streamlit as st
import subprocess
import os
import re
from pinecone import Pinecone, ServerlessSpec
import tempfile
from dotenv import load_dotenv
import random
import time
# Load environment variables
load_dotenv()

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

# Language mapping dictionary
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

# Streamlit app title
st.title("Vedantu Counselling Agent")

# Initialize Pinecone Assistant
assistant = pc.assistant.Assistant(assistant_name="vedantu-rag")

# File uploader widget (provides the upload button)
uploaded_file = st.file_uploader("Upload a file", type=["txt", "pdf", "docx", "md"])
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
                response = assistant.upload_file(file_path=file_path)
                st.success(f"Uploaded file '{original_filename}' with ID '{response['id']}'")
            except Exception as e:
                st.error(f"Error uploading file: {str(e)}")
    # Temporary directory is automatically cleaned up when the 'with' block exits

# Fetch and display the list of files in the assistant
try:
    files_response = assistant.list_files()
    files = files_response
    
    if files:
        st.subheader("Uploaded Files")
        for file in files:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"{file.name} - Status: {file.status}")
            with col2:
                if st.button("Delete", key=file.id):
                    try:
                        assistant.delete_file(file.id)
                        st.success(f"Deleted file '{file.name}'")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error deleting file: {str(e)}")
    else:
        st.info("No files uploaded to the assistant yet.")
except Exception as e:
    st.error(f"Error listing files: {str(e)}")
# Phone number input
phone_number = st.text_input("Enter Phone Number", placeholder="+91XXXXXXXXXX")

# Function to validate phone number
def validate_phone_number(phone):
    pattern = r'^\+91\d{10}$'
    return bool(re.match(pattern, phone))

# Language selection dropdown
language_options = list(LANGUAGE_MAPPING.keys())
language_display = [f"{LANGUAGE_MAPPING[lang]} ({lang})" for lang in language_options]
selected_language_display = st.selectbox("Select Language", language_display)
selected_language = language_options[language_display.index(selected_language_display)]

# LLM Model selection
llm_options = ['gpt-4o', 'gpt-4o-mini', 'gpt-4.1', 'gpt-4.1-mini']
selected_llm = st.selectbox("Select LLM Model", llm_options)

# STT Model selection
stt_options = ['sarvam', 'azure']
selected_stt = st.selectbox("Select STT Model", stt_options)

# TTS Model selection
tts_options = ['sarvam', 'azure', 'elevenlabs']
selected_tts = st.selectbox("Select TTS Model", tts_options)
if selected_tts == 'elevenlabs' and selected_language not in ['en-IN', 'hi-IN', 'ta-IN']:
    st.error("ElevenLabs is only available for English, Hindi, and Tamil languages.")

# Prompt Instruction
prompt_instruction = st.text_area("Enter Prompt Instruction")

# First Message
first_message = st.text_input("Enter First Message")

# Call button
if st.button("Call"):
    if phone_number and selected_language and selected_llm and selected_stt and selected_tts and prompt_instruction and first_message:
        if not validate_phone_number(phone_number):
            st.error("Invalid phone number format. Please enter a valid Indian phone number starting with +91 followed by 10 digits.")
        else:
            try:
                # Construct metadata dictionary
                metadata = {
                    "phone_number": phone_number,
                    "language": selected_language,
                    "llm_model": selected_llm,
                    "stt_model": selected_stt,
                    "tts_model": selected_tts,
                    "prompt_instruction": prompt_instruction,
                    "first_message": first_message
                }

                # Generate a unique vector ID (e.g., based on phone number or timestamp)
                vector_id = f"call-{phone_number}-{random.randint(100000, 999999)}"

                # Upsert metadata to Pinecone
                with st.spinner("Sending call metadata..."):
                    index.upsert(
                        vectors=[
                            {"id": vector_id, "values": DUMMY_VECTOR, "metadata": metadata}
                        ],
                        namespace=""
                    )
                    time.sleep(2)

                command = f'lk dispatch create --new-room --agent-name "teliphonic-rag-agent-test" --metadata "{vector_id}"'

                try:
                    # Execute the command
                    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    stdout, stderr = process.communicate()
                    
                    if process.returncode == 0:
                        st.success("Call initiated successfully!")
                        st.text("Command output:")
                        st.text(stdout.decode())
                    else:
                        st.error("Error initiating call:")
                        st.text(stderr.decode())
                except Exception as e:
                        st.error(f"An error occurred: {str(e)}")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
    else:
        st.warning("Please fill in all the fields.")