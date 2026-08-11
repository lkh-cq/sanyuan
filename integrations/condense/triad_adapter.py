"""triad_adapter.py — 三元自动搭载器

按模型锚点等级选择 ρ/θ 注意力向量的表达密度:
A级: 完整 ρ/θ 格式(精炼, 模型能理解抽象)
B级: ρ/θ + 白话方向(混合)
C级: 纯事实方向描述(不用 ρ/θ 抽象, 用具体语言)
"""


def adapt_vector_output(level: str, topic: str, rho: float, theta: float,
                        direction: str = "") -> str:
    level = level.upper()
    if level == "A":
        return f"主题: {topic}\n  ρ={rho:.2f}: {direction}\n  θ={theta:.2f}: 未采纳方向"
    if level == "C":
        return f"主题: {topic}\n  当前方向: {direction}\n  注意: 存在未决的其他可能"
    # B 级混合
    return f"主题: {topic}\n  ρ={rho:.2f} ({direction})\n  方向(白话): {direction}"


if __name__ == "__main__":
    for lv in ("A", "B", "C"):
        print(f"=== {lv} ===")
        print(adapt_vector_output(lv, "PNPLA8 铁死亡", 0.85, 0.15, "铁死亡促进"))
        print()
