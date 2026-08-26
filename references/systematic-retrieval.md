---
name: systematic-retrieval
module_id: extension-systematic-retrieval
description: "三阶段系统化检索分支：全量拓展检索→审核检索→收束目标检索，含检索-获取-审核-变更关键词循环、七类盲点发现与四类来源检索指南。"
version: 0.1.0
category: experimental-branch
manifest_ref: references/project-manifest.yaml
---

# 系统化检索分支

本模块是实验性可插拔认知分支，不修改 [architecture.md](architecture.md) 的冻结本体。它回答的是意识总线原本不回答的问题：**外部信息怎么取、取得够不够、取错了关键词怎么办**。机器可读协议见 [retrieval-protocol.yaml](retrieval-protocol.yaml)，检索计划结构见 [schema-retrieval-plan.schema.yaml](schema-retrieval-plan.schema.yaml)，操作入口见 [systematic-retrieval SKILL](../extensions/systematic-retrieval/SKILL.md)。

## 1. 定位与边界

```text
B_T (任务边界)
  → 检索分支 (取: 本模块)
  → 三才藏 (存) / 三题归 (读)
  → 归一化与合成
```

- 检索分支位于 [task-boundary.md](task-boundary.md) 编译之后、三才藏之前，只负责"取"与"审计取得是否充分"；取回材料的语义处理仍归藏归层。
- 检索事件复用 [flow-event-catalog.yaml](flow-event-catalog.yaml) 既有类型（flow/filter/merge/conflict/loss/restore），**不新增第四本体实体**。
- 外部数据库、搜索引擎、社区站点、工具调用都只是检索通道，不是本体节点。

## 2. 三阶段检索协议

| 阶段 | 目标 | 策略 | 完成判据 |
| --- | --- | --- | --- |
| 全量拓展检索 | 最大化召回 | 敏感式（宽检索式）：B_T 轴分解 + 受控词表扩展 + 同义词扩展 + 多来源并行 | 计划来源全部有检索记录（含 zero_hit 与 channel_failed 两种显式状态） |
| 审核检索 | 审计取到的与没取到的 | 覆盖审计 + 关键词合理性复审 | 七类盲点每项有结论（存在/不存在/无法判定+原因） |
| 收束目标检索 | 精确补检显式缺口 | 特异式（窄检索式）：由缺口生成定向检索式 | 显式缺口全部补检或显式放弃（含放弃理由） |

三阶段不是必须串行走完：小任务可从收束阶段起步（已知精确缺口时直接定向检索）。

## 3. 检索循环协议

```text
formulate (构造检索式)
  → execute (逐来源执行)
  → ingest (去重 + 分级 + 候选 StoreNode 登记)
  → audit (覆盖审计 + 关键词合理性复审)
  → revise_keywords (拓宽 / 收窄 / 换轴 / 换词表 / 换语言 / 换来源类)
  → decide (停止判定; 不停则回到 formulate)
```

- 默认最多 3 轮，硬上限 5 轮；超限必须显式登记未补缺口。
- **关键词变更合理性**是循环的核心步骤：每轮复审必须回答"当前检索词是否命中受控词表更优词条""零命中是词的问题还是真的没有"。每次变更在 RetrievalRound 登记 `change_reason`；同轴同词表连续两轮无新增即换轴。
- 停止条件（与 [output-contract.md](output-contract.md) 停止条件同构）：
  1. `rho_converged`：新增命中不再改变任务功能（[rho-convergence.md](rho-convergence.md) 收束信号）；
  2. `theta_scene_shift`：θ 达场景重识别阈值——该换轴而非换词，移交 [theta-switching.md](theta-switching.md)；
  3. `budget_exhausted`：预算耗尽，显式登记未补缺口；
  4. `marginal_gain_below_epsilon`：边际新增命中低于 epsilon_T 阈值；
  5. `blindspots_all_resolved`：七类盲点全部有结论。

## 4. 盲点发现协议（七类）

| 盲点 | 检测 | 响应 |
| --- | --- | --- |
| 来源盲点 | 来源覆盖矩阵空格；通道状态非 ok 未登记 | 补检或显式放弃并声明 |
| 词法盲点 | 复审发现更优受控词条；某来源零命中但同义词他处有命中 | 换词表 / 拓宽 |
| 模态盲点 | 继承 [modality-boundary.md](modality-boundary.md) 清单 | 显式声明缺失，结论降级为"正文阅读拓扑" |
| 结构盲点 | [reading-topology.md](reading-topology.md) 的 expected_but_absent / topology_gap | 生成 RetrievalFollowup 定向补检 |
| 时间盲点 | 时间窗与最新命中的时间差；撤稿与更正未查 | 收窄时间窗补检；查更正与撤稿 |
| 语言盲点 | 领域主要语言 vs 实际检索语言 | 换语言至少一轮 |
| 立场盲点 | 命中来源利益归属分布同质；反方/阴性/资助声明缺席 | 定向检索反方证据；引用前严格区分利益归属 |

立场盲点是硬约束：**有利益归属者的结论必须标注选择性偏倚风险，并重点检查其文献主线故意忽略的旁通路**；无利益归属者可自然引用。

## 5. 四类来源检索指南

| 类别 | 典型入口 | 约定性工具 | 证据分级 | 注意 |
| --- | --- | --- | --- | --- |
| 文献层 | PubMed / Embase / Scopus / WoS / Scholar / arXiv / bioRxiv | PICOS / MeSH / Boolean / search hedges / Cochrane 手册 | 高（同行评审） | 预印本分级不同；撤稿必查 |
| 社区落地层 | GitHub issues / StackOverflow / bioconductor forum / HN / Reddit / 知乎 | issue 与 PR 检索 / 复现报告 / 迁移讨论 | 中（真实落地信号） | 落地证据优先于宣称；幸存者偏差 |
| 实践经验层 | protocols.io / 官方文档 / 工程博客 / 会议报告 / 访谈 | 协议复现 / 配置示例 / 踩坑记录 | 中低（操作性高） | 每条给可追溯链接与访问日期 |
| 可参照 SOP 层 | ISO / GB / NIST / 行业手册 / vendor whitepaper | 标准编号 / 版本锁定 | 高（权威性） | 版本时效；vendor 有利益归属 |

证据分级按用途反转：找"如何落地"时社区与 SOP 优先于文献。分级只用于排序与披露，不冒充真值。

## 6. 约定性检索与设计性检索

- **约定性检索**：用社区冻结的检索约定（受控词表、PICOS/PRISMA、search hedges）。可复现、跨库一致，但领域新词滞后。
- **设计性检索**：任务特定构造（B_T 轴分解、同义词网络、敏感式 A / 特异式 B 双检索式）。覆盖特异缺口，但检索式必须登记才可复现。
- 配对规则：约定性给骨架，设计性补缺口；每轮关键词复审先查受控词表是否已有更优词条。

## 7. 鲁棒性协议

1. **通道故障区分**：`negative_result`（检索成功但无命中）≠ `channel_failed`（通道故障）；同通道连续三次故障即冻结并显式登记，不静默重试。
2. **去重**：来源指纹（标题+年份+来源域）生成稳定 ID，重复命中合并登记。
3. **来源分级**：每条命中登记类别与分级，只用于排序与披露。
4. **降级路径**：受限来源不可用时降级到替代来源，并按 modality-boundary 显式声明缺失，不得静默当作不存在。
5. **可追溯**：每条来源必须可追溯（URL/DOI/标准编号 + 访问日期）；严禁虚构检索结果或把未检索写成已检索。

## 8. 产物契约

| 产物 | 路径 | 必填字段 |
| --- | --- | --- |
| RetrievalPlan | `reference/retrieval/{plan_id}.yaml` | task_boundary_ref / phases / sources / queries / budget / stop_conditions |
| RetrievalRound | `reference/retrieval/{plan_id}/round_{n}.yaml` | round / queries / source_status / hits / blindspot_review / keyword_revision |
| RetrievalFollowup | `reference/retrieval/{plan_id}/followup_{n}.yaml` | blindspot_type / gap_description / next_query / status |

产物去向：来源本身作为地才（环境）候选 StoreNode 入藏；来源间关系登记 MutualNode；检索执行记录写入人题（读取记录）部分。

## 9. 验收标准

1. 三阶段均有执行记录或显式跳过理由；
2. 循环轮次 ≤ 硬上限，每轮有 blindspot_review 与 keyword_revision；
3. 七类盲点清单每项有结论；
4. 每条命中可追溯（链接/编号 + 访问日期）；
5. 检索计划的 YAML 结构通过 [validate_retrieval_spec.py](../extensions/systematic-retrieval/scripts/validate_retrieval_spec.py) 校验。

## 10. 禁止行为

- 不得虚构检索结果，不得把未检索的来源写成已检索；
- 不得把"检索到"写成"验证过"；
- 不得静默吞掉通道故障或缺失模态；
- 不得在立场盲点未审时直接引用有利益归属来源的结论而不标注偏倚风险；
- 不得把检索分支画成第四本体节点或新增 FlowEvent 类型；
- 不得超出硬上限继续循环而不登记未补缺口。
