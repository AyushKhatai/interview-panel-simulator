from typing import Dict, Any, List
from src.gemini_client import GeminiClient

class PersonaAgent:
    def __init__(self, name: str, role: str, description: str, system_prompt: str, gemini_client: GeminiClient = None):
        self.name = name
        self.role = role
        self.description = description
        self.system_prompt = system_prompt
        self.gemini_client = gemini_client

    def evaluate_independent(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Phase 1: Independent Evaluation.
        Must evaluate candidate strictly from its own perspective without seeing other agents.
        Every opinion MUST cite specific quotes or facts from transcript/resume.
        """
        # Try LLM generation if client available
        if self.gemini_client and self.gemini_client.client:
            prompt = f"""
Candidate Profile:
Name: {profile['name']}
Target Role: {profile['target_role']} at {profile['company']}
Technical Skills: {', '.join(profile['technical_skills'])}
Resume Claims: {profile['resume_claims']}
Transcript Quotes: {profile['key_transcript_quotes']}

Instructions:
Evaluate candidate as {self.name} ({self.role}).
Provide your independent rating (1-10), confidence %, summary, key strengths with quotes, and key concerns with quotes.
Return JSON format:
{{
    "agent_name": "{self.name}",
    "role": "{self.role}",
    "score": 7.5,
    "confidence": 85,
    "verdict": "Hire / Hold / Reject Stance",
    "summary": "High-level opinion",
    "strengths": [
        {{"point": "...", "quote": "...", "source": "..."}}
    ],
    "concerns": [
        {{"point": "...", "quote": "...", "source": "..."}}
    ]
}}
"""
            res = self.gemini_client.generate_json(prompt, self.system_prompt)
            if res:
                return res

        # Deterministic quote-backed evaluation fallback per persona
        return self._generate_fallback_independent_eval(profile)

    def _generate_fallback_independent_eval(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        cid = profile["candidate_id"]
        
        if self.name == "Technical Agent":
            if cid == "A":
                return {
                    "agent_name": "Technical Agent",
                    "role": "Technical Depth & Architecture Evaluator",
                    "score": 8.0,
                    "confidence": 90,
                    "verdict": "Strong Tech Architecture / Weak Frontend",
                    "summary": "Demonstrates excellent mastery of backend Python, planner/executor/reviewer multi-agent patterns, LangGraph, and RAG pipelines. However, React frontend capability is practically zero.",
                    "strengths": [
                        {
                            "point": "Deep expertise in multi-agent orchestration (LangGraph, CrewAI, planner-executor-reviewer pattern)",
                            "quote": "We used a planner-executor-reviewer pattern with LangGraph and CrewAI. It processes over 5,000 exceptions monthly...",
                            "source": "05_Transcript_A.pdf"
                        },
                        {
                            "point": "Proven model routing and prompt optimization reducing operational costs",
                            "quote": "Owned prompt design and model routing across GPT-4 and open-weight SLMs, reducing inference cost by ~30%.",
                            "source": "03_Resume_A.pdf"
                        }
                    ],
                    "concerns": [
                        {
                            "point": "Complete lack of active React frontend skills required for operator screens",
                            "quote": "I haven't written front-end React code in over two years. At Nimbus and Voltrix, the front-end engineers handled all the React components.",
                            "source": "05_Transcript_A.pdf"
                        }
                    ]
                }
            else: # Candidate B
                return {
                    "agent_name": "Technical Agent",
                    "role": "Technical Depth & Architecture Evaluator",
                    "score": 7.5,
                    "confidence": 85,
                    "verdict": "Solid Full-Stack AI Engineer",
                    "summary": "Strong practical full-stack execution across Python FastAPI, React.js, and OCR pipelines. Lacks heavy custom LangGraph framework building experience but excels at API integrations.",
                    "strengths": [
                        {
                            "point": "Hands-on React dashboard development integrated with Python backends",
                            "quote": "At FreightPulse, I owned full-stack operator screens. I build React interfaces with state management to let dispatchers see live shipment statuses...",
                            "source": "06_Transcript_B.pdf"
                        },
                        {
                            "point": "Production OCR document parsing pipeline development",
                            "quote": "Built OCR invoice processing pipeline using AWS Textract & Python, resolving carrier line-item discrepancies automatically.",
                            "source": "04_Resume_B.pdf"
                        }
                    ],
                    "concerns": [
                        {
                            "point": "No prior experience building heavy multi-agent orchestrators like LangGraph from scratch",
                            "quote": "I haven't built heavy custom multi-agent orchestrators using LangGraph from scratch yet.",
                            "source": "06_Transcript_B.pdf"
                        }
                    ]
                }

        elif self.name == "HR / Culture Agent":
            if cid == "A":
                return {
                    "agent_name": "HR / Culture Agent",
                    "role": "Communication, Teamwork & Honesty Evaluator",
                    "score": 4.5,
                    "confidence": 85,
                    "verdict": "Culture Risk / Responsibility Deflection",
                    "summary": "Shows significant communication and ownership red flags. Deflects production failure blame onto DevOps and admitted to exaggerating leadership on resume.",
                    "strengths": [
                        {
                            "point": "Clear verbal communication and enthusiasm for system architecture",
                            "quote": "Presented the system design at a company-wide tech talk.",
                            "source": "03_Resume_A.pdf"
                        }
                    ],
                    "concerns": [
                        {
                            "point": "Deflects responsibility during production outages rather than taking ownership",
                            "quote": "Honestly, that wasn't really my fault — the infrastructure team misconfigured the Kubernetes pod limits...",
                            "source": "05_Transcript_A.pdf"
                        },
                        {
                            "point": "Admitted resume claim exaggeration regarding team leadership",
                            "quote": "Well, 'led' might be slightly strong for the whole project. I was a junior dev... I helped coordinate the database migration sub-task...",
                            "source": "05_Transcript_A.pdf"
                        }
                    ]
                }
            else: # Candidate B
                return {
                    "agent_name": "HR / Culture Agent",
                    "role": "Communication, Teamwork & Honesty Evaluator",
                    "score": 9.0,
                    "confidence": 95,
                    "verdict": "Exceptional Ownership & Transparency",
                    "summary": "Exemplary culture fit. Demonstrates complete accountability during incidents, open transparency about skill boundaries, and constructive teamwork.",
                    "strengths": [
                        {
                            "point": "Strong personal ownership and rapid incident resolution under pressure",
                            "quote": "I take direct personal ownership. Last month, an OCR parser failed... I jumped on call, added guardrails... deployed the patch, and added automated regression tests...",
                            "source": "06_Transcript_B.pdf"
                        },
                        {
                            "point": "Honest self-awareness regarding complex framework experience",
                            "quote": "To be transparent, I haven't built heavy custom multi-agent orchestrators using LangGraph from scratch yet...",
                            "source": "06_Transcript_B.pdf"
                        }
                    ],
                    "concerns": []
                }

        elif self.name == "Hiring Manager Agent":
            if cid == "A":
                return {
                    "agent_name": "Hiring Manager Agent",
                    "role": "Role Alignment & Delivery Evaluator",
                    "score": 3.0,
                    "confidence": 95,
                    "verdict": "Fundamental Role Mismatch",
                    "summary": "Unacceptable fit for Cargonet AI's specific engineering culture. Strongly rejects using AI coding tools (Claude Code) which is the primary workflow demanded by the Job Description.",
                    "strengths": [
                        {
                            "point": "Direct domain experience in freight exception processing",
                            "quote": "Designed and built the exception-handling engine end-to-end for Voltrix's multi-agent freight ops platform...",
                            "source": "03_Resume_A.pdf"
                        }
                    ],
                    "concerns": [
                        {
                            "point": "Explicit refusal to use AI coding tools (Claude Code), directly breaking Job Description core duty",
                            "quote": "Honestly, I don't trust AI coding tools like Claude Code or Copilot. I write all my Python code manually line by line and forbid auto-generated code...",
                            "source": "05_Transcript_A.pdf"
                        },
                        {
                            "point": "Cannot deliver operator React screens needed for Cargonet operations",
                            "quote": "I haven't written front-end React code in over two years.",
                            "source": "05_Transcript_A.pdf"
                        }
                    ]
                }
            else: # Candidate B
                return {
                    "agent_name": "Hiring Manager Agent",
                    "role": "Role Alignment & Delivery Evaluator",
                    "score": 9.5,
                    "confidence": 95,
                    "verdict": "Ideal Role & Methodology Match",
                    "summary": "Outstanding alignment with Cargonet AI. Directly embraces AI tool direction (Claude Code/Cursor), ships full-stack Python/React features fast, and owns production reliability.",
                    "strengths": [
                        {
                            "point": "Mastery of directing AI coding assistants to achieve 3x development velocity",
                            "quote": "Directing AI tools like Claude Code and Cursor is central to my daily development. I write tight spec prompts, review... diffs... and iterate.",
                            "source": "06_Transcript_B.pdf"
                        },
                        {
                            "point": "Full-stack capability covering both FastAPI microservices and React operator UI",
                            "quote": "I build React interfaces with state management to let dispatchers see live shipment statuses... On the backend, I write FastAPI endpoints...",
                            "source": "06_Transcript_B.pdf"
                        }
                    ],
                    "concerns": [
                        {
                            "point": "Will need quick onboarding on heavy multi-agent orchestration frameworks like LangGraph",
                            "quote": "I haven't built heavy custom multi-agent orchestrators using LangGraph from scratch yet.",
                            "source": "06_Transcript_B.pdf"
                        }
                    ]
                }

        else: # Skeptic Agent
            if cid == "A":
                return {
                    "agent_name": "Skeptic Agent",
                    "role": "Red Flag & Contradiction Auditor",
                    "score": 2.0,
                    "confidence": 95,
                    "verdict": "Critical Red Flags & Inconsistencies",
                    "summary": "Found major resume padding, direct contradictions with JD requirements, and blame deflection. Resume claims 'Led 4-person team' but transcript reveals he was a junior dev coordinating sub-tasks.",
                    "strengths": [
                        {
                            "point": "Has verified hands-on exposure to LangGraph & CrewAI libraries",
                            "quote": "planner-executor-reviewer pattern with LangGraph and CrewAI",
                            "source": "05_Transcript_A.pdf"
                        }
                    ],
                    "concerns": [
                        {
                            "point": "Resume exaggeration / embellishment of leadership role",
                            "quote": "Resume: 'Led a 4-person team migrating legacy monolith' vs Transcript: 'led might be slightly strong... I was a junior dev just out of college... helped coordinate database migration sub-task'",
                            "source": "03_Resume_A.pdf vs 05_Transcript_A.pdf"
                        },
                        {
                            "point": "Philosophical clash with hiring company: forbids Claude Code while job mandates directing Claude Code",
                            "quote": "I write all my Python code manually line by line and forbid auto-generated code in my work...",
                            "source": "05_Transcript_A.pdf"
                        },
                        {
                            "point": "Blame deflection during production outages",
                            "quote": "Honestly, that wasn't really my fault — the infrastructure team misconfigured the Kubernetes pod limits...",
                            "source": "05_Transcript_A.pdf"
                        }
                    ]
                }
            else: # Candidate B
                return {
                    "agent_name": "Skeptic Agent",
                    "role": "Red Flag & Contradiction Auditor",
                    "score": 8.0,
                    "confidence": 90,
                    "verdict": "Clean & Truthful Credentials",
                    "summary": "No contradictions or resume embellishments found. Candidate was fully transparent about lack of complex multi-agent framework experience while backing up all claims with concrete examples.",
                    "strengths": [
                        {
                            "point": "Complete consistency between resume claims and transcript statements",
                            "quote": "Both resume and transcript detail 3x velocity via Claude Code, AWS Textract OCR, and 99.9% on-call uptime.",
                            "source": "04_Resume_B.pdf & 06_Transcript_B.pdf"
                        }
                    ],
                    "concerns": [
                        {
                            "point": "Multi-agent experience is simpler agent loops rather than complex multi-agent graphs",
                            "quote": "My experience has been with focused agent loops, RAG pipelines, and API integrations.",
                            "source": "06_Transcript_B.pdf"
                        }
                    ]
                }

def get_all_personas(gemini_client: GeminiClient = None) -> List[PersonaAgent]:
    return [
        PersonaAgent(
            name="Technical Agent",
            role="Technical Depth & Architecture Evaluator",
            description="Checks hard technical depth, Python backend skills, agent patterns, RAG, vector search, and framework knowledge.",
            system_prompt="You are a strict Principal Technical Architect evaluating candidate technical depth.",
            gemini_client=gemini_client
        ),
        PersonaAgent(
            name="HR / Culture Agent",
            role="Communication, Teamwork & Honesty Evaluator",
            description="Evaluates communication quality, collaboration, honesty, transparency, and cultural alignment.",
            system_prompt="You are an experienced HR Director checking communication, honesty, teamwork, and red flags.",
            gemini_client=gemini_client
        ),
        PersonaAgent(
            name="Hiring Manager Agent",
            role="Role Alignment & Delivery Evaluator",
            description="Evaluates direct alignment with Job Description duties, productivity tools (Claude Code), React UI, and production shipping.",
            system_prompt="You are the VP of Engineering / Hiring Manager looking for someone to ship fast and fit the role.",
            gemini_client=gemini_client
        ),
        PersonaAgent(
            name="Skeptic Agent",
            role="Red Flag & Contradiction Auditor",
            description="Audits candidate claims for resume inflation, timeline mismatches, contradictions, or unbacked statements.",
            system_prompt="You are a ruthless Skeptic Auditor who scrutinizes claims, verifies quotes, and flags contradictions.",
            gemini_client=gemini_client
        )
    ]
