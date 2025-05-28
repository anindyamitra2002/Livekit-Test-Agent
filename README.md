# StackVoice Telephonic Agent

A powerful AI-powered telephonic agent system that enables natural voice conversations with customizable AI models, supporting multiple languages and providers.

## 🌟 Features

- **Multi-Provider Support**: Integrates with various providers for Speech-to-Text (STT), Text-to-Speech (TTS), and Large Language Models (LLM)
- **Multi-Language Support**: Supports multiple Indian languages including Hindi, English, Tamil, Bengali, Gujarati, Kannada, Malayalam, Marathi, Odia, and Punjabi
- **Knowledge Base Integration**: Upload and manage documents for RAG (Retrieval-Augmented Generation) capabilities
- **Cost Tracking**: Real-time cost monitoring for all AI services
- **Customizable Configuration**: Fine-tune agent behavior with various settings
- **User Authentication**: Secure login system with role-based access
- **Modern UI**: Clean and intuitive Streamlit-based interface

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- LiveKit CLI installed
- Pinecone account and API key
- Environment variables set up (see Configuration section)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/StackVoice-Telephonic-Agent.git
cd StackVoice-Telephonic-Agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables in a `.env` file:
```env
PINECONE_API_KEY=your_pinecone_api_key
```

4. Run the application:
```bash
streamlit run app.py
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory with the following variables:
- `PINECONE_API_KEY`: Your Pinecone API key for vector storage

### Model Providers

The system supports multiple providers for each component:

#### Speech-to-Text (STT)
- Azure
- Sarvam
- Deepgram
- OpenAI
- IITM
- Groq

#### Text-to-Speech (TTS)
- Azure
- Sarvam
- ElevenLabs
- Cartesia
- Groq

#### Large Language Models (LLM)
- OpenAI
- TogetherAI

## 💡 Usage

1. **Login**: Access the system using provided credentials
   - Admin: admin@gmail.com / admin123
   - User: user@gmail.com / user123

2. **Knowledge Base Management**:
   - Upload documents through the sidebar
   - Manage uploaded files
   - Enable/disable RAG capabilities

3. **Call Configuration**:
   - Select language and provider for STT
   - Choose LLM model and settings
   - Configure TTS voice and provider
   - Set additional parameters like background sound and interruption handling

4. **Initiating Calls**:
   - Enter recipient's phone number (format: +91XXXXXXXXXX)
   - Configure first message
   - Review settings and costs
   - Initiate call

## ⚙️ Advanced Settings

### Agent Configuration
- **Knowledge Base**: Enable/disable document-based responses
- **Auto End Call**: Automatically end calls after silence
- **Allow Interruptions**: Enable/disable user interruption during agent speech
- **Background Sound**: Add office noise during calls
- **Minimum Silence Duration**: Configure silence detection threshold

### Cost Management
The system provides real-time cost tracking for:
- STT (Speech-to-Text) services
- LLM (Language Model) usage
- TTS (Text-to-Speech) services

## 🔒 Security

- Secure user authentication system
- Role-based access control
- Environment variable protection
- Secure API key management

## 📊 Cost Structure

The system uses a per-minute cost structure for different services:

### STT Costs
- Azure: $0.00835/min
- Sarvam: $0.00305/min
- Deepgram: $0.00290-$0.00385/min
- OpenAI: $0.00300/min
- Groq: $0.000167-$0.000925/min

### TTS Costs
- Azure: $0.03/min
- Sarvam: $0.036585/min
- ElevenLabs: $0.36/min
- Cartesia: $0.015/min
- Groq: $0.06/min

### LLM Costs
- Various models available with costs ranging from $0.000318/min to $0.0295/min

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with Streamlit
- Powered by LiveKit
- Vector storage by Pinecone
- Various AI service providers

## 📞 Support

For support, please open an issue in the GitHub repository or contact the development team.

---

<div align="center">
Made with 💜 by Sample Set
</div>

Remove-Item Env:\REDIS_PORT