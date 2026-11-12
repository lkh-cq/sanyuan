# ECR · Evidence-Chain Recommendation（证据链推荐）

> **一句话**：在**固定注入预算**下，决定「注入哪些证据、每条压到几级、按什么顺序」，并把**舍弃项与缺口留痕**。
> **它不产生知识、不判定结论**——只调度。结论成立与否仍归证据阶梯（`memory/070`）。

版本：**v1.0**（2026-11-12）| 前身：v0.1 设计稿（2026-10-29，未落盘）| 分支：`feat/evidence-chain-recommendation`

---

## 1 它在体系里的位置（注入面）

| 模块 | 平面 | 输入 → 输出 | 明确不管 |
|---|---|---|---|
| `sanyuan-normalization-port` | 数据面 | 原始素材 → 归一化证据单元 | 不决定注入哪些 |
| 藏归（三元/三题/三元语法） | 结构面 | 证据 ↔ 三元耦合结构 | 不决定预算分配 |
| `sanyuan-router` | 控制面 | 请求 → PASS/FAIL、路由 | 不决定内容取舍 |
| `conscious` / `consciousness-bus` | 认知面 | 注意力 ρ 收束方向 | 不管注入体积 |
| **ECR（本扩展）** | **注入面** | 命题 x + 候选池 → 注入计划 + 缺口 + 恢复引用 | **不产生知识、不判结论、不碰链路** |

---

## 2 快速开始

```bash
# 实跑（本仓自带工作实例：17 个真实文件、125,477 B）
python3 scripts/ecr_plan.py \
  --input refs/worked_example_input.json \
  --root  /mnt/d/hermes_memory/reference/提示词提炼_DEMO_v1_20261111 \
  --out   refs/worked_example_plan.json

# 自检（3 用例，必须 3/3）
python3 scripts/ecr_selftest.py
```

无第三方依赖（纯 stdlib），无随机数，输出确定性（同路径重跑**字节一致**，已实测）。

---

## 3 实跑结果摘要（v1.0 首次运行，非示例数字）

| 项 | 值 |
|---|---|
| 候选池 | 17 个文件 / **125,477 B**（L0 全量） |
| 预算 | B=90,000 ｜ B_L=27,995 ｜ B_U=27,000 ｜ B_C=35,005 |
| 实际注入 | **35,195 B**（39.1%），链长 **10** 步 |
| 覆盖分层 | 共识 x1/x2/x3 ｜ **独占 x4/x5** ｜ **缺口 x6** |
| 出处核验 | **17/17** 文件 bytes 与磁盘逐一吻合，sha256 运行时重算 |
| 拒载 / 降级 | 0 / 0（本实例全部证据 provenance 完整） |
| selftest | **3/3** |

**断点不在"选哪些"上**：x6（"现在能否落笔改 skill"）根本没有证据——c=0。这正是 ECR 存在的理由：**缺口必须外显，不允许静默消失**。

---

## 4 文件结构

```text
extensions/evidence-chain-recommendation/
├── README.md                          本文件
├── CHANGELOG.md                       v0.1 → v1.0
├── spec/
│   ├── 01_terms.md                    符号定义 + 六门 + 三档降维 + A–J 不变量
│   ├── 02_operators.md                O1–O7 形式化（含失效形态）
│   ├── 03_boundaries.md               12 条红线（含机器可校验项）
│   ├── 04_bus_interface.md            与五模块接口 + CLI 契约
│   └── 05_acceptance.md               验收标准与回归规则
├── schema/
│   ├── task_breakdown.schema.json     输入：命题 + 子问题分解
│   ├── evidence_unit.schema.json      输入：证据单元（含 gate/claim_type/power）
│   └── injection_plan.schema.json     输出：注入计划（含 gaps/dropped 留痕位）
├── scripts/
│   ├── ecr_plan.py                    最小实现
│   └── ecr_selftest.py                3 用例
└── refs/
    ├── worked_example.md              本会话 17 件产物的实跑记录
    ├── worked_example_input.json      实测 bytes + 运行时 sha256
    ├── worked_example_plan.json       实跑输出（注入计划）
    └── session_20261111_assets.md     产出 → ECR 角色映射
```

---

## 5 与 v0.1 的差别（一句话版）

v0.1 是**算法**（五算子 + 三份 JSON）；v1.0 是**制度**——多了三层：**门位标注（O6）**、**十不变量闸门（O7）**、**边际价值必须扣检验力（O3 修正）**，另加一条对 ECR 自身的元约束：**任何"某类证据被高估"的结论必须先扣度数边际**。
详见 `CHANGELOG.md` 与 `spec/02_operators.md`。
