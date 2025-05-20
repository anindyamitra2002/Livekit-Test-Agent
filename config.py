# Component configurations
CONFIG = {
    "STT": {
        "provider": {
            "type": "string",
            "enum": ["azure", "sarvam", "deepgram", "google", "openai", "iitm", "groq"]
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
                
                "openai:whisper-1",
                
                "iitm:ccc-wav2vec-2.0",
                
                "groq:whisper-large-v3-turbo",
                "groq:distil-whisper-large-v3-en",
                "groq:whisper-large-v3",
                
            ]
        },
        "language": {
            "type": "object",
            "azure": ["hi-IN", "mr-IN", "en-IN", "ta-IN", "bn-IN", "gu-IN", "te-IN", "ml-IN", "kn-IN", "od-IN"],
            "sarvam": ["hi-IN", "mr-IN", "en-IN", "ta-IN", "bn-IN", "gu-IN", "te-IN", "ml-IN", "kn-IN", "od-IN"],
            "deepgram": ["en-IN", "hi-IN"],
            "google": ["hi-IN", "mr-IN", "en-IN", "ta-IN", "bn-IN", "gu-IN", "te-IN", "ml-IN", "kn-IN"],
            "openai": ["hi-IN", "mr-IN", "en-IN", "ta-IN", "kn-IN"],
            "iitm": ["hi-IN", "mr-IN", "en-IN", "ta-IN", "bn-IN", "gu-IN", "te-IN", "ml-IN", "kn-IN", "od-IN"],
            "groq": ["en-IN"]
        }
    },
    "LLM": {
        "provider": {
            "type": "string",
            "enum": ["openai", "deepseek", "google", "groq", "togetherai"]
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
                "google:gemini-2.0-flash-lite",
                "google:gemini-1.5-flash",
                "google:gemini-1.5-flash-8b",
                "google:gemini-1.5-pro",
                
                "groq:gemma2-9b-it",
                "groq:llama-3.3-70b-versatile",
                "groq:llama-3.1-8b-instant",
                "groq:llama3-70b-8192",
                "groq:llama3-8b-8192",
                "groq:deepseek-r1-distill-llama-70b",
                "groq:mistral-saba-24b",
                "groq:qwen-qwq-32b",
                "groq:meta-llama/llama-4-maverick-17b-128e-instruct",
                "groq:meta-llama/llama-4-scout-17b-16e-instruct",
                "groq:meta-llama/Llama-Guard-4-12B",
                
                "togetherai:Qwen/Qwen3-235B-A22B-fp8-tput",
                "togetherai:meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
                "togetherai:meta-llama/Llama-4-Scout-17B-16E-Instruct",
                "togetherai:deepseek-ai/DeepSeek-R1",
                "togetherai:deepseek-ai/DeepSeek-V3",
                "togetherai:deepseek-ai/DeepSeek-R1-Distill-Llama-70B",
                "togetherai:deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B",
                "togetherai:deepseek-ai/DeepSeek-R1-Distill-Qwen-14B",
                "togetherai:perplexity-ai/r1-1776",
                "togetherai:marin-community/marin-8b-instruct",
                "togetherai:mistralai/Mistral-Small-24B-Instruct-2501",
                "togetherai:meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
                "togetherai:meta-llama/Llama-3.3-70B-Instruct-Turbo",
                "togetherai:nvidia/Llama-3.1-Nemotron-70B-Instruct-HF",
                "togetherai:Qwen/Qwen2.5-7B-Instruct-Turbo",
                "togetherai:Qwen/Qwen2.5-72B-Instruct-Turbo",
                "togetherai:Qwen/Qwen2.5-VL-72B-Instruct",
                "togetherai:Qwen/Qwen2.5-Coder-32B-Instruct",
                "togetherai:Qwen/QwQ-32B",
                "togetherai:Qwen/Qwen2-72B-Instruct",
                "togetherai:Qwen/Qwen2-VL-72B-Instruct",
                "togetherai:arcee-ai/virtuoso-medium-v2",
                "togetherai:arcee-ai/coder-large",
                "togetherai:arcee-ai/virtuoso-large",
                "togetherai:arcee-ai/maestro-reasoning",
                "togetherai:arcee-ai/caller",
                "togetherai:arcee-ai/arcee-blitz",
                "togetherai:meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
                "togetherai:meta-llama/Llama-3.2-3B-Instruct-Turbo",
                "togetherai:meta-llama/Meta-Llama-3-8B-Instruct-Lite",
                "togetherai:meta-llama/Llama-3-8b-chat-hf",
                "togetherai:meta-llama/Llama-3-70b-chat-hf",
                "togetherai:google/gemma-2-27b-it",
                "togetherai:google/gemma-2-9b-it*",
                "togetherai:google/gemma-2b-it*",
                "togetherai:Gryphe/MythoMax-L2-13b*",
                "togetherai:mistralai/Mistral-7B-Instruct-v0.1",
                "togetherai:mistralai/Mistral-7B-Instruct-v0.2",
                "togetherai:mistralai/Mistral-7B-Instruct-v0.3",
                "togetherai:mistralai/Mixtral-8x7B-Instruct-v0.1*",
                "togetherai:mistralai/Mixtral-8x22B-Instruct-v0.1*",
                "togetherai:NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO",
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
            "enum": ["azure", "sarvam", "elevenlabs", "cartesia", "groq"]
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
                
                "groq:en-Arista-PlayAI",
                "groq:en-Atlas-PlayAI",
                "groq:en-Basil-PlayAI",
                "groq:en-Briggs-PlayAI",
                "groq:en-Calum-PlayAI",
                "groq:en-Celeste-PlayAI",
                "groq:en-Cheyenne-PlayAI",
                "groq:en-Chip-PlayAI",
                "groq:en-Cillian-PlayAI",
                "groq:en-Deedee-PlayAI",
                "groq:en-Fritz-PlayAI",
                "groq:en-Gail-PlayAI",
                "groq:en-Indigo-PlayAI",
                "groq:en-Mamaw-PlayAI",
                "groq:en-Mason-PlayAI",
                "groq:en-Mikail-PlayAI",
                "groq:en-Mitch-PlayAI",
                "groq:en-Quinn-PlayAI",
                "groq:en-Thunder-PlayAI",
            ]
        },
        "language": {
            "type": "object",
            "azure": ["hi-IN", "mr-IN", "en-IN", "ta-IN", "bn-IN", "gu-IN", "te-IN", "ml-IN", "kn-IN", "od-IN", "pa-IN"],
            "sarvam": ["hi-IN", "mr-IN", "en-IN", "ta-IN", "bn-IN", "gu-IN", "te-IN", "ml-IN", "kn-IN", "od-IN", "pa-IN"],
            "elevenlabs": ["en-IN", "hi-IN", "ta-IN"],
            "cartesia": ["en-IN", "hi-IN"],
            "groq": ["en-IN"]
        }
    }
}

# Cost dictionary
costs_per_min = {
    "STT": {
        "azure:default": 0.00835,             
        "sarvam:saarika:v2": 0.00305,         
        "sarvam:saarika:v1": 0.00305,         
        "sarvam:saarika:flash": 0.00305,      
        "deepgram:nova-2-general": 0.00290,   
        "deepgram:nova-3-general": 0.00385,   
        "google:default": 0.00800,            
        "google:command_and_search": 0.01200, 
        "openai:whisper-1": 0.00300,
        "iitm:ccc-wav2vec-2.0": 0.000,
        "groq:whisper-large-v3-turbo": 0.000333,
        "groq:distil-whisper-large-v3-en": 0.000167,
        "groq:whisper-large-v3": 0.000925,      
    },
    "LLM": {
        "openai:gpt-4o": 0.0295,
        "openai:gpt-4o-mini": 0.00093,
        "openai:gpt-4.1": 0.0124,
        "openai:gpt-4.1-mini": 0.00248,
        "openai:gpt-4.1-nano": 0.00062,
        
        "deepseek:deepseek-v3": 0.0000784,
        "deepseek:deepseek-r1": 0.003407,
        
        "google:gemini-2.5-flash-preview-04-17": 0.00093,
        "google:gemini-2.5-pro-preview-05-06":  0.00925,
        "google:gemini-2.0-flash":              0.00062,
        "google:gemini-2.0-flash-lite":         0.00062,
        "google:gemini-1.5-flash":              0.002065,
        "google:gemini-1.5-flash-8b":           0.0002325,
        "google:gemini-1.5-pro":                0.02065,
        
        "groq:gemma2-9b-it": 0.00106,
        "groq:llama-3.3-70b-versatile": 0.003187,
        "groq:llama-3.1-8b-instant": 0.000274,
        "groq:llama3-70b-8192": 0.003187,
        "groq:llama3-8b-8192": 0.000274,
        "groq:deepseek-r1-distill-llama-70b": 0.004047,
        "groq:mistral-saba-24b": 0.004187,
        "groq:qwen-qwq-32b": 0.001567,
        "groq:meta-llama/llama-4-maverick-17b-128e-instruct": 0.00118,
        "groq:meta-llama/llama-4-scout-17b-16e-instruct": 0.000652,
        "groq:meta-llama/Llama-Guard-4-12B": 0.00106,
        
        "togetherai:Qwen/Qwen3-235B-A22B-fp8-tput":                    0.00118,
        "togetherai:meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8": 0.001605,
        "togetherai:meta-llama/Llama-4-Scout-17B-16E-Instruct":         0.001077,
        "togetherai:deepseek-ai/DeepSeek-R1":                          0.01710,
        "togetherai:deepseek-ai/DeepSeek-V3":                          0.006625,
        "togetherai:deepseek-ai/DeepSeek-R1-Distill-Llama-70B":        0.01060,
        "togetherai:deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B":         0.000954,
        "togetherai:deepseek-ai/DeepSeek-R1-Distill-Qwen-14B":          0.00848,
        "togetherai:perplexity-ai/r1-1776":                            0.01710,
        "togetherai:marin-community/marin-8b-instruct":                0.000954,
        "togetherai:mistralai/Mistral-Small-24B-Instruct-2501":        0.00424,
        "togetherai:meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo":       0.000954,
        "togetherai:meta-llama/Llama-3.3-70B-Instruct-Turbo":           0.004664,
        "togetherai:nvidia/Llama-3.1-Nemotron-70B-Instruct-HF":        0.004664,
        "togetherai:Qwen/Qwen2.5-7B-Instruct-Turbo":                    0.00159,
        "togetherai:Qwen/Qwen2.5-72B-Instruct-Turbo":                  0.00636,
        "togetherai:Qwen/Qwen2.5-VL-72B-Instruct":                     0.004135,
        "togetherai:Qwen/Qwen2.5-Coder-32B-Instruct":                  0.00424,
        "togetherai:Qwen/QwQ-32B":                                     0.00636,
        "togetherai:Qwen/Qwen2-72B-Instruct":                          0.00477,
        "togetherai:Qwen/Qwen2-VL-72B-Instruct":                       0.00636,
        "togetherai:arcee-ai/virtuoso-medium-v2":                      0.00265,
        "togetherai:arcee-ai/coder-large":                             0.00265,
        "togetherai:arcee-ai/virtuoso-large":                          0.00390,
        "togetherai:arcee-ai/maestro-reasoning":                       0.00459,
        "togetherai:arcee-ai/caller":                                  0.00199,
        "togetherai:arcee-ai/arcee-blitz":                             0.002475,
        "togetherai:meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo":     0.01855,
        "togetherai:meta-llama/Llama-3.2-3B-Instruct-Turbo":            0.000318,
        "togetherai:meta-llama/Meta-Llama-3-8B-Instruct-Lite":          0.00053,
        "togetherai:meta-llama/Llama-3-8b-chat-hf":                     0.00053,
        "togetherai:meta-llama/Llama-3-70b-chat-hf":                    0.004664,
        "togetherai:google/gemma-2-27b-it":                             0.00424,
        "togetherai:google/gemma-2-9b-it":                             None,
        "togetherai:google/gemma-2b-it":                                0.00053,
        "togetherai:Gryphe/MythoMax-L2-13b":                            0.00053,
        "togetherai:mistralai/Mistral-7B-Instruct-v0.1":                0.00106,
        "togetherai:mistralai/Mistral-7B-Instruct-v0.2":                0.00106,
        "togetherai:mistralai/Mistral-7B-Instruct-v0.3":                0.00106,
        "togetherai:mistralai/Mixtral-8x7B-Instruct-v0.1":              None,
        "togetherai:mistralai/Mixtral-8x22B-Instruct-v0.1":             None,
        "togetherai:NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO":       0.00318,
    },
    "TTS": {
        "azure": 0.03,        
        "sarvam": 0.036585,   
        "elevenlabs": 0.36,   
        "cartesia": 0.015,
        "groq": 0.0600,   
    }
}