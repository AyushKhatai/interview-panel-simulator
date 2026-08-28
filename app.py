import os
import json
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from src.profile_builder import CandidateProfileBuilder
from src.agents import get_all_personas
from src.debate_engine import DebateEngine
from src.decision_engine import DecisionEngine
from src.gemini_client import GeminiClient

app = FastAPI(title="HireMind — Multi-Agent AI Interview Panel Simulator")

# Serve static files for frontend dashboard
app.mount("/static", StaticFiles(directory="static"), name="static")

gemini_client = GeminiClient()
jd_path = os.path.join("data", "02_Job_Description.pdf")
resume_a_path = os.path.join("data", "03_Resume_A.pdf")
resume_b_path = os.path.join("data", "04_Resume_B.pdf")
transcript_a_path = os.path.join("data", "05_Transcript_A.pdf")
transcript_b_path = os.path.join("data", "06_Transcript_B.pdf")

profile_builder_a = CandidateProfileBuilder(jd_path, resume_a_path, transcript_a_path)
profile_builder_b = CandidateProfileBuilder(jd_path, resume_b_path, transcript_b_path)
decision_engine = DecisionEngine()

# Cache generated results in memory for instant speed
CACHE = {}

def get_candidate_data(cid: str):
    cid = cid.upper()
    if cid in CACHE:
        return CACHE[cid]
    
    pb = profile_builder_a if cid == "A" else profile_builder_b
    profile = pb.build_profile(cid)
    
    personas = get_all_personas(gemini_client)
    initial_evals = {agent.name: agent.evaluate_independent(profile) for agent in personas}
    
    debate_engine = DebateEngine(gemini_client)
    debate_data = debate_engine.run_debate(profile, initial_evals)
    
    final_report = decision_engine.synthesize_decision(profile, initial_evals, debate_data)
    
    res = {
        "profile": profile,
        "initial_evals": initial_evals,
        "debate_data": debate_data,
        "final_report": final_report
    }
    CACHE[cid] = res
    return res

@app.get("/", response_class=HTMLResponse)
def read_root():
    with open(os.path.join("static", "index.html"), "r", encoding="utf-8") as f:
        return f.read()

@app.get("/api/candidates")
def list_candidates():
    return [
        {"id": "A", "name": "Rohan Malhotra", "role": "Senior AI Engineer", "company_experience": "Voltrix Logistics"},
        {"id": "B", "name": "Maya Lin", "role": "Full-Stack AI Engineer", "company_experience": "FreightPulse"}
    ]

@app.get("/api/candidate/{cid}")
def get_candidate_full(cid: str):
    if cid.upper() not in ["A", "B"]:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return get_candidate_data(cid)

@app.get("/api/comparison")
def get_comparison():
    data_a = get_candidate_data("A")
    data_b = get_candidate_data("B")
    return decision_engine.rank_candidates(data_a["final_report"], data_b["final_report"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
