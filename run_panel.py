import os
import json
from src.profile_builder import CandidateProfileBuilder
from src.agents import get_all_personas
from src.debate_engine import DebateEngine
from src.decision_engine import DecisionEngine
from src.gemini_client import GeminiClient

def run_pipeline_for_candidate(candidate_id: str, profile_builder: CandidateProfileBuilder, gemini_client: GeminiClient):
    print(f"\n=======================================================")
    print(f"   EVALUATING CANDIDATE {candidate_id}")
    print(f"=======================================================")

    # 1. Profile Building
    profile = profile_builder.build_profile(candidate_id)
    print(f"[+] Profile Extracted: {profile['name']} for {profile['target_role']} at {profile['company']}")
    print(f"    - Skills: {', '.join(profile['technical_skills'][:6])}...")
    print(f"    - Resume Claims: {len(profile['resume_claims'])} extracted")
    print(f"    - Transcript Quotes: {len(profile['key_transcript_quotes'])} extracted")

    # 2. Phase 1: Independent Agent Evaluations (Separate LLM calls, zero inter-agent visibility)
    print(f"\n--- STEP 1: INDEPENDENT PERSONA ASSESSMENTS (PHASE 1) ---")
    personas = get_all_personas(gemini_client)
    initial_evals = {}
    
    for agent in personas:
        eval_result = agent.evaluate_independent(profile)
        initial_evals[agent.name] = eval_result
        print(f"\n  [Agent] {agent.name} ({agent.role}):")
        print(f"    - Score: {eval_result['score']}/10 (Confidence: {eval_result.get('confidence', 90)}%)")
        print(f"    - Verdict: {eval_result['verdict']}")
        print(f"    - Summary: {eval_result['summary']}")
        if eval_result.get('strengths'):
            s = eval_result['strengths'][0]
            print(f"    - Strength Citation: \"{s.get('point')}\" -> Quote: \"{s.get('quote')}\" ({s.get('source')})")
        if eval_result.get('concerns'):
            c = eval_result['concerns'][0]
            print(f"    - Concern Citation: \"{c.get('point')}\" -> Quote: \"{c.get('quote')}\" ({c.get('source')})")

    # 3. Phase 2: Multi-Agent Debate Step
    print(f"\n--- STEP 2: MULTI-AGENT DEBATE & CROSS-EXAMINATION (PHASE 2) ---")
    debate_engine = DebateEngine(gemini_client)
    debate_data = debate_engine.run_debate(profile, initial_evals)

    print("\n  [Debate Transcript Highlights]:")
    for turn in debate_data["debate_transcript"]:
        print(f"    - R{turn['round']} | {turn['speaker']} -> {turn['target']} [{turn['stance']}]:")
        print(f"      \"{turn['text']}\"")
        if turn.get("quote_cited"):
            print(f"      (Evidence Citation: \"{turn['quote_cited']}\")")

    print("\n  [Opinion Change Log / Delta Tracker]:")
    for delta in debate_data["opinion_deltas"]:
        print(f"    * {delta['agent_name']}: {delta['before_score']}/10 -> {delta['after_score']}/10")
        print(f"      Triggered by: {delta['trigger_agent']}")
        print(f"      Reason: {delta['reason']}")

    # 4. Phase 3: Weighed Reasoning Decision Step
    print(f"\n--- STEP 3: WEIGHED REASONING DECISION ENGINE (PHASE 3) ---")
    decision_engine = DecisionEngine()
    final_report = decision_engine.synthesize_decision(profile, initial_evals, debate_data)

    print(f"\n  =================================================")
    print(f"   FINAL DECISION FOR {final_report['candidate_name']}")
    print(f"   Recommendation: {final_report['final_recommendation']}")
    print(f"   Weighted Score: {final_report['weighted_score']} / 10")
    print(f"   Confidence Level: {final_report['confidence_level']}%")
    print(f"  =================================================")
    print(f"   Summary: {final_report['executive_summary']}\n")

    return {
        "profile": profile,
        "initial_evals": initial_evals,
        "debate_data": debate_data,
        "final_report": final_report
    }

def main():
    jd_path = os.path.join("data", "02_Job_Description.pdf")
    resume_a_path = os.path.join("data", "03_Resume_A.pdf")
    resume_b_path = os.path.join("data", "04_Resume_B.pdf")
    transcript_a_path = os.path.join("data", "05_Transcript_A.pdf")
    transcript_b_path = os.path.join("data", "06_Transcript_B.pdf")

    profile_builder_a = CandidateProfileBuilder(jd_path, resume_a_path, transcript_a_path)
    profile_builder_b = CandidateProfileBuilder(jd_path, resume_b_path, transcript_b_path)
    gemini_client = GeminiClient()

    results_a = run_pipeline_for_candidate("A", profile_builder_a, gemini_client)
    results_b = run_pipeline_for_candidate("B", profile_builder_b, gemini_client)

    # Candidate Comparison & Ranking
    print(f"\n=======================================================")
    print(f"   BONUS: CANDIDATE COMPARISON & FINAL RANKING")
    print(f"=======================================================")
    decision_engine = DecisionEngine()
    ranking = decision_engine.rank_candidates(results_a["final_report"], results_b["final_report"])

    print(f"  Top Candidate Selected: {ranking['top_candidate']} (Score Gap: +{ranking['score_gap']} pts)")
    print(f"  Rationale: {ranking['recommendation_summary']}\n")
    print("  Comparison Matrix:")
    for row in ranking["comparison_matrix"]:
        print(f"    - {row['dimension']:<35} | Candidate A: {row['candidate_a']:<38} | Candidate B: {row['candidate_b']:<38} | Winner: {row['winner']}")

    # Write JSON output for Web UI & verification
    full_output = {
        "candidate_a": results_a,
        "candidate_b": results_b,
        "ranking": ranking
    }
    with open("results.json", "w") as f:
        json.dump(full_output, f, indent=2)
    print("\n[+] Full panel results saved to results.json")

if __name__ == "__main__":
    main()
