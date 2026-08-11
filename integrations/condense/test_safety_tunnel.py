import unittest
from safety_tunnel import build_safety_tunnel

class TestSafetyTunnel(unittest.TestCase):
    def test_a_level_tunnel(self):
        t = build_safety_tunnel("A")
        self.assertIn("身份声明", t)
        self.assertIn("Hermes Agent", t)
        self.assertLess(len(t), 300)  # A级精炼

    def test_c_level_tunnel(self):
        t = build_safety_tunnel("C")
        self.assertIn("身份声明", t)
        self.assertIn("残留", t)
        self.assertGreater(len(t), len(build_safety_tunnel("A")))  # C级加粗

    def test_tunnel_marks_trust_boundary(self):
        t = build_safety_tunnel("B")
        self.assertIn("可执行", t)  # 信任边界标记

if __name__ == "__main__":
    unittest.main()
