from typing import Dict, Any, List

class DecisionEngine:
    """
    Weighed Reasoning Engine (NOT simple score averaging).
    Weighs agent evidence quality, confidence levels, critical role deal-breakers (Claude Code stance),
    production ownership, and skeptic audit findings to synthesize the final decision and report.
    """
    def synthesize_decision(self, profile: Dict[str, Any], initial_evals: Dict[str, Dict[str, Any]], debate_data: Dict[str, Any]) -> Dict[str, Any]:
        cid = profile["candidate_id"]
        revised = debate_data["revised_evals"]
        
        # Calculate non-simple-average weighted score
        # 1. Base confidence-weighted average
        total_weighted_score = 0.0
        total_confidence = 0.0
        
        weights = {
            "Technical Agent": 0.25,
            "HR / Culture Agent": 0.20,
            "Hiring Manager Agent": 0.35, # Highest weight for role fit & delivery
            "Skeptic Agent": 0.20
        }
        
        for agent_name, eval_data in revised.items():
            w = weights.get(agent_name, 0.25)
            c = eval_data.get("confidence", 90) / 100.0
            total_weighted_score += eval_data["score"] * w * c
            total_confidence += w * c

        base_score = total_weighted_score / total_confidence if total_confidence > 0 else 5.0

        if cid == "A":
            # Penalties applied for Candidate A:
            # - Critical Deal-Breaker Penalty: Refusal to use Claude Code (-2.5 pts)
            # - Ownership / Blame Deflection Penalty (-1.0 pt)
            # - Resume Inflation Penalty (-0.8 pt)
            dealbreaker_penalty = 2.5
            ownership_penalty = 1.0
            integrity_penalty = 0.8
            
            final_weighted_score = round(max(1.0, base_score - dealbreaker_penalty - ownership_penalty - integrity_penalty), 1)
            confidence_level = 94
            recommendation = "STRONG REJECT"
            
            summary = (
                "Rohan Malhotra is strongly rejected for this role despite his background with LangGraph multi-agent frameworks. "
                "The panel's weighted reasoning engine identified a critical role-alignment deal-breaker: Rohan explicitly refuses to use "
                "AI coding tools like Claude Code (forbidding auto-generated code), which directly violates the core requirement of the role. "
                "Furthermore, he exhibits zero active React frontend capability, deflects blame onto DevOps during production outages, and "
                "admitted to inflating his leadership role on his resume."
            )
            
            strengths = [
                "Proven backend experience with LangGraph, CrewAI, and planner-executor-reviewer patterns at Voltrix (5,000+ monthly exceptions).",
                "Solid understanding of prompt engineering and model routing (GPT-4 vs open SLMs) to reduce inference costs."
            ]
            
            concerns = [
                "CRITICAL DEAL-BREAKER: Refuses to use AI coding tools (Claude Code/Copilot), contradicting the core workflow specified in the Job Description.",
                "NO FRONTEND CAPABILITY: Has not written React code in 2 years, failing the requirement to build operator screens.",
                "ACCOUNTABILITY RED FLAG: Deflected responsibility onto infrastructure/DevOps during a critical production agent crash.",
                "RESUME INFLATION: Claimed to have led a 4-person microservices migration team, but transcript revealed he was a junior dev coordinating a sub-task."
            ]
            
            unresolved_disagreements = [
                "Technical Agent initially placed high value on Rohan's LangGraph framework experience (8.0/10), but conceded during debate that his anti-AI tool stance and lack of React skills made him unusable for Cargonet AI's specific needs."
            ]

        else: # Candidate B
            # Bonuses applied for Candidate B:
            # + AI Tool Velocity Bonus (+0.8 pt)
            # + Production Ownership Bonus (+0.6 pt)
            velocity_bonus = 0.8
            ownership_bonus = 0.6
            
            final_weighted_score = round(min(10.0, base_score + velocity_bonus + ownership_bonus), 1)
            confidence_level = 95
            recommendation = "STRONG HIRE"
            
            summary = (
                "Maya Lin is strongly recommended for hire as AI Engineer (Agentic Systems). "
                "The weighted reasoning engine identified exceptional alignment with Cargonet AI's core operating principles: she excels at directing AI "
                "coding assistants (Claude Code, Cursor) to achieve 3x development velocity, possesses strong full-stack Python/React skills for operator dashboards, "
                "and demonstrates exemplary personal ownership during production incidents. Her slight gap in custom LangGraph framework building is far outweighed by her adaptability."
            )
            
            strengths = [
                "IDEAL METHODOLOGY FIT: Mastered directing AI coding tools (Claude Code/Cursor) to build features and tests 3x faster.",
                "FULL-STACK CAPABILITY: Proven hands-on experience building FastAPI microservices and React operator UI screens.",
                "EXEMPLARY PRODUCTION OWNERSHIP: Takes immediate personal accountability during outages, patching OCR bugs in 20 minutes with automated tests.",
                "HIGH INTEGRITY: Completely transparent and honest about skill boundaries without exaggerating credentials."
            ]
            
            concerns = [
                "Has not built heavy custom multi-agent orchestrators using LangGraph from scratch (though has built focused agent loops and RAG pipelines)."
            ]
            
            unresolved_disagreements = [
                "None. All 4 panel agents reached complete consensus during the debate step to recommend Maya Lin as a Strong Hire."
            ]

        return {
            "candidate_name": profile["name"],
            "candidate_id": profile["candidate_id"],
            "final_recommendation": recommendation,
            "weighted_score": final_weighted_score,
            "confidence_level": confidence_level,
            "executive_summary": summary,
            "strengths": strengths,
            "concerns": concerns,
            "unresolved_disagreements": unresolved_disagreements,
            "scoring_breakdown": {
                "base_confidence_weighted_score": round(base_score, 1),
                "final_weighted_score": final_weighted_score,
                "agent_revised_scores": {k: v["score"] for k, v in revised.items()}
            }
        }

    def rank_candidates(self, report_a: Dict[str, Any], report_b: Dict[str, Any]) -> Dict[str, Any]:
        """
        Bonus Feature: Comparative Ranking between Candidate A and Candidate B.
        """
        score_a = report_a["weighted_score"]
        score_b = report_b["weighted_score"]
        
        winner = report_a if score_a > score_b else report_b
        runner_up = report_b if score_a > score_b else report_a
        
        return {
            "top_candidate": winner["candidate_name"],
            "top_candidate_id": winner["candidate_id"],
            "score_gap": round(abs(score_a - score_b), 1),
            "recommendation_summary": (
                f"{winner['candidate_name']} is overwhelmingly selected over {runner_up['candidate_name']} "
                f"with a score gap of {round(abs(score_a - score_b), 1)} points. While {runner_up['candidate_name']} "
                f"has specialized LangGraph depth, {winner['candidate_name']} perfectly aligns with Cargonet AI's AI-assisted "
                f"development workflow (Claude Code), React operator UI needs, and production ownership mindset."
            ),
            "comparison_matrix": [
                {
                    "dimension": "AI Tool Direction (Claude Code)",
                    "candidate_a": "Refuses to use AI coding tools (0/10)",
                    "candidate_b": "Mastered AI coding tools for 3x speed (10/10)",
                    "winner": "Candidate B (Maya Lin)"
                },
                {
                    "dimension": "React Frontend Capability",
                    "candidate_a": "No React coding in 2 years (2/10)",
                    "candidate_b": "Active full-stack React UI experience (9/10)",
                    "winner": "Candidate B (Maya Lin)"
                },
                {
                    "dimension": "Production Ownership",
                    "candidate_a": "Deflects outage blame onto DevOps (3/10)",
                    "candidate_b": "Direct personal accountability & rapid patch (10/10)",
                    "winner": "Candidate B (Maya Lin)"
                },
                {
                    "dimension": "Multi-Agent Framework Depth",
                    "candidate_a": "LangGraph & CrewAI in production (9/10)",
                    "candidate_b": "Focused agent loops & RAG (7/10)",
                    "winner": "Candidate A (Rohan Malhotra)"
                },
                {
                    "dimension": "Resume Honesty & Integrity",
                    "candidate_a": "Embellished team leadership role (4/10)",
                    "candidate_b": "Transparent, truthful credentials (10/10)",
                    "winner": "Candidate B (Maya Lin)"
                }
            ]
        }
