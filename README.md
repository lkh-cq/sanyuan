# 三元三才·意识总线

意识总线是一个面向复杂科研、知识整理、项目规划和长上下文任务的认知预处理协议。它的目标不是替代现实证据、证明系统或通用 Agent, 而是在回答、阅读、整理和迁移材料之前, 先把任务边界、信息结构、关系路径和可验证输出整理清楚。

当前公开基线为 `V3.2.0`。

## 项目定位

本项目把复杂任务拆成几个可检查的层次:

| 层次 | 作用 | 入口 |
| --- | --- | --- |
| 任务边界 | 先定义任务目标、禁止损失、可验证功能和停止条件 | [`references/task-boundary.md`](references/task-boundary.md) |
| 元信息空间 | 记录内容本身, 使用三才藏: 天才、地才、人才 | [`references/sancai-store.md`](references/sancai-store.md) |
| 互信息空间 | 记录关系、流止、转换、反馈和路径残差 | [`references/hu-observation-space.md`](references/hu-observation-space.md) |
| 藏归循环 | 写入具体内容, 再按任务读取相关节点 | [`references/zang-gui-orchestrator.md`](references/zang-gui-orchestrator.md) |
| 注意力控制 | 用 `ρ/θ`、缓存波和 `n` 位聚焦控制收束与切换 | [`references/rho-convergence.md`](references/rho-convergence.md), [`references/theta-switching.md`](references/theta-switching.md), [`references/n-focus.md`](references/n-focus.md) |
| 扩展迁移 | 接收归档对话中的新方案, 但不直接污染冻结本体 | [`references/archive-ingestion.md`](references/archive-ingestion.md) |

最短理解方式:

> 先限定任务边界, 再分离内容与关系, 最后只读取当前任务真正需要的上下文。

## 冻结本体

`V3.2.0` 中以下定义为冻结本体, 扩展模块不得静默改写。

| 概念 | 固定含义 |
| --- | --- |
| 三才, 藏 | 天才=规律, 地才=环境, 人才=实践 |
| 三题, 归 | 天题=信息的本来样貌, 地题=读取方式, 人题=读取记录 |
| 天地人拓扑 | 天 ↔ 地 ↔ 人, 地居中, 管理流与止, 不携带固有方向 |
| 互 | 独立关系观测空间, `FlowEvent` 是互的子类型 |
| ρ/θ | `ρ + θ = 1`; ρ 是收束度, θ 是切换度, 不是正确率/错误率 |
| n 位聚焦 | 离线建表, 调用时查表, 不在调用时运行 Dijkstra |

禁止把三才和三题合并成一层, 也禁止另造“天元/地元/人元”作为第三套分类。

## 三元语法的位置

三元语法在本项目中应被理解为科研文本的阅读拓扑方法, 不是写作生成器。

它读取已经存在的论文或材料, 观察作者实际如何组织信息, 并把行文功能、衔接、顺序、回环、证据承重、缺口和引用关系转成可追溯的拓扑表示。

相关扩展见 [`references/reading-topology.md`](references/reading-topology.md)。核心纠偏是:

- 节点是对原文已经发生的行文功能的观测标签。
- 路径是对文本实际组织方式的描述。
- 常见路径只能是语料观察结果, 不能反过来变成写作强制模板。
- 阅读拓扑需要记录阅读者任务坐标、证据压力、拓扑断裂和缺席节点。

## 多模态边界

在纯文本或弱多模态环境中, 项目必须记录模态可见性边界。否则容易把“正文声称的拓扑”误判成“证据实际呈现的拓扑”。

相关扩展见 [`references/modality-boundary.md`](references/modality-boundary.md)。尤其是生物医学论文阅读中, Figure、Supplementary figure、图注、表格、流式门控、WB、IF、IHC、HE、原始矩阵和实验视频都可能改变证据拓扑。

基本规则:

- 看不到的模态不得静默当作不存在。
- text-only 环境中, 结果最多称为正文阅读拓扑。
- 涉及图像质量、空间定位、方法动作和原始数据形态时, 必须降级证据置信度。
- `claim` 与 `evidence` 的关系应进入互空间, 不嵌入内容节点。

## 仓库结构

```text
.
├── SKILL.md                         # Skill 运行入口
├── README.md                        # 人类读者说明书
└── references/
    ├── architecture.md              # 冻结本体与总体架构
    ├── project-manifest.yaml         # 机器清单
    ├── task-boundary.md              # 任务边界编译
    ├── sancai-store.md               # 三才藏
    ├── santi-read.md                 # 三题归
    ├── hu-observation-space.md       # 互信息空间
    ├── meta-normalization.md         # 元空间归一化
    ├── hu-normalization.md           # 互空间归一化
    ├── zang-gui-orchestrator.md      # 藏归调度
    ├── flow-topology.md              # 流止拓扑
    ├── rho-convergence.md            # ρ 收束
    ├── theta-switching.md            # θ 切换
    ├── cache-wave.md                 # 缓存波动力学
    ├── n-focus.md                    # n 位聚焦
    ├── condense-protocol.md          # 压缩协议
    ├── archive-ingestion.md          # 归档方案迁移协议
    ├── reading-topology.md           # 三元语法阅读拓扑
    └── modality-boundary.md          # 模态可见性边界
```

`references/` 是 Skill 自带的只读规范目录。运行任务时产生的材料、节点、读取记录和路由表应写入任务项目自己的 `reference/` 目录, 不写回 `references/`。

## 如何使用

通常不需要一次读完整个仓库。按任务读取最小模块即可。

| 需求 | 建议入口 |
| --- | --- |
| 快速筛选、比较、压缩信息 | [`references/fast-filter-recipe.yaml`](references/fast-filter-recipe.yaml) |
| 科研深度分析、多材料整合 | [`references/research-recipe.yaml`](references/research-recipe.yaml) |
| 修改本体、公式、模块或版本 | [`references/architecture.md`](references/architecture.md) + [`references/project-manifest.yaml`](references/project-manifest.yaml) |
| 把旧对话方案纳入项目 | [`references/archive-ingestion.md`](references/archive-ingestion.md) |
| 讨论三元语法 | [`references/reading-topology.md`](references/reading-topology.md) |
| 处理图表、图像、视频缺失风险 | [`references/modality-boundary.md`](references/modality-boundary.md) |

## 归档方案迁移

归档对话中的方案不能直接混入冻结本体。迁移前必须先登记为 `archive_item`, 判断它解决什么问题、属于哪个层级、是否违反冻结定义、接入哪里、加入和遗漏分别有什么风险。

状态分为:

| 状态 | 含义 |
| --- | --- |
| `candidate` | 已识别, 尚未判断是否进入项目 |
| `accepted` | 接受为扩展或修订项 |
| `rejected` | 明确不纳入, 保留拒绝理由 |
| `deferred` | 有价值但当前接口、证据或工程条件不足 |

当前已接入的归档迁移主题包括:

- 三元语法是阅读拓扑方法。
- 模态可见性边界。
- 阅读者/任务坐标。
- 证据压力。
- 拓扑断裂与缺席节点。
- 图文互证。

## 版本原则

- 冻结本体必须稳定。
- 用户最新明确纠正高于旧版本文件。
- 新方案先进入扩展或迁移层, 不直接覆盖核心定义。
- 工程未接线的方案不得伪装成已实现能力。
- 缺少可计算输入时, 不伪造精确的 `ρ`、`θ`、`Ω`、`∇E` 或 `θ'` 数值。

## 当前状态

`V3.2.0` 已提供可读的 Skill 入口、核心模块、预处理模块、藏归模块、互空间模块、任务配方、Schema 和扩展迁移层。

下一步重点不是继续堆概念, 而是把归档对话中的候选方案逐条迁移为可判断、可接线、可拒绝、可追溯的项目条目。