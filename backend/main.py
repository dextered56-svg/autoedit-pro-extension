import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

# Import modules
import modules.silence as silence_module
import modules.visual as visual_module
import modules.multicam as multicam_module
import modules.captions as captions_module

app = FastAPI(title="AutoEdit Pro Backend API")

# Configure CORS for Premiere Pro CEP extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For production, restrict this to CEP origin
    allow_credentials=False, # Fix: Cannot use allow_credentials=True with allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "AutoEdit Pro Backend is running"}

class SilenceRequest(BaseModel):
    filepath: str
    noise_floor: int = -40
    min_silence_len: int = 500
    padding: int = 100

@app.post("/api/detect_silence")
def detect_silence(req: SilenceRequest):
    return silence_module.detect(req.filepath, req.noise_floor, req.min_silence_len, req.padding)

class VisualRequest(BaseModel):
    filepath: str
    scale_percent: int = 150
    center_sensitivity: int = 50

@app.post("/api/visual_automation")
def visual_automation(req: VisualRequest):
    return visual_module.process(req.filepath, req.scale_percent, req.center_sensitivity)

class MulticamRequest(BaseModel):
    filepath: str
    num_speakers: Optional[int] = None

@app.post("/api/multicam_switch")
def multicam_switch(req: MulticamRequest):
    return multicam_module.diarize(req.filepath, req.num_speakers)

class CaptionRequest(BaseModel):
    filepath: str
    filter_profanity: bool = True

@app.post("/api/captions")
def generate_captions(req: CaptionRequest):
    return captions_module.generate(req.filepath, req.filter_profanity)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)
