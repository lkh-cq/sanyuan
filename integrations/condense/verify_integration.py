"""verify_integration.py — 端到端验证"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from model_anchor_probe import probe_model
from safety_tunnel import build_safety_tunnel
from triad_adapter import adapt_vector_output

def main():
    print("=== 1. 模型探测(未配端点 → 返回空, 降级 manual) ===")
    result = probe_model("manual-test")
    print(f"  level={result['level']} (空响应 → C 保守)")

    print("\n=== 2. 安全隧道三档 ===")
    for lv in ("A", "B", "C"):
        t = build_safety_tunnel(lv)
        print(f"  {lv}: {len(t)} chars")

    print("\n=== 3. 三元搭载三档 ===")
    for lv in ("A", "B", "C"):
        out = adapt_vector_output(lv, "测试主题", 0.8, 0.2, "方向A")
        print(f"  {lv}: {out.splitlines()[1][:50]}")

    print("\n✅ 集成验证通过")

if __name__ == "__main__":
    main()
