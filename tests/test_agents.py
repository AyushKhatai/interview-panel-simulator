import unittest
from src.agents import get_all_personas, PersonaAgent
from src.profile_builder import CandidateProfileBuilder

class TestAgents(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profile_builder = CandidateProfileBuilder(
            "data/02_Job_Description.pdf",
            "data/03_Resume_A.pdf",
            "data/05_Transcript_A.pdf"
        )
        cls.profile_a = cls.profile_builder.build_profile("A")

    def test_four_distinct_personas_exist(self):
        personas = get_all_personas()
        self.assertEqual(len(personas), 4)
        names = [p.name for p in personas]
        self.assertIn("Technical Agent", names)
        self.assertIn("HR / Culture Agent", names)
        self.assertIn("Hiring Manager Agent", names)
        self.assertIn("Skeptic Agent", names)

    def test_independent_evaluations_have_quote_citations(self):
        personas = get_all_personas()
        for agent in personas:
            res = agent.evaluate_independent(self.profile_a)
            self.assertIn("score", res)
            self.assertIn("verdict", res)
            self.assertIn("summary", res)
            
            # Check that strengths or concerns cite evidence quotes
            has_quote = False
            for s in res.get("strengths", []) + res.get("concerns", []):
                if "quote" in s and s["quote"]:
                    has_quote = True
                    break
            self.assertTrue(has_quote, f"{agent.name} did not cite evidence quotes in Phase 1.")

if __name__ == "__main__":
    unittest.main()
