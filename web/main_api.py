import os
import sys
import shutil
import tempfile

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from groq import Groq
from src.engine import query_murshid

load_dotenv()

app = FastAPI(title="Murshid AI Enterprise API")
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class ChatRequest(BaseModel):
    message: str
    faculty: str = "كلية الحاسبات والذكاء الاصطناعي"

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_path = os.path.join(BASE_DIR, "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        return f.read()

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    user_query = req.message.strip()
    faculty = req.faculty.strip()
    
    if not user_query:
        return {"answer": "يرجى كتابة استفسار واضح.", "sources": []}
    
    try:
        # إرسال السؤال الصافي مع اسم الكلية للفلترة
        result = query_murshid(user_query=user_query, faculty=faculty)
        return result
    except Exception as e:
        return {"answer": f"حدث خطأ أثناء معالجة السؤال: {str(e)}", "sources": []}

@app.post("/api/transcribe")
async def transcribe_endpoint(audio: UploadFile = File(...), faculty: str = Form("كلية الحاسبات والذكاء الاصطناعي")):
    temp_dir = tempfile.mkdtemp()
    temp_audio_path = os.path.join(temp_dir, audio.filename or "recording.webm")
    
    try:
        with open(temp_audio_path, "wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)
            
        with open(temp_audio_path, "rb") as audio_file:
            transcript = groq_client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=(os.path.basename(temp_audio_path), audio_file.read()),
                language="ar",
                prompt=f"استفسار يخص {faculty}، جامعة الريادة للعلوم والتكنولوجيا، ساعات معتمدة، سنة الامتياز، شروط القبول، المصروفات"
            )
        return {"text": transcript.text}
    except Exception as e:
        return {"text": f"خطأ في معالجة الصوت: {str(e)}"}
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)