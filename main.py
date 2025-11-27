from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

# --- Pydantic models ---
class Image(BaseModel):
    filename: Optional[str] = None
    name: Optional[str] = None
    url: Optional[str] = None
    
    def get_filename(self):
        return self.filename or self.name

class FNOLRequest(BaseModel):
    incident_type: str
    date: str
    location: str
    severity: str
    third_party: str
    injuries: str
    description: str
    images: Optional[List[Image]] = []  # Expect a list

# --- API endpoint ---
@app.post("/fnol")
async def analyze_fnol(data: FNOLRequest):
    try:
        # Build OpenAI prompt
        prompt = f"""
You are an insurance assistant AI.

You receive FNOL data with fields:
- Date: {data.date}
- Location: {data.location}
- Description: {data.description}
- Number of images: {len(data.images)}

Task:
1. Analyze the claim and provide clear recommendations for the user on the next steps (e.g., contact police, take photos, contact insurance).
2. Ignore actual image content, just note how many images were received.
3. Return a concise text message to show the user.

Return only plain text suitable for displaying to the user.
"""

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=300
        )

        recommendation_text = response.choices[0].message.content

        # Return the summary along with original data
        return {
            "original_data": data.dict(),
            "recommendation": recommendation_text
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
