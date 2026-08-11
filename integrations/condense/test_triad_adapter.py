import unittest
from triad_adapter import adapt_vector_output

class TestTriadAdapter(unittest.TestCase):
    def test_a_level_full_rho_theta(self):
        out = adapt_vector_output("A", "PNPLA8 铁死亡", rho=0.85, theta=0.15)
        self.assertIn("ρ", out)
        self.assertIn("θ", out)

    def test_c_level_plain_facts(self):
        out = adapt_vector_output("C", "PNPLA8 铁死亡", rho=0.85, theta=0.15)
        self.assertNotIn("ρ", out)  # C级不用 ρ/θ 抽象
        self.assertIn("方向", out)

    def test_b_level_hybrid(self):
        out = adapt_vector_output("B", "PNPLA8 铁死亡", rho=0.85, theta=0.15)
        self.assertIn("ρ", out)
        self.assertIn("方向", out)  # B级混合

if __name__ == "__main__":
    unittest.main()
