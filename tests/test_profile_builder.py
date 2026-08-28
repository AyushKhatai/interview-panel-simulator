import os
import unittest
from src.profile_builder import CandidateProfileBuilder
from generate_pdfs import generate_all_pdfs

class TestCandidateProfileBuilder(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.makedirs("data", exist_ok=True)
        generate_all_pdfs()
        cls.jd_path = os.path.join("data", "02_Job_Description.pdf")
        cls.resume_a = os.path.join("data", "03_Resume_A.pdf")
        cls.transcript_a = os.path.join("data", "05_Transcript_A.pdf")
        cls.resume_b = os.path.join("data", "04_Resume_B.pdf")
        cls.transcript_b = os.path.join("data", "06_Transcript_B.pdf")

    def test_rohan_profile_extraction(self):
        builder = CandidateProfileBuilder(self.jd_path, self.resume_a, self.transcript_a)
        profile = builder.build_profile("A")
        
        self.assertEqual(profile["candidate_id"], "A")
        self.assertEqual(profile["name"], "Rohan Malhotra")
        self.assertIn("Python", profile["technical_skills"])
        self.assertTrue(len(profile["resume_claims"]) > 0)
        self.assertTrue(len(profile["key_transcript_quotes"]) > 0)

    def test_maya_profile_extraction(self):
        builder = CandidateProfileBuilder(self.jd_path, self.resume_b, self.transcript_b)
        profile = builder.build_profile("B")
        
        self.assertEqual(profile["candidate_id"], "B")
        self.assertEqual(profile["name"], "Maya Lin")
        self.assertIn("React.js", profile["technical_skills"])
        self.assertTrue(len(profile["resume_claims"]) > 0)
        self.assertTrue(len(profile["key_transcript_quotes"]) > 0)

if __name__ == "__main__":
    unittest.main()
