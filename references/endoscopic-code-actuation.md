---
name: Endoscopic Code Actuation
module_id: extension-endoscopic-code-actuation
description: "三元归一化阴影驱动的代码/计算风险审计与最小恢复协议；以 TaskProfile、NSL、Probe、E/S/O 三闸门和 Bloodtesting 构成可持续全链路。"
version: 0.2.0
category: extension
manifest_ref: references/project-manifest.yaml
---

# Endoscopic Code Actuation 0.2

> Endoscope 是实验性扩展，不修改冻结本体，不是通用 Agent，也不声称能在线修改模型权重、隐藏状态或托管模型内部解码器。
>
> 核心原则：**谁压缩，谁留下恢复坐标；谁过滤，谁解释过滤理由；谁截断，谁留下重新打开的条件。**

## 1. Scope / Non-goals

Endoscope 处理的是“任务条件化信息收缩之后，何时需要恢复被暂时忽略的信息，以及如何独立控制执行、状态和最终交付”。它面向代码生成/修改、Bug 修复、数值计算、统计建模、科研计算、ETL、数据库写入、跨模块重构、CI/CD、权限/生产变更和长时间计算。

它不代替 `B_T`，不把启发式分数解释成错误概率或 ρ，不默认停止一切计算，不自动执行不可逆副作用，不直接修改 LLM 权重，不把旧 SVD 低方差分量提升为正式门控依据，也不用一套固定 Probe 代替 TaskProfile。

## 2. 全链路

```text
raw input / source
        ↓
       B_T
        ↓
TaskProfile P_T
        ↓
meta / hu normalization
   ├─────────── active M_T / H_T
   └─────────── omitted + recovery_refs
                       ↓
             Normalization Shadow Ledger (NSL)
                       ↓
source/runtime/cross-space/domain Probe
                       ↓
             Observation Event
                       ↓
             Shadow revival rank
                       ↓
              minimal recovery refs
                       ↓
           E / S / O Gate Decision
                       ↓
      diagnostic / review / actuation / delivery
                       ↓
               BloodRecord
                       ↓
                calibration
                       ↓
 candidate policy -> shadow replay -> A/B -> explicit promotion
```

Endoscope 不额外复制完整上下文。正常情况下只持有 shadow 元数据和恢复引用；只有出现新证据时才按最小集合恢复。

## 3. 语言与环境分工

### 3.1 Python 控制面

`scripts/endoscope.py` 是权威参考控制器：Python 3.10+、只使用标准库，负责 TaskProfile、NSL、Probe 汇总、shadow revival、E/S/O、Bloodtesting 记录和校准；Python 源码用标准库 `ast` 做结构解析。选择 Python 作为控制面是为了让没有 R、Tree-sitter、LSP 或数据库客户端的环境仍能运行协议降级版。

### 3.2 R 领域适配器

`scripts/endoscope_r.R` 是 base R 零包依赖适配器：使用 `parse(..., keep.source=TRUE)` 验证 R 语法；对 `NA` 敏感分支、强制转换、全局赋值、外部写入、动态执行和并发产生结构化 signal；输出 JSON 给 Python 控制面。R 不可用时明确记录 `adapter_status=unavailable_fallback_static`，而不是伪装成完整 R 语义分析。

R 适合承担统计/科研领域 Probe 和未来长表 provenance；但 0.2 不把 `data.table`、`igraph`、`Matrix`、`torch`、`rly`、`Rcpp/cpp11` 设为硬依赖。

### 3.3 可选增强

未来可替换或并行接入 Tree-sitter（增量语法树）、LSP（definition/reference/type/caller）、R `data.table`、`igraph`、R `torch`、`cpp11/Rcpp`。只有 benchmark 证明热点后才允许把重依赖引入关键路径，而且不得改变核心 JSON 合同。

## 4. TaskProfile：Probe 从属于任务

`B_T` 之后先编译 Endoscope TaskProfile `P_T`。TaskProfile 不是新的任务本体，只把当前任务边界翻译成 Probe 保护对象、shadow 关注点、默认风险轴和恢复上限。

仓库 `endoscope-task-profiles.json` 覆盖 `small_completion`、`bug_fix`、`numerical_computation`、`statistical_modeling`、`scientific_computing`、`data_etl`、`database_mutation`、`cross_module_refactor`、`ci_deploy`、`long_running_compute` 等场景。TaskProfile 必须允许显式选择；自动分类只能作为候选，不得静默改变最高干预权限。

## 5. Normalization Shadow Ledger（NSL）

三元正式归一化已经产生 `omitted_features` 与 `recovery_refs`。Endoscope 把这些副产物编译成 NSL，而不是重新扫描全部原材料。

```json
{
  "shadow_id": "sh_...",
  "boundary_id": "bt_...",
  "space": "meta",
  "stage": "meta_normalization",
  "feature": "sample_size",
  "recovery_ref": "source://meta/17",
  "omitted_reason": "indifferent",
  "relation_to_active": [],
  "recovery_cost": "cheap",
  "sensitivity": "normal",
  "status": "shadow"
}
```

NSL 不是第二份上下文，不存完整内容。`recovery_ref` 只能指向可验证来源；无法恢复的条目必须明确为 `null/unknown`。`path_residual` 仍属于互空间的正式特殊保护特征，不能与 NSL shadow 混称 residual。

## 6. Bleed 定义

0.2 将 bleed 定义为：**原本在当前 `B_T` 下被判定为可省略、可隔离或可延迟的信息，在任务演化过程中因为新观测重新获得功能相关性，或者其缺失开始影响执行、解释或交付边界。**

因此 bleed 不等于异常：程序成功但统计支持集不稳定、PDE 高阶递推静默读出截断边界、R `as.numeric(factor)` 运行成功但语义变化、生产写入发生在验证前，都可构成 bleed；单纯看到复杂代码但没有新证据不是 bleed。

## 7. Probe 来源与优先级

优先使用已经存在的证据，再调用更昂贵 Probe：`B_T/TaskProfile` → 归一化副产物 → `H'_T`/`H_T` 跨空间差异 → focus/condense/output 丢弃描述 → parser/AST → R adapter → 可选 Tree-sitter/LSP → 领域 Probe → 外部副作用 Probe。

原则：`Probe Cost << Re-read Cost`。没有理由时禁止一次恢复全部 shadow。

## 8. Observation Event 合同

Probe 不直接修改 Gate，而先产生 Observation Event：

```json
{
  "event_id": "evt_...",
  "event_type": "probe_observation",
  "signals": ["support_instability"],
  "features": ["feature_correlation"],
  "locus": "fit_model",
  "evidence_type": "runtime_observation"
}
```

事件中的 evidence 必须是观测或明确恢复内容。推断不能伪装成观测。与 `process-transparency` 共用时，event 可作为其 `evidence`，而推断只能进入 `assumption`。

## 9. 最小恢复算法

输入 NSL、TaskProfile、Observation Event。参考实现只做排序，不声称概率：event 与 shadow feature 或 `relation_to_active` 命中优先；TaskProfile `shadow_watch` 只能在已有事件证据命中时加权，不能单独触发复活；`conflicting/insufficient` 比普通 `indifferent` 更优先；超出 `max_cost` 的条目不自动恢复；只返回 `recovery_ref`，不把整份原始材料重新注入。

输出 `revival_rank` 是排序值，`rank_is_probability=false`。

## 10. E/S/O 三闸门

Execution Gate：`OPEN | CONTINUE_DIAGNOSTIC | PAUSE_BEFORE_SIDE_EFFECT | STOP`。
State Gate：`OPEN | FILTERED | QUARANTINED | DISCARD`。
Output Gate：`OPEN | REVIEW_REQUIRED | BLOCKED | REPLACE`。

典型统计任务可为 `E=CONTINUE_DIAGNOSTIC / S=QUARANTINED / O=BLOCKED`；典型不可逆生产写入为 `E=PAUSE_BEFORE_SIDE_EFFECT / S=QUARANTINED / O=BLOCKED`。`E=OPEN` 永远不推出 `O=OPEN`。

## 11. 风险轴与权限边界

保留未校准四轴：`S` scope、`B` blast radius、`U` uncertainty、`D` dependency depth。初始启发式：

```text
R = 0.25*S + 0.35*B + 0.25*U + 0.15*D
```

它只用于排序，不是错误概率。干预层级为 `PATCH_LEAF`、`PATCH_LOCAL`、`NO_TOUCH`。数据库 schema、生产批量写、权限/密钥、基础设施、多模块公共接口、并发共享状态和不可快速回滚的大端任务默认为心脏级 `NO_TOUCH`；安全诊断可继续，但副作用必须停在执行闸门前。

## 12. R 使用边界

R adapter 0.2 只保证 base R parser 的语法成功/失败、低成本静态 signal、UTF-8 JSON 输出，并且不执行用户 R 代码、不加载项目包。它不保证类型推导、NSE/rlang 完整语义、`data.table` 引用语义静态证明、DBI transaction 实际状态、package namespace 解析、测试执行或动态对象值。这些能力必须由 runtime adapter、项目测试或未来 R language server 获得。

## 13. Bloodtesting

Bloodtesting 对照 `continue-generation` 与 `task-profile -> probe -> shadow revival -> E/S/O -> review/recovery`，至少记录 `first_bleed_locus`、`propagation_span`、`avoidable_output_tokens`、`false_alarm/missed_bleed`、`gate_accuracy`、`recovered_items`、`effective_recovered_items` 和 `recovery_efficiency`。

`Recovery Efficiency = effective_recovered_items / recovered_items`。

仓库 `endoscope-bloodtesting.yaml` 提供 12 个初始夹具，其中包括 PDE 截断污染和 Lasso 支持集替代。

## 14. 自助迭代，但禁止自证式自改

持续化流程为 `run -> BloodRecord -> calibrate -> candidate policy -> shadow replay -> A/B review -> explicit promotion`。`scripts/endoscope.py calibrate` 只产生 `collect_more`、`eligible_for_shadow_replay` 或 `recalibrate_candidate` 等候选状态，永远输出 `auto_promote=false`。任何权重、TaskProfile 或 ρ 场景向量都必须显式评审后再写入稳定层。

## 15. 与 ρ、θ 和 process-transparency 的接口

Endoscope 给 ρ 的是观测事件和建议注意方向，`rho_value=null`；ρ 是证据出现后的注意力再分配器，不是风险检测器。若当前 TaskProfile 边界持续失效，可向 θ 提供“场景边界可能失效”事件，但是否切换仍由 θ 决定。

`process-transparency` 记录“结论—证据—假设—验证”；Endoscope 记录“哪些信息被省略、何时复活、为什么改变 Gate”。Endoscope 事件可成为观测证据，但不能替代决策日志。

## 16. 兼容性与降级阶梯

| 环境 | 能力 |
| --- | --- |
| Python 3.10+ only | 完整控制链 + Python AST + 通用静态 Probe |
| Python + Rscript | 增强 R parse/静态 Probe |
| + Tree-sitter | 增量多语言 AST（可选） |
| + LSP | definition/reference/type/caller（可选） |
| + 项目 runtime/test | 动态值、测试、transaction、领域证据 |

任何 adapter 不可用时必须显式报告 capability loss。协议 JSON 使用稳定字段和 `protocol_version`；未知字段允许忽略，删除或改义字段必须提升协议版本。

## 17. CLI

```bash
python scripts/endoscope.py profile statistical_modeling
python scripts/endoscope.py probe analysis.R
python scripts/endoscope.py shadow-build normalization-snapshot.json
python scripts/endoscope.py revive ledger.json --task-family statistical_modeling --event-json '{"signals":["support_instability"],"features":["feature_correlation"]}'
python scripts/endoscope.py gate --scope 1 --blast 1 --uncertainty 2 --dependency 1 --tainted
python scripts/endoscope.py pipeline --task-family statistical_modeling --source analysis.R --snapshot normalization-snapshot.json --event-json '{"features":["feature_correlation"],"signals":["support_instability"]}'
python scripts/endoscope.py blood-record record.json --append reference/flow/endoscope-blood.jsonl
python scripts/endoscope.py calibrate reference/flow/endoscope-blood.jsonl
python scripts/endoscope.py selftest
Rscript scripts/endoscope_r.R selftest
```

## 18. 数据存储边界

规范文件在只读 `references/`；任务运行时数据不得写入其中。推荐使用 `reference/source/` 保存可恢复原材料、`reference/store/` 保存结构节点、`reference/read/` 保存当前恢复视图、`reference/flow/` 保存 Endoscope events/BloodRecord JSONL、`reference/routing/` 保存 recovery_ref/adapter address。BloodRecord 可能包含敏感路径、数据库名、错误内容或样本标识，必须沿用任务数据访问控制。

## 19. 验收与发布边界

0.2 最低验收：Python `selftest`；base R adapter `selftest`；TaskProfile/JSON Schema/Bloodtesting 可解析；tainted 场景允许诊断继续但 `O=BLOCKED`；destructive/credential 场景必须 `PAUSE_BEFORE_SIDE_EFFECT + NO_TOUCH`；shadow revival 只返回最小 recovery refs；calibration 不自动写回策略；`architecture.md` 不因该扩展修改；项目 bundle validator 继续通过。

这些通过只证明工程合同与确定性参考实现自洽，不证明 Endoscope 已在真实 coding agent 上达到更高正确率或节省固定比例 token；真实收益只能由 Bloodtesting 前向数据支持。
