import hashlib
import io
import json
import secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, EmailStr
from dotenv import load_dotenv

load_dotenv()

from .config import FRONTEND_ORIGINS, ARTIFACT_DIR, FRONTEND_URL, RESET_TOKEN_MINUTES
from .database import init_db, get_connection
from .auth import hash_password, verify_password, create_token, current_user
from .nlp import basic_stats, humanize, topic_relevance
from .ml import EssayModel
from .report import generate_report
from .email_service import send_password_reset_email, send_welcome_email

app = FastAPI(title="EssayScorer API", version="3.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = EssayModel()

class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=20, max_length=200)
    password: str = Field(min_length=8, max_length=100)

class EssayRequest(BaseModel):
    essay: str = Field(min_length=1, max_length=100000)
    topic: str | None = None

@app.on_event("startup")
def startup():
    init_db()

@app.get("/")
def root():
    return {"name": "EssayScorer API", "version": "3.0.0", "status": "running"}

@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_available": model.available,
        "evaluation_available": (ARTIFACT_DIR / "evaluation.json").exists(),
    }

@app.post("/auth/register")
def register(req: RegisterRequest):
    conn = get_connection()
    try:
        password_hash = hash_password(req.password)
        conn.execute(
            "INSERT INTO users(name,email,password_hash) VALUES(?,?,?)",
            (req.name.strip(), str(req.email).strip().lower(), password_hash),
        )
        conn.commit()
        user = conn.execute(
            "SELECT id,name,email FROM users WHERE email=?", (str(req.email).strip().lower(),)
        ).fetchone()
        user_data = dict(user)
        email_sent = False
        try:
            email_sent = send_welcome_email(user_data["email"], user_data["name"])
        except Exception:
            # Registration must remain successful even if SMTP is temporarily unavailable.
            # The user can still sign in normally; email_sent tells the UI whether delivery succeeded.
            email_sent = False
        return {
            "message": "Account created successfully. Please sign in with your email and password.",
            "email_sent": email_sent,
            "email": user_data["email"],
            "user": user_data,
        }
    except Exception:
        raise HTTPException(status_code=400, detail="An account with this email already exists or the account data is invalid.")
    finally:
        conn.close()

@app.post("/auth/login")
def login(req: LoginRequest):
    conn = get_connection()
    user = conn.execute("SELECT * FROM users WHERE email=?", (str(req.email).strip().lower(),)).fetchone()
    conn.close()
    if not user or not verify_password(req.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="The email or password is incorrect.")
    return {
        "token": create_token(user["id"]),
        "user": {"id": user["id"], "name": user["name"], "email": user["email"]},
    }

@app.get("/auth/me")
def me(user=Depends(current_user)):
    return user

@app.post("/auth/forgot-password")
def forgot_password(req: ForgotPasswordRequest):
    email = str(req.email).strip().lower()
    conn = get_connection()
    user = conn.execute("SELECT id,name,email FROM users WHERE email=?", (email,)).fetchone()
    if not user:
        conn.close()
        return {"message": "If an account exists for this email, password reset instructions have been sent."}

    raw_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    expires = datetime.now(timezone.utc) + timedelta(minutes=RESET_TOKEN_MINUTES)
    conn.execute("UPDATE password_reset_tokens SET used_at=CURRENT_TIMESTAMP WHERE user_id=? AND used_at IS NULL", (user["id"],))
    conn.execute(
        "INSERT INTO password_reset_tokens(user_id,token_hash,expires_at) VALUES(?,?,?)",
        (user["id"], token_hash, expires.isoformat()),
    )
    conn.commit()
    conn.close()

    reset_link = f"{FRONTEND_URL}/?reset_token={raw_token}"
    try:
        sent = send_password_reset_email(email, reset_link)
    except Exception:
        sent = False

    response = {"message": "If an account exists for this email, password reset instructions have been sent."}
    # Only expose the link when SMTP is not configured, so local development is testable.
    if not sent:
        response["development_reset_link"] = reset_link
    return response

@app.post("/auth/reset-password")
def reset_password(req: ResetPasswordRequest):
    token_hash = hashlib.sha256(req.token.encode()).hexdigest()
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM password_reset_tokens WHERE token_hash=? AND used_at IS NULL",
        (token_hash,),
    ).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=400, detail="This password reset link is invalid or has already been used.")

    try:
        expires = datetime.fromisoformat(row["expires_at"])
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
    except ValueError:
        expires = datetime.min.replace(tzinfo=timezone.utc)
    if expires <= datetime.now(timezone.utc):
        conn.close()
        raise HTTPException(status_code=400, detail="This password reset link has expired. Please request a new one.")

    conn.execute("UPDATE users SET password_hash=? WHERE id=?", (hash_password(req.password), row["user_id"]))
    conn.execute("UPDATE password_reset_tokens SET used_at=CURRENT_TIMESTAMP WHERE id=?", (row["id"],))
    conn.execute("UPDATE password_reset_tokens SET used_at=CURRENT_TIMESTAMP WHERE user_id=? AND used_at IS NULL", (row["user_id"],))
    conn.commit()
    conn.close()
    return {"message": "Your password has been updated successfully. You can now sign in."}

@app.post("/predict")
def predict(req: EssayRequest, user=Depends(current_user)):
    if len(req.essay.strip()) < 10:
        raise HTTPException(status_code=400, detail="Please write a little more so the essay can be evaluated meaningfully.")

    stats = basic_stats(req.essay)
    human = humanize(req.essay)
    topic = topic_relevance(req.essay, req.topic)

    try:
        raw_score = model.predict(req.essay)
        # ASAP-style source scores are 1–6. Present a reader-friendly 1–10 scale.
        score = round(max(1.0, min(10.0, 1.0 + (raw_score - 1.0) * 9.0 / 5.0)), 2)
        raw_score = round(raw_score, 3)
    except RuntimeError:
        score = None
        raw_score = None

    analysis = {
        **stats,
        "topic_relevance": topic,
        "model_available": model.available,
        "raw_model_score": raw_score,
        "score_scale": "1–10 (normalized from the training score scale)",
    }

    conn = get_connection()
    cur = conn.execute(
        """
        INSERT INTO evaluations
        (user_id,essay,topic,predicted_score,word_count,sentence_count,character_count,analysis_json,humanization_json)
        VALUES(?,?,?,?,?,?,?,?,?)
        """,
        (
            user["id"], req.essay, req.topic, score, stats["word_count"],
            stats["sentence_count"], stats["character_count"],
            json.dumps(analysis), json.dumps(human),
        ),
    )
    evaluation_id = cur.lastrowid
    conn.commit()
    conn.close()

    return {
        "evaluation_id": evaluation_id,
        "predicted_score": score,
        "analysis": analysis,
        "humanization": human,
    }

@app.get("/history")
def history(user=Depends(current_user)):
    conn = get_connection()
    rows = conn.execute(
        "SELECT id,predicted_score,word_count,sentence_count,topic,created_at FROM evaluations WHERE user_id=? ORDER BY id DESC",
        (user["id"],),
    ).fetchall()
    conn.close()
    return {"items": [dict(x) for x in rows]}

@app.delete("/evaluations/{evaluation_id}")
def delete_evaluation(evaluation_id: int, user=Depends(current_user)):
    conn = get_connection()
    cur = conn.execute("DELETE FROM evaluations WHERE id=? AND user_id=?", (evaluation_id, user["id"]))
    conn.commit()
    conn.close()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Evaluation not found.")
    return {"message": "Evaluation deleted."}

@app.get("/evaluations/{evaluation_id}")
def get_evaluation(evaluation_id: int, user=Depends(current_user)):
    conn = get_connection()
    row = conn.execute("SELECT * FROM evaluations WHERE id=? AND user_id=?", (evaluation_id, user["id"])).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Evaluation not found.")
    result = dict(row)
    result["analysis"] = json.loads(result["analysis_json"] or "{}")
    result["humanization"] = json.loads(result["humanization_json"] or "{}")
    return result

@app.post("/reports/{evaluation_id}")
def create_report(evaluation_id: int, user=Depends(current_user)):
    evaluation = get_evaluation(evaluation_id, user)
    path = generate_report(evaluation)
    return {"download_url": f"/reports/{evaluation_id}", "filename": Path(path).name}

@app.get("/reports/{evaluation_id}")
def download_report(evaluation_id: int, user=Depends(current_user)):
    evaluation = get_evaluation(evaluation_id, user)
    path = Path(generate_report(evaluation))
    return FileResponse(path, media_type="application/pdf", filename=path.name)

@app.post("/upload")
async def upload(file: UploadFile = File(...), user=Depends(current_user)):
    data = await file.read()
    name = (file.filename or "").lower()
    text = ""
    if name.endswith(".txt"):
        text = data.decode("utf-8", errors="ignore")
    elif name.endswith(".pdf"):
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(data))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    elif name.endswith(".docx"):
        from docx import Document
        doc = Document(io.BytesIO(data))
        text = "\n".join(p.text for p in doc.paragraphs)
    else:
        raise HTTPException(status_code=400, detail="Supported files: TXT, PDF, DOCX.")
    if not text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from the uploaded file.")
    return {"filename": file.filename, "text": text[:100000]}




@app.post("/humanize")
def humanize_essay(payload: dict, user=Depends(current_user)):
    text=str(payload.get("essay") or "").strip()
    if len(text)<10: raise HTTPException(400,"Write at least 10 characters for natural-writing suggestions.")
    return humanize(text)

@app.get("/dashboard")
def dashboard(user=Depends(current_user)):
    conn=get_connection()
    rows=conn.execute("SELECT id,predicted_score,word_count,created_at,topic FROM evaluations WHERE user_id=? ORDER BY id DESC",(user["id"],)).fetchall()
    docs=conn.execute("SELECT COUNT(*) c FROM documents WHERE user_id=?",(user["id"],)).fetchone()["c"]
    reports=conn.execute("SELECT COUNT(*) c FROM evaluations WHERE user_id=? AND predicted_score IS NOT NULL",(user["id"],)).fetchone()["c"]
    quiz=conn.execute("SELECT score,total,created_at FROM quiz_attempts WHERE user_id=? ORDER BY id DESC LIMIT 1",(user["id"],)).fetchone()
    conn.close()
    scores=[float(r["predicted_score"]) for r in rows if r["predicted_score"] is not None]
    avg=round(sum(scores)/len(scores),2) if scores else None
    improvement=None
    if len(scores)>=2: improvement=round(scores[0]-scores[-1],2)
    return {"essays_analyzed":len(rows),"average_score":avg,"score_improvement":improvement,"documents":docs,"reports":reports,"latest_quiz":dict(quiz) if quiz else None,"recent":[dict(r) for r in rows[:6]]}

@app.get("/analytics")
def analytics(user=Depends(current_user)):
    conn=get_connection()
    rows=conn.execute("SELECT id,predicted_score,word_count,sentence_count,analysis_json,created_at FROM evaluations WHERE user_id=? ORDER BY id ASC",(user["id"],)).fetchall()
    conn.close()
    points=[]
    for r in rows:
        a=json.loads(r["analysis_json"] or "{}")
        points.append({"id":r["id"],"score":r["predicted_score"],"words":r["word_count"],"sentences":r["sentence_count"],"vocabulary":a.get("vocabulary_richness",0),"readability":a.get("readability",0),"date":r["created_at"]})
    return {"points":points}

@app.post("/documents")
def create_document(payload: dict, user=Depends(current_user)):
    filename=str(payload.get("filename") or "Untitled document")[:255]
    content=str(payload.get("content") or "")
    if not content.strip(): raise HTTPException(400,"Document content is empty.")
    conn=get_connection(); cur=conn.execute("INSERT INTO documents(user_id,filename,content,content_type) VALUES(?,?,?,?)",(user["id"],filename,content,payload.get("content_type"))); conn.commit(); doc_id=cur.lastrowid; conn.close()
    return {"id":doc_id,"filename":filename}

@app.get("/documents")
def list_documents(user=Depends(current_user)):
    conn=get_connection(); rows=conn.execute("SELECT id,filename,content_type,uploaded_at,last_accessed,access_count,length(content) content_length FROM documents WHERE user_id=? ORDER BY id DESC",(user["id"],)).fetchall(); conn.close()
    return {"items":[dict(r) for r in rows]}

@app.get("/documents/{document_id}")
def get_document(document_id:int,user=Depends(current_user)):
    conn=get_connection(); row=conn.execute("SELECT * FROM documents WHERE id=? AND user_id=?",(document_id,user["id"])).fetchone()
    if not row: conn.close(); raise HTTPException(404,"Document not found.")
    conn.execute("UPDATE documents SET access_count=access_count+1,last_accessed=CURRENT_TIMESTAMP WHERE id=?",(document_id,)); conn.commit(); conn.close()
    return dict(row)

@app.delete("/documents/{document_id}")
def delete_document(document_id:int,user=Depends(current_user)):
    conn=get_connection(); cur=conn.execute("DELETE FROM documents WHERE id=? AND user_id=?",(document_id,user["id"])); conn.commit(); conn.close()
    if not cur.rowcount: raise HTTPException(404,"Document not found.")
    return {"message":"Document deleted."}

QUIZ=[
 {"id":1,"q":"Which metric measures the proportion of unique words in an essay?","options":["Vocabulary richness","Character count","Paragraph count","Punctuation density"],"answer":0},
 {"id":2,"q":"What does TF-IDF primarily represent?","options":["Term importance in documents","Password strength","PDF page count","User activity"],"answer":0},
 {"id":3,"q":"Which metric penalizes prediction errors using absolute differences?","options":["MAE","R²","Accuracy","Vocabulary richness"],"answer":0},
 {"id":4,"q":"Which model is used as the primary scoring model in EssayScorer?","options":["Linear Regression","K-Means","Naive Bayes","Decision Tree"],"answer":0},
 {"id":5,"q":"What is the purpose of natural-writing suggestions?","options":["Improve clarity and readability","Hide authorship","Bypass plagiarism checks","Increase word count automatically"],"answer":0},
 {"id":6,"q":"Which file type can EssayScorer extract text from?","options":["PDF","TXT","DOCX","All of these"],"answer":3},
 {"id":7,"q":"A lower RMSE generally indicates what on the same test set?","options":["Smaller prediction errors","More documents","More paragraphs","More unique words"],"answer":0},
 {"id":8,"q":"Which database is used for the local MVP?","options":["SQLite","Redis","MongoDB","Oracle"],"answer":0},
 {"id":9,"q":"What does R² describe in regression evaluation?","options":["Variance explained by the model","Number of words","Password entropy","PDF quality"],"answer":0},
 {"id":10,"q":"Which feature counts question marks in an essay?","options":["question_count","word_count","unique_word_count","paragraph_count"],"answer":0},
]

@app.get("/quiz")
def quiz(user=Depends(current_user)):
    return {"questions":[{"id":x["id"],"question":x["q"],"options":x["options"]} for x in QUIZ]}

@app.post("/quiz/submit")
def submit_quiz(payload:dict,user=Depends(current_user)):
    answers=payload.get("answers") or []
    score=0
    for q in QUIZ:
        val=answers[q["id"]-1] if q["id"]-1 < len(answers) else -1
        if val==q["answer"]: score+=1
    conn=get_connection(); cur=conn.execute("INSERT INTO quiz_attempts(user_id,score,total,answers_json) VALUES(?,?,?,?)",(user["id"],score,len(QUIZ),json.dumps(answers))); conn.commit(); attempt_id=cur.lastrowid; conn.close()
    return {"attempt_id":attempt_id,"score":score,"total":len(QUIZ),"percentage":round(score*100/len(QUIZ),1)}

@app.get("/quiz/history")
def quiz_history(user=Depends(current_user)):
    conn=get_connection(); rows=conn.execute("SELECT id,score,total,created_at FROM quiz_attempts WHERE user_id=? ORDER BY id DESC LIMIT 10",(user["id"],)).fetchall(); conn.close(); return {"items":[dict(r) for r in rows]}

@app.get("/reports")
def report_history(user=Depends(current_user)):
    conn=get_connection(); rows=conn.execute("SELECT id,predicted_score,topic,created_at,word_count FROM evaluations WHERE user_id=? ORDER BY id DESC",(user["id"],)).fetchall(); conn.close(); return {"items":[dict(r) for r in rows]}

@app.get("/coach")
def coach(user=Depends(current_user)):
    return {"lessons":[
      {"title":"Build a clear introduction","body":"State the topic, context and main direction early so the reader knows what to expect."},
      {"title":"Strengthen evidence","body":"Support major claims with a concrete example, explanation or relevant evidence."},
      {"title":"Improve transitions","body":"Use transitions only when they accurately show contrast, cause, sequence or example."},
      {"title":"Write a purposeful conclusion","body":"Restate the central idea in fresh words and close with a meaningful implication."},
    ]}

@app.get("/model-metrics")
def model_metrics(user=Depends(current_user)):
    path = ARTIFACT_DIR / "evaluation.json"
    if not path.exists():
        return {"available": False, "message": "Run training/evaluation first."}
    return {"available": True, **json.loads(path.read_text())}
