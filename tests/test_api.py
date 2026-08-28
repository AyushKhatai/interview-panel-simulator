import unittest
from fastapi.testclient import TestClient
from app import app

class TestFastAPIEndpoints(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_root_endpoint(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_list_candidates_endpoint(self):
        response = self.client.get("/api/candidates")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(len(data) >= 2)

    def test_get_candidate_a_endpoint(self):
        response = self.client.get("/api/candidate/A")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("profile", data)
        self.assertIn("initial_evals", data)
        self.assertIn("debate_data", data)
        self.assertIn("final_report", data)

    def test_comparison_endpoint(self):
        response = self.client.get("/api/comparison")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["top_candidate"], "Maya Lin")

if __name__ == "__main__":
    unittest.main()
