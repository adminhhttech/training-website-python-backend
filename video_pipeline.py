import uuid

from gemini_client import get_slides
from image_fetcher import fetch_image
from tts_piper import generate_audio
from slide_builder import build_slide
from video_builder import build_video
from config import OUTPUT_VIDEO, FPS


def generate_personal_assistant_video(topic: str, mode: str, output_path: str):
    slide_count = {
        "crisp": 6,
        "detailed": 10,
        "comprehensive": 15
    }.get(mode, 6)

    slides_data = get_slides(topic, slide_count)

    slide_imgs = []
    audio_files = []

    for i, slide in enumerate(slides_data):
        img = fetch_image(slide["image_query"], i)
        slide_img = build_slide(
            img,
            slide["heading"],
            slide["subheading"],
            i
        )
        audio = generate_audio(slide["narration"], i)

        slide_imgs.append(slide_img)
        audio_files.append(audio)

    build_video(slide_imgs, audio_files, output_path, FPS)
    
    
    
def generate_mock_test_video(topic: str, output_path: str):
    
    slides_data = get_slides(topic)

    slide_imgs = []
    audio_files = []

    for i, slide in enumerate(slides_data):
        img = fetch_image(slide["image_query"], i)
        slide_img = build_slide(
            img,
            slide["heading"],
            slide["subheading"],
            i
        )
        audio = generate_audio(slide["narration"], i)

        slide_imgs.append(slide_img)
        audio_files.append(audio)

    build_video(slide_imgs, audio_files, output_path, FPS)
