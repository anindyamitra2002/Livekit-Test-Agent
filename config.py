# Component configurations
CONFIG = {
    "STT": {
        "provider": {
            "type": "string",
            "enum": ["azure", "sarvam", "deepgram", "google", "openai"]
        },
        "model": {
            "type": "string",
            "enum": [
                "azure:default",
                
                "sarvam:saarika:v2",
                "sarvam:saarika:v1",
                "sarvam:saarika:flash",
                
                "deepgram:nova-2-general",
                "deepgram:nova-3-general",
                
                "google:command_and_search",
                "google:default",
                
                "openai:whisper-1"
            ]
        },
        "language": {
            "type": "object",
            "azure": ["hi-IN", "mr-IN", "en-IN", "ta-IN", "bn-IN", "gu-IN", "te-IN", "ml-IN", "kn-IN", "od-IN"],
            "sarvam": ["hi-IN", "mr-IN", "en-IN", "ta-IN", "bn-IN", "gu-IN", "te-IN", "ml-IN", "kn-IN", "od-IN"],
            "deepgram": ["en-IN", "hi-IN"],
            "google": ["hi-IN", "mr-IN", "en-IN", "ta-IN", "bn-IN", "gu-IN", "te-IN", "ml-IN", "kn-IN"],
            "openai": ["hi-IN", "mr-IN", "en-IN", "ta-IN", "kn-IN"],
        }
    },
    "LLM": {
        "provider": {
            "type": "string",
            "enum": ["openai", "deepseek", "google"]
        },
        "model": {
            "type": "string",
            "enum": [
                "openai:gpt-4o",
                "openai:gpt-4o-mini",
                "openai:gpt-4.1",
                "openai:gpt-4.1-mini",
                "openai:gpt-4.1-nano",
                
                "deepseek:deepseek-v3",
                "deepseek:deepseek-r1",
                
                "google:gemini-2.5-flash-preview-04-17",
                "google:gemini-2.5-pro-preview-05-06",
                "google:gemini-2.0-flash",
                "google:gemini-2.0-flash-preview-image-generation",
                "google:gemini-2.0-flash-lite",
                "google:gemini-1.5-flash",
                "google:gemini-1.5-flash-8b",
                "google:gemini-1.5-pro",
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
            "enum": ["azure", "sarvam", "elevenlabs", "cartesia"]
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
                
                "azure:pa-IN-OjasNeural",
                "azure:pa-IN-VaaniNeural"

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
                "sarvam:Vian",
                
                "elevenlabs:en-Brittney",
                "elevenlabs:hi-Monika-Sogam",
                "elevenlabs:ta-Meera",
                
                "cartesia:en-Carson",
                "cartesia:en-Ethan",
                "cartesia:en-David",
                "cartesia:en-Sophie",
                "cartesia:en-Savannah",
                "cartesia:en-Brooke",
                "cartesia:en-Corinne",
                "cartesia:hi-Apoorva",
                "cartesia:hi-Ananya",
                "cartesia:hi-Mita",
                "cartesia:hi-Amit",
                "cartesia:hi-Ishan",
                "cartesia:hi-Mihir",
            ]
        },
        "language": {
            "type": "object",
            "azure": ["hi-IN", "mr-IN", "en-IN", "ta-IN", "bn-IN", "gu-IN", "te-IN", "ml-IN", "kn-IN", "od-IN", "pa-IN"],
            "sarvam": ["hi-IN", "mr-IN", "en-IN", "ta-IN", "bn-IN", "gu-IN", "te-IN", "ml-IN", "kn-IN", "od-IN", "pa-IN"],
            "elevenlabs": ["en-IN", "hi-IN", "ta-IN"],
            "cartesia": ["en-IN", "hi-IN"]
        }
    }
}