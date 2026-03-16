import os
from dotenv import load_dotenv
from groq import Groq


GEMINI_API_KEY = "AIzaSyAooNjmq0L_C38WsA-90xtYUnndC74H2Do"
GOOGLE_CSE_API_KEY = "AIzaSyAO61Zs_VEeGuPjO_u4813lBHPnl55Cug8"
GOOGLE_CSE_ID = "46ec81a4219f14e22"


IMAGE_DIR = "assets/images"
AUDIO_DIR = "assets/audio"
SLIDE_DIR = "assets/slides"
OUTPUT_VIDEO = "output/final_video.mp4"

VIDEO_SIZE = (1280, 720)
FPS = 24


load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in environment variables.")

client = Groq(api_key=GROQ_API_KEY)

MODEL_NAME = "llama-3.1-8b-instant"

MAX_TOKENS = 180
TEMPERATURE = 0.7
