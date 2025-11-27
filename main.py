from fastapi import FastAPI
from pydantic import BaseModel
import requests
import os

MAKE_WEBHOOK_URL = os.getenv("MAKE_WEBHOOK_URL")

app = FastAPI()

class Claim(BaseModel):
    incident_type: str
    incident_date: str
    location: str
    description: str
    third_party: bool
    injuries: bool
    severity: str
    images: list

@app.post("/submit_claim")
def submit_claim(claim: Claim):

    # Send to Make.com and WAIT for response
    make_response = requests.post(
        MAKE_WEBHOOK_URL,
        json=claim.dict(),
        timeout=120  # give Make enough time
    )

    # Parse response
    try:
        result = make_response.json()
    except:
        result = {"recommendations": None}

    # Return the recommendations back to Gradio
    return {
        "status": make_response.status_code,
        "recommendations": result.get("recommendations", "No recommendation"),
        "processed_data": result
    }
