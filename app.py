from fastapi import FastAPI, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from transformers import pipeline
import os

app = FastAPI()
security = HTTPBearer()

# تنظیمات
MODEL_NAME = "google/flan-t5-base"
API_TOKEN = os.environ.get("API_TOKEN", "your-secret-token")

# لود مدل
print("🌀 در حال لود مدل Flan-T5-Base...")
pipe = pipeline("text2text-generation", model=MODEL_NAME)
print("✅ مدل لود شد!")

@app.post("/generate")
async def generate_text(
    prompt: str,
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    if credentials.credentials != API_TOKEN:
        raise HTTPException(status_code=401, detail="توکن نامعتبر")
    
    try:
        # تولید پاسخ
        result = pipe(
            prompt,
            max_length=150,
            temperature=0.7,
            do_sample=True
        )
        
        return {"response": result[0]['generated_text']}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "model": MODEL_NAME}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
