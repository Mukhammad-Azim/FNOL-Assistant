# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
import openai

# Initialize OpenAI with your environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI(title="FNOL Assistant Backend")

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
        # Build the prompt for OpenAI
        prompt = f"""
You are an insurance AI assistant. 

You receive the following FNOL (First Notice of Loss) report:

Date: {data.date}
Location: {data.location}
Description: {data.description}
Images: {', '.join([img.url or img.filename for img in data.images])}

Your job:
1. Normalize the date into dd.mm.yyyy format.
2. Extract full address if possible (street, number, city, postal code, country).
3. Analyze damage severity and possible injuries.
4. Produce a "risk_category" and liability estimate if applicable.
5. Give clear recommendations to the user about next steps.

Return **only valid JSON** with the following fields:

{{
    "date_normalized": "",
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
            max_tokens=400
        )

        summary_text = response.choices[0].message.content

        # Return the summary along with original data
        return {
            "original_data": data.dict(),
            "fnol_summary": summary_text
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
