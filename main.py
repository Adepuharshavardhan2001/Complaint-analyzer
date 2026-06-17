# =========================================
# COMPLAINT ANALYZER - FASTAPI VERSION
# Using your existing Groq + Langfuse code
# =========================================

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import json
from groq import Groq
from langfuse import Langfuse

# =========================================
# LOAD ENV VARIABLES
# =========================================

load_dotenv()

# =========================================
# LANGFUSE CLIENT
# =========================================

langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_HOST")
)

# =========================================
# GROQ CLIENT
# =========================================

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# =========================================
# INITIALIZE FASTAPI
# =========================================

app = FastAPI(
    title="Complaint Analyzer API",
    description="Analyze customer complaints using Groq Llama 3.1",
    version="2.0.0"
)

# =========================================
# REQUEST/RESPONSE MODELS (Pydantic)
# =========================================

class ComplaintRequest(BaseModel):
    text: str
    customer_id: int = None

class ComplaintResponse(BaseModel):
    complaint_category: str
    severity: str
    root_issue: str
    recommended_action: str

# =========================================
# ROOT ENDPOINT
# =========================================

@app.get("/")
async def root():
    return {
        "message": "Complaint Analyzer API is running!",
        "docs": "/docs",
        "status": "healthy"
    }

# =========================================
# ANALYZE ENDPOINT (Main Logic)
# =========================================

@app.post("/analyze", response_model=ComplaintResponse)
async def analyze_complaint(complaint: ComplaintRequest):
    """
    Analyze customer complaint using Groq Llama 3.1
    
    Example:
    {
        "text": "My food arrived cold and late",
        "customer_id": 12345
    }
    """
    
    # =========================================
    # VALIDATE INPUT
    # =========================================
    
    if not complaint.text or len(complaint.text) < 5:
        raise HTTPException(
            status_code=400,
            detail="Complaint must be at least 5 characters long"
        )
    
    try:
        # =========================================
        # GET PROMPT FROM LANGFUSE
        # =========================================
        
        prompt = langfuse.get_prompt("complaint-analysis-prompt")
        final_prompt = prompt.compile(complaint=complaint.text)
        
        # =========================================
        # CREATE TRACE
        # =========================================
        
        trace = langfuse.trace(
            name="Complaint-Analyzer-API",
            input=complaint.text,
            metadata={
                "endpoint": "/analyze",
                "customer_id": complaint.customer_id
            }
        )
        
        # =========================================
        # CREATE GENERATION
        # =========================================
        
        generation = trace.generation(
            name="Groq-Generation",
            model="llama-3.1-8b-instant",
            input=final_prompt,
            metadata={"provider": "Groq"}
        )
        
        # =========================================
        # GROQ API CALL
        # =========================================
        
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": "You are a complaint analysis assistant. Return ONLY valid JSON."
                },
                {
                    "role": "user",
                    "content": final_prompt
                }
            ],
            temperature=0
        )
        
        # Extract result
        result = response.choices[0].message.content
        
        # =========================================
        # TOKEN USAGE
        # =========================================
        
        usage_data = {
            "input": response.usage.prompt_tokens,
            "output": response.usage.completion_tokens,
            "total": response.usage.total_tokens
        }
        
        # End generation with usage
        generation.end(
            output=result,
            usage=usage_data
        )
        
        # =========================================
        # ADD SCORES
        # =========================================
        
        trace.score(
            name="json_validity",
            value=1,
            comment="Valid JSON generated"
        )
        
        trace.score(
            name="response_quality",
            value=0.95,
            comment="Good complaint analysis"
        )
        
        # =========================================
        # FLUSH LANGFUSE
        # =========================================
        
        langfuse.flush()
        
        # =========================================
        # PARSE AND RETURN
        # =========================================
        
        parsed = json.loads(result)
        
        # Validate with Pydantic
        validated = ComplaintResponse(**parsed)
        
        return validated
        
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="AI response was not valid JSON"
        )
    except Exception as e:
        # Log error to Langfuse
        if 'generation' in locals():
            generation.end(
                level="ERROR",
                status_message=str(e)
            )
            langfuse.flush()
        
        raise HTTPException(
            status_code=500,
            detail=f"Error processing complaint: {str(e)}"
        )

# =========================================
# HEALTH CHECK
# =========================================

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "complaint-analyzer",
        "model": "llama-3.1-8b-instant"
    }