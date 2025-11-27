from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
import openai
from fastapi.middleware.cors import CORSMiddleware

# Initialize OpenAI with your environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

# Allow CORS so Make.com can call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, restrict to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic models for validation ---
class Image(BaseModel):
    filename: str
    url: Optional[str] = None

class FNOLRequest(BaseModel):
    date: str
    location: str
    description: str
    images: Optional[List[Image]] = []

# --- API endpoint ---
@app.post("/fnol")
async def analyze_fnol(data: FNOLRequest):
    try:
        # Create prompt for OpenAI
        prompt = f"""
You are analyzing an insurance claim with the following fields:
- date: {data.date}
- location: {data.location}
- description: {data.description}
- images: {data.images}

Please generate ONLY valid JSON with the following fields:
{{
    "date_normalized": "dd.mm.yyyy",
    "location_normalized": {{
        "street": "",
        "street_number": "",
        "city": "",
        "postal_code": "",
        "country": ""
    }},
    "risk_category": "",
    "estimated_damage_severity": "",
    "injury_assessment": "",
    "liability_estimate": "",
    "recommendations": ""
}}
"""

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=500
        )

        fnol_summary = response.choices[0].message.content

        return {
            "original_data": data.dict(),
            "fnol_summary": fnol_summary
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
