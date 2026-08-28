import unittest
from src.profile_builder import CandidateProfileBuilder
from src.agents import get_all_personas
from src.debate_engine import DebateEngine

class TestDebateEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pb = CandidateProfileBuilder(
            "data/02_Job_Description.pdf",
            "data/03_Resume_A.pdf",
            "data/05_Transcript_A.pdf"
        )
        cls.profile_a = cls.pb.build_profile("A")
        cls.personas = get_all_personas()
        cls.initial_evals = {p.name: p.evaluate_independent(cls.profile_a) for p in cls.personas}
        cls.debate_engine = DebateEngine()

    def test_debate_execution_and_deltas(self):
        debate_data = self.debate_engine.run_debate(self.profile_a, self.initial_evals)
        
        self.assertIn("debate_transcript", debate_data)
        self.assertIn("revised_evals", debate_data)
        self.assertIn("opinion_deltas", debate_data)
        
        # Verify cross-examination turn exists
        turns = debate_data["debate_transcript"]
        self.assertTrue(len(turns) >= 4)
        
        # Verify opinion change tracker logs at least 1 delta
        deltas = debate_data["opinion_deltas"]
        self.assertTrue(len(deltas) > 0)
        self.assertIn("agent_name", deltas[0])
        self.assertIn("before_score", deltas[0])
        self.assertIn("after_score", deltas[0])
        self.assertIn("reason", deltas[0])

if __name__ == "__main__":
    unittest.main()
