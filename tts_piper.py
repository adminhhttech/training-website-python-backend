# from pathlib import Path
# import asyncio
# import edge_tts
# import concurrent.futures

# # -------------------------
# # PATHS
# # -------------------------
# BASE_DIR = Path(__file__).resolve().parent
# AUDIO_DIR = BASE_DIR / "assets" / "audio"
# AUDIO_DIR.mkdir(parents=True, exist_ok=True)

# VOICE = "en-US-AriaNeural"


# # -------------------------
# # ASYNC TTS
# # -------------------------
# async def _tts(text: str, output_path: str):
#     communicate = edge_tts.Communicate(text, VOICE)
#     await communicate.save(output_path)


# # -------------------------
# # PUBLIC FUNCTION
# # -------------------------
# def generate_audio(text: str, index: int) -> str:
#     if not text or not text.strip():
#         raise ValueError("Narration text is empty")

#     mp3_path = AUDIO_DIR / f"slide_{index}.mp3"

#     # Run async TTS safely inside FastAPI
#     with concurrent.futures.ThreadPoolExecutor() as executor:
#         executor.submit(
#             asyncio.run,
#             _tts(text, str(mp3_path))
#         ).result()

#     print(f"✅ Audio generated: {mp3_path}")
#     return str(mp3_path)


import asyncio
import wave
from pathlib import Path
from piper import PiperVoice

# -------------------------
# PATHS
# -------------------------
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "en_US-lessac-medium.onnx"
AUDIO_DIR = BASE_DIR / "assets" / "audio"

AUDIO_DIR.mkdir(parents=True, exist_ok=True)

_piper_voice: PiperVoice | None = None


# -------------------------
# LOAD MODEL ONCE
# -------------------------
def _get_piper_voice() -> PiperVoice:
    global _piper_voice
    if _piper_voice is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"Piper model not found at: {MODEL_PATH}")
        print(f"🔊 Loading Piper model: {MODEL_PATH}")
        _piper_voice = PiperVoice.load(MODEL_PATH)
    return _piper_voice


# -------------------------
# ASYNC AUDIO GENERATION
# -------------------------
async def _generate_voice_async(text: str, index: int) -> str:
    output_path = AUDIO_DIR / f"slide_{index}.wav"

    if not text or text.isspace():
        raise ValueError("Narration text is empty")

    voice = _get_piper_voice()

    def _synthesize():
        with wave.open(str(output_path), "wb") as wav_file:
            voice.synthesize_wav(text, wav_file)

    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, _synthesize)

    print(f"✅ Audio generated: {output_path}")
    return str(output_path)


# -------------------------
# PUBLIC SYNC API
# -------------------------
def generate_audio(text: str, index: int) -> str:
    """
    Synchronous wrapper used by main.py
    """
    return asyncio.run(_generate_voice_async(text, index))
