import unittest
from src.profile_builder import CandidateProfileBuilder
from src.agents import get_all_personas
from src.debate_engine import DebateEngine
from src.decision_engine import DecisionEngine

class TestDecisionEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pb_a = CandidateProfileBuilder("data/02_Job_Description.pdf", "data/03_Resume_A.pdf", "data/05_Transcript_A.pdf")
        cls.pb_b = CandidateProfileBuilder("data/02_Job_Description.pdf", "data/04_Resume_B.pdf", "data/06_Transcript_B.pdf")
        cls.profile_a = cls.pb_a.build_profile("A")
        cls.profile_b = cls.pb_b.build_profile("B")
        
        cls.personas = get_all_personas()
        cls.evals_a = {p.name: p.evaluate_independent(cls.profile_a) for p in cls.personas}
        cls.evals_b = {p.name: p.evaluate_independent(cls.profile_b) for p in cls.personas}
        
        cls.debate_engine = DebateEngine()
        cls.debate_a = cls.debate_engine.run_debate(cls.profile_a, cls.evals_a)
        cls.debate_b = cls.debate_engine.run_debate(cls.profile_b, cls.evals_b)
        
        cls.decision_engine = DecisionEngine()

    def test_non_averaging_decision_rohan(self):
        report = self.decision_engine.synthesize_decision(self.profile_a, self.evals_a, self.debate_a)
        self.assertEqual(report["final_recommendation"], "STRONG REJECT")
        self.assertIn("weighted_score", report)
        self.assertTrue(report["weighted_score"] < 4.0)

    def test_non_averaging_decision_maya(self):
        report = self.decision_engine.synthesize_decision(self.profile_b, self.evals_b, self.debate_b)
        self.assertEqual(report["final_recommendation"], "STRONG HIRE")
        self.assertTrue(report["weighted_score"] >= 8.5)

    def test_candidate_ranking(self):
        rep_a = self.decision_engine.synthesize_decision(self.profile_a, self.evals_a, self.debate_a)
        rep_b = self.decision_engine.synthesize_decision(self.profile_b, self.evals_b, self.debate_b)
        ranking = self.decision_engine.rank_candidates(rep_a, rep_b)
        
        self.assertEqual(ranking["top_candidate"], "Maya Lin")
        self.assertTrue(len(ranking["comparison_matrix"]) >= 5)

if __name__ == "__main__":
    unittest.main()
