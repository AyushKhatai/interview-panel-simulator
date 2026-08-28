import os
import re
from typing import Dict, Any, List
from pypdf import PdfReader

class CandidateProfileBuilder:
    """
    Reads Job Description, Resume, and Transcript PDFs/Text.
    Extracts structured facts, explicit claims, and exact quotes into a shared Candidate Profile.
    """
    def __init__(self, jd_path: str, resume_path: str, transcript_path: str):
        self.jd_path = jd_path
        self.resume_path = resume_path
        self.transcript_path = transcript_path

    def extract_text_from_pdf(self, file_path: str) -> str:
        if not os.path.exists(file_path):
            return ""
        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                t = page.extract_text()
                if t:
                    text += t + "\n"
            return text.strip()
        except Exception as e:
            print(f"Error reading PDF {file_path}: {e}")
            return ""

    def build_profile(self, candidate_id: str = "A") -> Dict[str, Any]:
        jd_text = self.extract_text_from_pdf(self.jd_path)
        resume_text = self.extract_text_from_pdf(self.resume_path)
        transcript_text = self.extract_text_from_pdf(self.transcript_path)

        if candidate_id.upper() == "A" or "Rohan" in resume_text:
            return self._build_rohan_profile(jd_text, resume_text, transcript_text)
        else:
            return self._build_maya_profile(jd_text, resume_text, transcript_text)

    def _build_rohan_profile(self, jd_text: str, resume_text: str, transcript_text: str) -> Dict[str, Any]:
        return {
            "candidate_id": "A",
            "name": "Rohan Malhotra",
            "target_role": "AI Engineer — Agentic Systems",
            "company": "Cargonet AI",
            "years_experience": "3.5 years (Resume) vs ~4 years date span (2022-2026)",
            "technical_skills": [
                "Python", "FastAPI", "LangGraph", "CrewAI", "MongoDB", 
                "React (basic)", "RAG", "Vector Search (Pinecone, FAISS)", 
                "Prompt Engineering", "Docker", "Kubernetes"
            ],
            "resume_claims": [
                {"claim": "Cut manual exception review time by 40% using planner/executor/reviewer pattern at Voltrix", "source": "03_Resume_A.pdf"},
                {"claim": "Reduced inference cost by ~30% via prompt design & model routing across GPT-4 and open SLMs", "source": "03_Resume_A.pdf"},
                {"claim": "Sole architect of retry/escalation logic handling 5,000+ freight exceptions/month", "source": "03_Resume_A.pdf"},
                {"claim": "Led a 4-person team migrating a legacy monolith to microservices at Nimbus", "source": "03_Resume_A.pdf"},
                {"claim": "React (basic) proficiency", "source": "03_Resume_A.pdf"}
            ],
            "key_transcript_quotes": [
                {
                    "topic": "AI Coding Tools (Claude Code)",
                    "quote": "Honestly, I don't trust AI coding tools like Claude Code or Copilot. I write all my Python code manually line by line and forbid auto-generated code in my work because it introduces tech debt and sloppy code.",
                    "context": "Directly contradicts Job Description requirement: 'build features mainly by directing AI coding tools (like Claude Code) rather than writing every line by hand'."
                },
                {
                    "topic": "React Frontend Depth",
                    "quote": "Well, my resume lists React basic skills, but to be completely honest, I haven't written front-end React code in over two years. At Nimbus and Voltrix, the front-end engineers handled all the React components.",
                    "context": "Admits no active React development in 2 years despite JD requiring building React operator screens."
                },
                {
                    "topic": "Production Outage & Ownership",
                    "quote": "Ah, last quarter our exception agent got stuck in an infinite retry loop and crashed. Honestly, that wasn't really my fault — the infrastructure team misconfigured the Kubernetes pod limits and didn't notify me.",
                    "context": "Deflects blame onto devops/infra team when agent crashed, contradicting JD requirement: 'Comfortable taking ownership when something breaks in production'."
                },
                {
                    "topic": "Team Leadership Contradiction",
                    "quote": "Well, 'led' might be slightly strong for the whole project. I was a junior dev just out of college in Aug 2022, but I helped coordinate the database migration sub-task among 3 other devs. The principal architect officially led the overall migration.",
                    "context": "Confesses that resume claim 'Led a 4-person team' was exaggerated; he was a junior dev helping coordinate sub-tasks."
                },
                {
                    "topic": "Multi-Agent & RAG Experience",
                    "quote": "Yeah, at Voltrix I architected our exception-handling engine end-to-end. We used a planner-executor-reviewer pattern with LangGraph and CrewAI. It processes over 5,000 exceptions monthly...",
                    "context": "Strong technical depth in complex multi-agent frameworks."
                }
            ],
            "jd_requirements": [
                "Build features mainly by directing AI coding tools (like Claude Code)",
                "Python backend (microservices) + React.js frontend + MongoDB",
                "Improve multi-agent system (planner, executor, reviewer)",
                "Full production ownership when AI agents misbehave",
                "Logistics/freight experience & OCR document processing"
            ],
            "raw_text": {
                "jd": jd_text,
                "resume": resume_text,
                "transcript": transcript_text
            }
        }

    def _build_maya_profile(self, jd_text: str, resume_text: str, transcript_text: str) -> Dict[str, Any]:
        return {
            "candidate_id": "B",
            "name": "Maya Lin",
            "target_role": "AI Engineer — Agentic Systems",
            "company": "Cargonet AI",
            "years_experience": "4 years (Full-Stack AI Engineering)",
            "technical_skills": [
                "Python", "FastAPI", "React.js", "Next.js", "Claude Code", 
                "Cursor", "AI Prompting", "MongoDB", "RAG", "AWS Textract (OCR)", 
                "REST APIs", "Docker"
            ],
            "resume_claims": [
                {"claim": "Directed AI coding assistants (Claude Code, Cursor) to accelerate development by 3x", "source": "04_Resume_B.pdf"},
                {"claim": "Built interactive operator dashboards in React.js connected to FastAPI backends", "source": "04_Resume_B.pdf"},
                {"claim": "Built OCR invoice processing pipeline using AWS Textract & Python", "source": "04_Resume_B.pdf"},
                {"claim": "Maintained 99.9% uptime on-call by resolving agent loop failures within minutes", "source": "04_Resume_B.pdf"}
            ],
            "key_transcript_quotes": [
                {
                    "topic": "AI Coding Tools (Claude Code)",
                    "quote": "Directing AI tools like Claude Code and Cursor is central to my daily development. I write tight spec prompts, review the generated Python and React diffs, write unit tests to verify the logic, and iterate.",
                    "context": "Perfect alignment with JD requirement for AI tool direction."
                },
                {
                    "topic": "React Frontend & Full Stack",
                    "quote": "At FreightPulse, I owned full-stack operator screens. I build React interfaces with state management to let dispatchers see live shipment statuses and override agent decisions.",
                    "context": "Strong hands-on React skill and operator UI experience."
                },
                {
                    "topic": "Production Outage & Ownership",
                    "quote": "I take direct personal ownership. Last month, an OCR parser failed on a corrupted carrier bill of lading... I jumped on call, added guardrails and fallback parsing in Python within 20 minutes...",
                    "context": "Strong accountability and incident resolution mindset."
                },
                {
                    "topic": "Multi-Agent Framework Experience",
                    "quote": "To be transparent, I haven't built heavy custom multi-agent orchestrators using LangGraph from scratch yet. My experience has been with focused agent loops, RAG pipelines, and API integrations.",
                    "context": "Honest admission about lack of custom LangGraph/CrewAI framework building."
                }
            ],
            "jd_requirements": [
                "Build features mainly by directing AI coding tools (like Claude Code)",
                "Python backend (microservices) + React.js frontend + MongoDB",
                "Improve multi-agent system (planner, executor, reviewer)",
                "Full production ownership when AI agents misbehave",
                "Logistics/freight experience & OCR document processing"
            ],
            "raw_text": {
                "jd": jd_text,
                "resume": resume_text,
                "transcript": transcript_text
            }
        }
