---
name: systematic-retrieval
description: "Use when 需要外部信息且要求可审计检索: 文献调研/社区方案挖掘/找SOP/盲点排查/系统性综述取材. 三阶段(全量拓展→审核→收束) + 检索-获取-审核-变更关键词循环 + 七类盲点 + 四类来源指南."
version: 0.1.0
category: research
---

# 系统化检索分支 (systematic-retrieval)

> 模块: extension-systematic-retrieval (experimental)
> 机器协议: references/retrieval-protocol.yaml | 规范: references/systematic-retrieval.md
> 定位: consciousness-bus 管"取回之后", 本分支管"取"——B_T 之后、三才藏之前。

## 一、触发条件

- 需要外部信息且任务对"取全 / 取准"敏感（综述 / 调研 / 选型 / 排坑）
- 用户要求系统性检索、文献综述、社区方案比较、找可参照 SOP
- 已有材料出现 expected_but_absent 或盲点，需要定向补检

## 二、三阶段速查

| 阶段 | 一句话 |
| --- | --- |
| 全量拓展检索 | 宽检索式 + 多来源并行，宁多勿漏，来源全有记录 |
| 审核检索 | 审"取到的+没取到的"：盲点逐项核查 + 关键词合理性复审 |
| 收束目标检索 | 窄检索式只补显式缺口，ρ 收束即停 |

## 三、循环（每轮必做）

```text
构造检索式 → 执行 → 登记(去重/分级) → 审核(覆盖+关键词复审) → 变更关键词 → 停止判定
```

- 默认 ≤3 轮，硬上限 5 轮；每轮必须登记 blindspot_review 与 keyword_revision（含变更理由）。
- 关键词变更动作：`broaden / narrow / swap_axis / swap_vocabulary / swap_language / swap_source_class`。
- 同轴同词表连续两轮无新增命中 → 换轴。

## 四、七类盲点速查

`source` 来源没检全 · `lexical` 词没覆盖 · `modality` 模态受限 · `structural` 应出现而未出现 · `temporal` 时间窗外缺席 · `language` 语言缺席 · `stance` 反方/利益归属证据缺席

> stance 是硬约束：有利益归属者的结论标注选择性偏倚风险，并重点查其主线忽略的旁通路。

## 五、四类来源速查

| 用途 | 优先 |
| --- | --- |
| 机理 / 证据强度 | literature（PubMed/Embase/Scopus…，PICOS+MeSH+hedges） |
| 真实落地 / 踩坑 | community（GitHub issues/SO/forum…） |
| 操作细节 | practice（protocols.io/官方文档/工程博客…） |
| 标准规范 | sop（ISO/GB/NIST/行业手册…） |

## 六、鲁棒性红线

- `negative_result` ≠ `channel_failed`；同通道三连故障 → 冻结并显式登记。
- 每条命中必须可追溯（URL/DOI/标准号 + 访问日期）。
- 缺失来源/模态显式声明，不静默省略；严禁虚构检索结果。

## 七、执行步骤

1. 读 B_T，按 schema-retrieval-plan.schema.yaml 写 RetrievalPlan 登记 `reference/retrieval/{plan_id}.yaml`
2. 跑三阶段 + 循环，每轮写 RetrievalRound
3. 盲点结论生成 RetrievalFollowup 并补检
4. 来源入三才藏（地才候选 StoreNode），关系记 MutualNode
5. 交付时按 blindspot 清单声明"没检到什么"

## 八、自测清单

- [ ] `python3 extensions/systematic-retrieval/scripts/validate_retrieval_spec.py` 通过
- [ ] `python3 extensions/systematic-retrieval/scripts/validate_retrieval_spec.py --plan <plan.yaml>` 对已写计划通过
- [ ] `python3 scripts/validate_bundle.py` 仍通过（登记完整性）
- [ ] 每轮 round 记录含 blindspot_review + keyword_revision.change_reason
- [ ] 交付含"未检索来源/缺失模态/未补缺口"显式声明

> 版本: 0.1.0 | 2026-08-26 | 协议与规范见 references/（只读层，运行产物写 reference/retrieval/）
