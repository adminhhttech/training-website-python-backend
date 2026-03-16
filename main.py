from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import uuid
from config import client, MODEL_NAME, MAX_TOKENS, TEMPERATURE
from video_pipeline import generate_mock_test_video, generate_personal_assistant_video
from personalities import PERSONALITY_MODES
from memory import get_session_memory, add_message
from service import CounsellorService
service = CounsellorService()


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          
    allow_credentials=False,      
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "healthy"}

VIDEO_DIR = "videos"
os.makedirs(VIDEO_DIR, exist_ok=True)


class MockVideoRequest(BaseModel):
    topic: str


class PersonalVideoRequest(BaseModel):
    topic: str
    mode: str
    

## AI Mentor
class ChatRequest(BaseModel):
    session_id: str
    message: str
    mode: str
    
    



@app.post("/mock-test-video")
def mock_test_video(req: MockVideoRequest):
    output_video_path = os.path.join(VIDEO_DIR, f"video_{uuid.uuid4().hex}.mp4")
    generate_mock_test_video(req.topic, output_video_path)
    return {"status": "success", "video_url": f"/video/{os.path.basename(output_video_path)}"}
    
    
@app.post("/personal-assistant")
def personal_assistant(req: PersonalVideoRequest):   
    output_video = os.path.join(VIDEO_DIR, f"video_{uuid.uuid4().hex}.mp4")
    generate_personal_assistant_video(topic=req.topic, mode=req.mode, output_path=output_video)
    return {"status": "success", "video_url": f"/video/{os.path.basename(output_video)}"}

@app.post("/chat-ai-mentor")
def chat_ai_mentor(request: ChatRequest):
    session_id = request.session_id
    user_message = request.message.strip()
    mode = request.mode
    print("AI Mentor chat request received!")
    if not user_message:
        return {"response": "Please enter a valid message."}

    if mode not in PERSONALITY_MODES:
        return {"response": "Invalid personality mode selected."}

    
    add_message(session_id, "user", user_message)

    system_prompt = {
        "role": "system",
        "content": PERSONALITY_MODES[mode]
    }

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[system_prompt] + get_session_memory(session_id),
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE
        )

        ai_reply = response.choices[0].message.content.strip()

        
        add_message(session_id, "assistant", ai_reply)

        return {"response": ai_reply}

    except Exception:
        return {"response": "Server is busy. Try again shortly."}

@app.get("/video/{filename}")
def get_video(filename: str):
    video_path = os.path.join(VIDEO_DIR, filename)
    return FileResponse(video_path, media_type="video/mp4")


## AI Councellor##    

class AnswerRequest(BaseModel):
    session_id: str
    answer: str
class PersonalInfoRequest(BaseModel):
    session_id: str
    name: str | None = None
    location: str | None = None
    education: str | None = None
class DomainRequest(BaseModel):
    session_id: str | None = None
    domain: str | None = None
class FeedbackRequest(BaseModel):
    session_id: str | None = None
    feedback: str
class ChatRequest(BaseModel):
    session_id: str
    message: str
    
    
@app.post("/start")
def start_conversation():
    return {"session_id": service.start()}
@app.post("/personal-info")
def submit_personal_info(request: PersonalInfoRequest):
    return service.submit_personal_info(
        session_id=request.session_id,
        name=request.name,
        location=request.location,
        education=request.education,
    )
@app.get("/domains")
def list_domains():
    return {"domains": service.get_domains()}
@app.post("/answer")
def submit_answer(request: AnswerRequest):
    return service.answer(request.session_id, request.answer)
@app.post("/detailed-roadmap")
def detailed_roadmap(request: DomainRequest):
    return service.detailed_roadmap(session_id=request.session_id, domain=request.domain)
@app.post("/download-roadmap")
def download_roadmap_pdf(request: DomainRequest):
    pdf_path = service.generate_roadmap_pdf(session_id=request.session_id, domain=request.domain)
    domain = (request.domain or "frontend").replace(" ", "_")
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"{domain}_roadmap.pdf",
    )
@app.post("/feedback")
def submit_feedback(request: FeedbackRequest):
    return service.submit_feedback(session_id=request.session_id, feedback=request.feedback)
@app.post("/chat")
def chat(request: ChatRequest):
    return service.chat(session_id=request.session_id, message=request.message)
