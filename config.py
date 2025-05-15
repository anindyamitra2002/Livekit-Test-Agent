# Component configurations
CONFIG = {
    "STT": {
        "provider": {
            "type": "string",
            "enum": ["azure", "sarvam", "deepgram"]
        },
        "model": {
            "type": "string",
            "enum": [
                "azure:default",
                "sarvam:saarika:v2",
                "sarvam:saarika:v1",
                "sarvam:saarika:flash",
                "deepgram:nova-2-general",
                "deepgram:nova-3-general"
            ]
        },
        "language": {
            "type": "object",
            "azure": ["hi-IN", "mr-IN", "en-IN", "ta-IN", "bn-IN", "gu-IN", "te-IN", "ml-IN", "kn-IN", "od-IN"],
            "sarvam": ["hi-IN", "mr-IN", "en-IN", "ta-IN", "bn-IN", "gu-IN", "te-IN", "ml-IN", "kn-IN", "od-IN"],
            "deepgram": ["en-IN", "hi-IN"]
        }
    },
    "LLM": {
        "provider": {
            "type": "string",
            "enum": ["openai"]
        },
        "model": {
            "type": "string",
            "enum": [
                "openai:gpt-4o",
                "openai:gpt-4o-mini",
                "openai:gpt-4.1",
                "openai:gpt-4.1-mini",
                "openai:gpt-4.1-nano"
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
            "enum": ["azure", "sarvam", "elevenlabs"]
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
                "elevenlabs:ta-Meera"
            ]
        },
        "language": {
            "type": "object",
            "azure": ["hi-IN", "mr-IN", "en-IN", "ta-IN", "bn-IN", "gu-IN", "te-IN", "ml-IN", "kn-IN", "od-IN", "pa-IN"],
            "sarvam": ["hi-IN", "mr-IN", "en-IN", "ta-IN", "bn-IN", "gu-IN", "te-IN", "ml-IN", "kn-IN", "od-IN", "pa-IN"],
            "elevenlabs": ["en-IN", "hi-IN", "ta-IN"]
        }
    }
}