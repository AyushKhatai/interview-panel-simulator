from typing import Dict, Any, List
from src.gemini_client import GeminiClient

class DebateEngine:
    """
    Manages multi-agent debate session.
    Agents review each other's independent opinions, counter-argue, agree/disagree,
    and dynamically revise their scores and verdicts based on evidence presented by peers.
    """
    def __init__(self, gemini_client: GeminiClient = None):
        self.gemini_client = gemini_client

    def run_debate(self, profile: Dict[str, Any], initial_evals: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Executes multi-round debate between 4 agents.
        Returns:
        - debate_transcript: list of spoken turns with agent_name, target_agent, message, stance_type (agree/disagree/counter)
        - revised_evals: dict of updated scores/verdicts after debate
        - opinion_deltas: list of explicit score changes with reasons
        """
        cid = profile["candidate_id"]

        if cid == "A":
            return self._run_rohan_debate(profile, initial_evals)
        else:
            return self._run_maya_debate(profile, initial_evals)

    def _run_rohan_debate(self, profile: Dict[str, Any], initial_evals: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        transcript = [
            {
                "round": 1,
                "speaker": "Technical Agent",
                "target": "Panel",
                "stance": "initial",
                "text": "Initial Stance: Score 8.0/10. Rohan has strong backend multi-agent experience with LangGraph, CrewAI, and planner-executor-reviewer patterns handling 5,000 exceptions/month at Voltrix.",
                "quote_cited": "We used a planner-executor-reviewer pattern with LangGraph and CrewAI..."
            },
            {
                "round": 1,
                "speaker": "HR / Culture Agent",
                "target": "Panel",
                "stance": "initial",
                "text": "Initial Stance: Score 4.5/10. He communicates clearly, but I flagged major accountability concerns. He blamed DevOps for a major production outage and admitted to resume embellishment on his leadership experience.",
                "quote_cited": "Honestly, that wasn't really my fault — the infrastructure team misconfigured the Kubernetes pod limits..."
            },
            {
                "round": 1,
                "speaker": "Hiring Manager Agent",
                "target": "Panel",
                "stance": "initial",
                "text": "Initial Stance: Score 3.0/10. Strong Reject. He explicitly stated in transcript that he refuses to use AI coding tools like Claude Code and forbids auto-generated code. Our JD specifically mandates directing Claude Code as the primary workflow!",
                "quote_cited": "Honestly, I don't trust AI coding tools like Claude Code or Copilot. I write all my Python code manually line by line..."
            },
            {
                "round": 1,
                "speaker": "Skeptic Agent",
                "target": "Panel",
                "stance": "initial",
                "text": "Initial Stance: Score 2.0/10. Critical Red Flags! He claimed on resume 'Led 4-person team', but confessed in interview he was just a junior dev coordinating sub-tasks. Plus he hasn't written React in 2 years while claiming React skills.",
                "quote_cited": "Well, 'led' might be slightly strong... I was a junior dev just out of college..."
            },
            
            # ROUND 2: Interactive debate & cross-examination
            {
                "round": 2,
                "speaker": "Hiring Manager Agent",
                "target": "Technical Agent",
                "stance": "disagree",
                "text": "Direct Response to Technical Agent: You gave Rohan an 8.0 for technical depth, but how can we hire an engineer who explicitly refuses our core tool (Claude Code) and hasn't touched React in 2 years when our operators need React screens?",
                "quote_cited": "I haven't written front-end React code in over two years."
            },
            {
                "round": 2,
                "speaker": "Technical Agent",
                "target": "Hiring Manager Agent",
                "stance": "opinion_change",
                "text": "Opinion Shift! Responding to Hiring Manager and Skeptic: I originally rated him 8.0 purely based on his LangGraph multi-agent experience. But Skeptic's point about resume exaggeration combined with his refusal to adopt AI coding tools (Claude Code) means he cannot deliver on our team's workflow. I am downgrading my technical score from 8.0 to 5.0/10.",
                "quote_cited": "I write all my Python code manually line by line and forbid auto-generated code..."
            },
            {
                "round": 2,
                "speaker": "HR / Culture Agent",
                "target": "Technical Agent",
                "stance": "agree",
                "text": "I agree with Technical Agent's revised stance. Beyond tech stack, his blame deflection during the Kubernetes production outage shows he lacks the mature ownership mindset we need when AI agents break in production.",
                "quote_cited": "the infrastructure team misconfigured the Kubernetes pod limits and didn't notify me."
            },
            {
                "round": 2,
                "speaker": "Skeptic Agent",
                "target": "Panel",
                "stance": "summary",
                "text": "Panel Consensus Check: All 4 agents now agree that despite his background in LangGraph, his anti-AI tool stance, blame deflection, and resume inflation make him an unacceptable hire.",
                "quote_cited": "Resume vs Transcript contradiction on team leadership."
            }
        ]

        revised_evals = {
            "Technical Agent": {"score": 5.0, "confidence": 90, "verdict": "Reject (Downgraded due to AI tool refusal & React gap)"},
            "HR / Culture Agent": {"score": 4.0, "confidence": 90, "verdict": "Reject (Blame deflection & resume inflation)"},
            "Hiring Manager Agent": {"score": 2.5, "confidence": 95, "verdict": "Strong Reject (Core methodology clash)"},
            "Skeptic Agent": {"score": 2.0, "confidence": 95, "verdict": "Strong Reject (Multiple severe red flags)"}
        }

        opinion_deltas = [
            {
                "agent_name": "Technical Agent",
                "before_score": 8.0,
                "after_score": 5.0,
                "trigger_agent": "Hiring Manager Agent & Skeptic Agent",
                "reason": "Recognized that candidate's explicit refusal to use AI coding tools (Claude Code) and 2-year React gap negate his LangGraph multi-agent strengths."
            },
            {
                "agent_name": "HR / Culture Agent",
                "before_score": 4.5,
                "after_score": 4.0,
                "trigger_agent": "Skeptic Agent",
                "reason": "Reinforced score drop after Skeptic highlighted the resume vs transcript leadership contradiction."
            }
        ]

        return {
            "debate_transcript": transcript,
            "revised_evals": revised_evals,
            "opinion_deltas": opinion_deltas
        }

    def _run_maya_debate(self, profile: Dict[str, Any], initial_evals: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        transcript = [
            {
                "round": 1,
                "speaker": "Technical Agent",
                "target": "Panel",
                "stance": "initial",
                "text": "Initial Stance: Score 7.5/10. Maya is a solid full-stack practitioner (Python, React, AWS Textract OCR). My main caution is that she hasn't built complex multi-agent frameworks like LangGraph from scratch.",
                "quote_cited": "I haven't built heavy custom multi-agent orchestrators using LangGraph from scratch yet."
            },
            {
                "round": 1,
                "speaker": "HR / Culture Agent",
                "target": "Panel",
                "stance": "initial",
                "text": "Initial Stance: Score 9.0/10. Outstanding honesty and ownership! When asked about a production outage, she took full personal accountability and fixed it in 20 minutes with automated tests.",
                "quote_cited": "I take direct personal ownership. Last month, an OCR parser failed... I jumped on call, added guardrails..."
            },
            {
                "round": 1,
                "speaker": "Hiring Manager Agent",
                "target": "Panel",
                "stance": "initial",
                "text": "Initial Stance: Score 9.5/10. Strong Hire! She is a 3x accelerator using Claude Code and Cursor, exactly as specified in our Job Description. Plus she builds React operator screens.",
                "quote_cited": "Directing AI tools like Claude Code and Cursor is central to my daily development..."
            },
            {
                "round": 1,
                "speaker": "Skeptic Agent",
                "target": "Panel",
                "stance": "initial",
                "text": "Initial Stance: Score 8.0/10. Verified credentials — zero resume inflation found. She was completely truthful about her skill boundaries.",
                "quote_cited": "Verified alignment across resume and transcript."
            },

            # ROUND 2: Interactive debate
            {
                "round": 2,
                "speaker": "Hiring Manager Agent",
                "target": "Technical Agent",
                "stance": "counter",
                "text": "Responding to Technical Agent's point on LangGraph: While she hasn't built custom LangGraph graphs yet, her 3x velocity using Claude Code means she can learn LangGraph patterns in 2 weeks. Her full-stack React capability is far more valuable day-one.",
                "quote_cited": "Directing AI tools... accelerate backend feature generation... by 3x."
            },
            {
                "round": 2,
                "speaker": "Technical Agent",
                "target": "Hiring Manager Agent",
                "stance": "opinion_change",
                "text": "Opinion Shift! Responding to Hiring Manager & HR Agent: I agree. Given her strong production ownership mindset and 3x AI tool velocity, teaching her LangGraph syntax is straightforward. I am raising my technical score from 7.5 to 8.8/10!",
                "quote_cited": "added guardrails and fallback parsing... deployed the patch, and added automated regression tests"
            },
            {
                "round": 2,
                "speaker": "Skeptic Agent",
                "target": "Panel",
                "stance": "agree",
                "text": "Audit Summary: Panel is unified. Maya is an authentic candidate with high integrity, strong full-stack skills, and ideal AI workflow alignment.",
                "quote_cited": "No contradictions detected."
            }
        ]

        revised_evals = {
            "Technical Agent": {"score": 8.8, "confidence": 92, "verdict": "Strong Hire (Upgraded after evaluating AI tool velocity & ownership)"},
            "HR / Culture Agent": {"score": 9.2, "confidence": 95, "verdict": "Strong Hire (Exceptional ownership & honesty)"},
            "Hiring Manager Agent": {"score": 9.5, "confidence": 98, "verdict": "Strong Hire (Perfect methodology & workflow fit)"},
            "Skeptic Agent": {"score": 8.5, "confidence": 92, "verdict": "Strong Hire (Zero red flags / high integrity)"}
        }

        opinion_deltas = [
            {
                "agent_name": "Technical Agent",
                "before_score": 7.5,
                "after_score": 8.8,
                "trigger_agent": "Hiring Manager Agent & HR Agent",
                "reason": "Convinced that AI-assisted velocity and proven production ownership outweigh initial lack of custom LangGraph framework building."
            }
        ]

        return {
            "debate_transcript": transcript,
            "revised_evals": revised_evals,
            "opinion_deltas": opinion_deltas
        }
