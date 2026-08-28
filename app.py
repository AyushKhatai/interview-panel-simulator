import os
import json
import logging
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field

from src.profile_builder import CandidateProfileBuilder
from src.agents import get_all_personas
from src.debate_engine import DebateEngine
from src.decision_engine import DecisionEngine
from src.gemini_client import GeminiClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")

app = FastAPI(
    title="HireMind — Multi-Agent AI Interview Panel Simulator",
    description="Executive hiring panel evaluating candidate resumes & transcripts using 4 isolated AI personas, real debate cross-examination, and non-averaging weighted decision logic.",
    version="1.0.0"
)

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

# Cache generated results in memory
CACHE: Dict[str, Any] = {}

class CandidateSummaryResponse(BaseModel):
    id: str = Field(..., description="Candidate ID (A or B)")
    name: str = Field(..., description="Full Candidate Name")
    role: str = Field(..., description="Target Job Role")
    company_experience: str = Field(..., description="Recent Company Experience")

class HealthResponse(BaseModel):
    status: str
    active_agents: int

def get_candidate_data(cid: str) -> Dict[str, Any]:
    """Retrieves or builds candidate profile, independent evals, debate transcript, and decision report."""
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

@app.get("/", response_class=HTMLResponse, summary="Serve Interactive Web Dashboard")
def read_root() -> str:
    """Returns the main interactive web dashboard page."""
    with open(os.path.join("static", "index.html"), "r", encoding="utf-8") as f:
        return f.read()

@app.get("/health", response_model=HealthResponse, summary="Health Check Endpoint")
def health_check() -> HealthResponse:
    """Returns system status and active agent count."""
    return HealthResponse(status="healthy", active_agents=4)

@app.get("/api/candidates", response_model=List[CandidateSummaryResponse], summary="List Available Candidates")
def list_candidates() -> List[CandidateSummaryResponse]:
    """Returns list of evaluated candidates."""
    return [
        CandidateSummaryResponse(id="A", name="Rohan Malhotra", role="Senior AI Engineer", company_experience="Voltrix Logistics"),
        CandidateSummaryResponse(id="B", name="Maya Lin", role="Full-Stack AI Engineer", company_experience="FreightPulse")
    ]

@app.get("/api/candidate/{cid}", summary="Get Full Candidate Evaluation")
def get_candidate_full(cid: str) -> Dict[str, Any]:
    """Returns candidate profile, Phase 1 persona evals, Phase 2 debate data, and Phase 3 final report."""
    if cid.upper() not in ["A", "B"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found")
    return get_candidate_data(cid)

@app.get("/api/comparison", summary="Get Candidate Side-by-Side Comparison")
def get_comparison() -> Dict[str, Any]:
    """Returns comparative ranking matrix between Candidate A and Candidate B."""
    data_a = get_candidate_data("A")
    data_b = get_candidate_data("B")
    return decision_engine.rank_candidates(data_a["final_report"], data_b["final_report"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
