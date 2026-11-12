# 本会话产出 → ECR 角色映射（2026-11-11）

> 来源目录：`/mnt/d/hermes_memory/reference/提示词提炼_DEMO_v1_20261111/`
> 用途：把该会话的 17 个产物登记为 ECR 候选池，并标明每个文件在 ECR 里扮演什么角色。
> 字节数全部 `wc -c` 实测；`worked_example_plan.json` 里存有运行时重算的 sha256。

## A. 候选池清单（17 件 / 125,477 B）

| id | 文件 | 字节 | gate | 角色 | 覆盖子问题 |
|---|---|---:|---|---|---|
| a01 | `_DEMO.md` | 27,995 | 3 | 51 条提示清单 + 五模式（已降级为表层留证）+ skill 判定 | x1, **x5** |
| a02 | `instance_wf010_20261111.json` | 13,010 | 3 | 机读实例（51 条 prompts，正文不双写） | x1 |
| a03 | `analysis/_BEHAVIOUR_v1.md` | 10,121 | 3 | 行为编码报告（动作分布/滞后序列） | x1 |
| a04 | `analysis/_PROCESS_v1.md` | 13,480 | 3 | 六门状态机 + 三条过程律 | x1, x3 |
| a05 | `analysis/_TESTS_v1.md` | 7,405 | 2 | T1–T4 检验（含零假设说明） | x1, x3 |
| a06 | `analysis/_RESIDUAL_v1.md` | 6,919 | 2 | 基线残差（quasi-independence + 配置模型） | x1 (partial) |
| a07 | `analysis/_CAPABILITY_CROSSCHECK.md` | 6,906 | 3 | 能力锚点 6 轮 vs 本轮短板对照 | **x4** |
| a08 | `analysis/_SHAME_DISTILL_v1.md` | 9,548 | 3 | 32 条事故 → 8 不变量 + I/J 元缺陷 + 10×5 闸门 | x2, x3 |
| a09 | `analysis/output_shame_wf010_20261111.txt` | 5,605 | 2 | 事故统计原始输出（md5 `f934bf8c…`） | x2, x3 |
| a10 | `analysis/coding_shame_pillar_20261111.csv` | 2,157 | 2 | 32 条事故编码（gate/inv/recur） | x2 |
| a11 | `analysis/coding_self_errors_20261111.csv` | 541 | 2 | 本轮自犯 8 错 → 命中编号 | x3 |
| a12 | `analysis/output_residual_wf010_20261111.txt` | 4,156 | 2 | 残差原始输出（md5 `f1619a60…`） | x1 |
| a13 | `analysis/output_tests_wf010_20261111.txt` | 2,637 | 2 | 检验原始输出 | x1 |
| a14 | `analysis/output_gates_wf010_20261111.txt` | 4,586 | 2 | 门位原始输出（md5 `959b1de7…`） | x1 |
| a15 | `analysis/coding_wf010_20261111_gates.csv` | 2,908 | 2 | 51 条门位编码 | x1 |
| a16 | `analysis/output_wf010_20261111.txt` | 4,702 | 2 | 行为统计原始输出（md5 `826c592d…`） | x1 |
| a17 | `analysis/coding_wf010_20261111.csv` | 2,801 | 2 | 51 条行为编码 | x1 |

## B. 本会话被 ECR 反身引用的关键统计量

| 量 | 值 | 出处 |
|---|---|---|
| 提示条数 | 51（A12/B6/C9/D24；verbatim 18 / false 33） | `_DEMO.md` |
| 门位序列长度 | 49 条入环 + 2 条表态 → 48 次 lag-1 转移 | `_PROCESS_v1.md` §2.3 |
| 自持 vs 保度基线 | 22 vs 8.75，**p=0.0001**（配置模型 10000 次） | `_RESIDUAL_v1.md` §3 |
| 撤销的结论 | 4 条（回溯放大/回溯方向偏好/1→2 硬证据/最长连跑） | `_RESIDUAL_v1.md` §4 |
| 逐格期望频数 | 36 个非零格全部 **≤3.25** → 逐格 z 近似失效 | `_RESIDUAL_v1.md` §6 |
| 事故门位分布（32 条） | 0:9 / 2:8 / 1:5 / 4:4 / 3:3 / 5:3 | `_SHAME_DISTILL_v1.md` §3 |
| 时间反转 | ≤07-31 方法门 46.7% → ≥08-01 设施门 47.1% | `_SHAME_DISTILL_v1.md` §3.1 |
| 本轮自犯 8 错命中编号 | 6/32 = 18.8%，**阻断规则触发率 0/6** | `_SHAME_DISTILL_v1.md` §5 |
| 能力锚点（当前模型） | 蒸馏 0.72 / 耦合 0.74 / 互驱 0.68（2026-09-16） | `_CAPABILITY_CROSSCHECK.md` §1 |

## C. 为什么这 17 件适合当 ECR 的第一个实例

1. **有真实体积差**：541 B（一张编码表）到 27,995 B（主文档），量级差 52 倍 → 能压出边际价值的排序差异。
2. **有真实缺口**：x6（"现在能否落笔改 skill"）在整个目录里**没有任何证据** → c=0，缺口外显不是构造出来的。
3. **有真实 locked 项**：x5 需要逐字引用主文档的行号级内容 → 强制 L0，占掉 27,995 B（B_L 全额），演示"逐字核对的代价"。
4. **有真实门位**：编码表在 gate 2（方法/判据），报告与主文档在 gate 3（现象）→ 门位均衡检查能落地。
5. **出处可核**：17 个文件都在本机，sha256 可随时重算 → provenance 不是声明而是事实。

## D. 不适用之处（必须说明）

- 本实例的 `expected_min_cell` 全为 `null`（该数据无格子/期望频数设计），所以**检验力闸门未被真实触发**，其行为只由 `selftest t3` 覆盖。
- `stance`（support/partial）是我人工标注，**无第二编码者**，无 κ 一致性 → 这是本实例最大的外部依赖。
- 候选池只含"本轮我自己的产出"，没有第三方证据 → 无法演示"跨来源冲突（support vs refute 并存）"的处理；该场景留给 v1.1 用例。
