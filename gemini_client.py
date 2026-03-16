from google import genai
from config import GEMINI_API_KEY
import json

client = genai.Client(api_key=GEMINI_API_KEY)


# -------- PROMPT 1 : FIXED 5 SLIDES --------
FIXED_PROMPT_TEMPLATE = """
You are an educational content creator for computer science students.

Generate EXACTLY 5 slides for the topic: "{topic}"

Return ONLY valid JSON in this format:
[
{{
    "heading": "",
    "subheading": "",
    "narration": "",
    "image_query": ""
}}
]

STRICT RULES:
- narration must be 2–3 short, clear sentences
- No markdown
- No explanations
- Valid JSON ONLY

IMAGE RULES:
1. For definition/working/structure/algorithm slides
→ image_query MUST include the word "diagram"

2. For application/real-world slides
→ image_query MUST NOT include the word "diagram"
→ Must describe real objects or environments

3. Do NOT use:
banner, course, tutorial, lecture, interview, illustration, cartoon

4. Generate slides in logical learning order.
"""


# -------- PROMPT 2 : DYNAMIC SLIDE COUNT --------
DYNAMIC_PROMPT_TEMPLATE = """
You are an educational content creator for computer science students.

Generate EXACTLY {slide_count} slides for the topic: "{topic}"

Return ONLY valid JSON in this format:
[
{{
    "heading": "",
    "subheading": "",
    "narration": "",
    "image_query": ""
}}
]

STRICT RULES:
- narration must be 2–3 short, clear sentences
- No markdown
- No explanations
- Valid JSON ONLY

IMAGE RULES:
1. For definition/working/structure/algorithm slides
→ image_query MUST include the word "diagram"

2. For application/real-world slides
→ image_query MUST NOT include the word "diagram"
→ Must describe real objects or environments

3. Do NOT use:
banner, course, tutorial, lecture, interview, illustration, cartoon

4. Generate slides in logical learning order.
"""


# -------- FUNCTION --------
def get_slides(topic: str, slide_count: int = None):

    if slide_count is None:
        # Use fixed prompt
        prompt = FIXED_PROMPT_TEMPLATE.format(topic=topic)
    else:
        # Use dynamic prompt
        prompt = DYNAMIC_PROMPT_TEMPLATE.format(
            topic=topic,
            slide_count=slide_count
        )

    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt
    )

    text = response.text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        raise RuntimeError(
            "Gemini did not return valid JSON.\n\nReturned text:\n" + text
        )