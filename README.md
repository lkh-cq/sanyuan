# 三元三才·意识总线

<p align="center">
  <img src="assets/mascot-abigail.png" alt="阿比盖尔，三元三才项目吉祥物" width="240">
</p>

<p align="center">
  <strong>阿比盖尔 / 塞壬种子</strong><br>
  象征可缓慢生长、可迁移、可再组织的认知新芽。
</p>

三元三才·意识总线是一个面向 RAG 的前端语义—拓扑预处理插件，而不是 RAG 本身；它负责在检索之前组织用户意图、来源信息与上下文关系，并仅以 ρ/θ 作为主注意力辅助，不替代下游检索、重排、推理或生成。它面向复杂科研、知识整理、项目规划与长上下文任务，先限定任务边界，再分离内容与关系，最后把内部结构转译为读者可以直接理解的结果。它不是现实机制、证明系统或通用 Agent。

当前项目版本以 [`references/project-manifest.yaml`](references/project-manifest.yaml) 的 `project.version` 为唯一来源；正式版本由通过校验的 `v<version>` Git tag 标记。

## 支持 Agent

协议与 Skill 已适配以下 Agent 环境：

- **Hermes** <img src="assets/agent-icons/hermes.png" width="20" height="20" alt="Hermes 官方图标"> — 意识总线技能宿主：`skill_view(conscious / unconscious / conscious-archive)` 上岗必载
- **Claude Code** <img src="assets/agent-icons/claude-code.svg" width="20" height="20" alt="Anthropic 官方图标"> — 编码 worker 编排：Hermes 规划 + CC 落地（`claude -p ... --permission-mode acceptEdits`）
- **Codex / GPT** <img src="assets/agent-icons/codex.png" width="20" height="20" alt="Codex 官方图标"> — OpenAI 界面元数据（[`agents/openai.yaml`](agents/openai.yaml)）
- **dsh** <img src="assets/agent-icons/dsh.svg" width="20" height="20" alt="dsh 官方图标"> — dsh skill 兼容适配：`sanyuan-hive`（metadata.version `0.1.0-dsh.1`，单层 bundle + dsh 字段最小集）

## 从哪里开始

| 你要做什么 | 读取入口 |
| --- | --- |
| 理解项目本体与职责边界 | [`references/architecture.md`](references/architecture.md) |
| 快速筛选、比较或压缩信息 | [`references/fast-filter-recipe.yaml`](references/fast-filter-recipe.yaml) |
| 科研深度分析与多材料整合 | [`references/research-recipe.yaml`](references/research-recipe.yaml) |
| 分析论文写作逻辑与证据缺口 | [`references/reading-topology.md`](references/reading-topology.md) |
| 输出可读的文献逻辑段落 | [`references/reader-facing-analysis.md`](references/reader-facing-analysis.md) |
| 运行代码/计算风险审计与最小恢复 | [`references/endoscopic-code-actuation.md`](references/endoscopic-code-actuation.md) |
| 理解用户原始设计动机 | [`references/original-anchors.md`](references/original-anchors.md) |
| 阅读八卷二十八章理论来源浓缩 | [`references/sanyuan-daobian-framework.md`](references/sanyuan-daobian-framework.md) |
| 修改模块、本体、Schema 或版本 | [`references/project-manifest.yaml`](references/project-manifest.yaml) + [`references/version-provenance.md`](references/version-provenance.md) |

冻结定义只在 [`architecture.md`](references/architecture.md) 维护。`SKILL.md` 与本 README 只提供流程和导航，避免多份本体静默漂移。

## 项目如何工作

| 层级 | 作用 |
| --- | --- |
| 任务边界 | 明确目标、禁止损失、可验证功能、误差与停止条件 |
| 元信息空间 | 用三才藏保存内容本身及其来源 |
| 互信息空间 | 保存关系、流止、转换、反馈与路径残差 |
| 藏归与耦合态 | 分开保存内容节点和关系节点，再用耦合态组成可检索事务 |
| 注意力控制 | 以 ρ/θ、缓存波和 n 位聚焦控制收束与切换 |
| Endoscope | 把归一化省略信息编译为 NSL，按 TaskProfile 探测复活并独立控制 E/S/O |
| 读者端交付 | 将内部拓扑转译为连贯、简明、可独立阅读的自然语言 |

最短理解方式：

> 先限定任务边界，再分离内容与关系，最后只读取当前任务真正需要的上下文。

## Endoscope / Bloodtesting

Endoscope 是实验性代码与计算风险扩展，不修改冻结本体。它复用元/互归一化已经产生的 `omitted_features + recovery_refs`，形成轻量 Normalization Shadow Ledger（NSL）；只有新观测命中 shadow 或其与 active view 的关系时，才恢复最小集合。

完整链路是：`B_T → TaskProfile → M/H normalization → NSL → Probe/Event → minimal revival → E/S/O → BloodRecord → calibration candidate`。执行、状态与最终交付彼此独立，因此安全诊断可以继续而可疑状态进入隔离区，最终输出保持阻断；不可逆副作用则必须停在执行闸门前。

参考实现采用 **Python 标准库控制面 + 可选 base R 适配器**。没有 R 时仍能运行完整控制链和 Python AST/通用静态探针，但会明确报告 R 能力降级；R 可用时增加 `parse()` 与低成本 R 信号，不执行用户 R 代码。Tree-sitter、LSP、`data.table`、`igraph`、`torch` 和 C++ 后端均为未来可选增强，不是硬依赖。

Bloodtesting 提供 12 个初始对照夹具，包括 PDE 截断污染与 Lasso 支持集替代。校准脚本只产生候选策略，永不自动修改 ρ、模型权重或稳定策略。

## 三元语法与文献分析

三元语法在当前项目中是阅读拓扑方法：它观察论文实际上如何组织信息、推进论证与承载证据。节点编号、关系代码、内部箭头和矩阵只用于工作层；正式产物必须说明作者先写什么、如何承接或推进、证据支持到哪里。

无注释简图不能替代文字分析。图表只有在显著提升理解时使用，并写全名称、关系含义、证据来源和图例。

## 仓库结构

```text
.
├── .github/workflows/       # 自动校验与版本标签
├── agents/                  # GPT/Codex 界面元数据
├── assets/                  # 图标、吉祥物与 5 张 Canvas
├── extensions/              # 可选子模块（process-transparency、index-naming-norm）
├── references/              # 本体、协议、配方、来源、扩展与 Schema
├── scripts/                 # 确定性校验、Endoscope 控制器与 R 适配器
├── CONTRIBUTING.md          # 提交、评审与发布规范
├── LICENSE                  # 权利声明
├── README.md                # 人类读者入口
└── SKILL.md                 # Skill 运行入口
```

`references/` 按功能分为：

- 权威与来源：架构、版本来源、用户原话、三元道辩浓缩、反例免疫；
- 任务与控制：任务边界、拆分、ρ/θ、n 位聚焦、缓存波；
- 藏归与关系：三才、三题、互、流止、耦合态、写入与读取；
- 分析与交付：阅读拓扑、读者端分析、多模态边界、输出契约；
- 实验接口：Endoscope TaskProfile、NSL、E/S/O、Bloodtesting；
- 机器约束：项目清单、配方、验收用例与全部 Schema。

所有模块路径都登记在 [`project-manifest.yaml`](references/project-manifest.yaml)，校验脚本会检查断链、孤儿文件、YAML、Canvas、配方顺序、版本生命周期与验收用例结构。

## 扩展（extensions/ 与协议文档）

2026-08-12 新增两个扩展（已合并进 main，均通过独立并行门控测试）：

### index-naming-norm（extensions/index-naming/）

知识库目录索引的命名、分层与拓扑审计规范（v2.0，2026-08-12 用户冻结）：

- **层级 = 上游目录的文件夹个数**：0=根目录总 INDEX，1=根文件夹 main branch，2=次级文件夹，依此类推。
- **main branch index（层级 1）**：按内容命名或编号（语义名须以 `_index` 结尾），文件第一行加小标题标引该目录具体内容，供下一级索引引用。
- **子分支（层级 ≥2）**：严格 `index.<date>.<内容>.<层级>` 三段式（YYYYMMDD + 主题短词 + 数字）。
- 仅根目录 `_index.md` 保留；层级 ≥1 的 `_index.md` 一律改造。`COLOR_INDEX.md`/`GEO_ROOT_INDEX.md`/CSV 索引不参与。
- **校验**：`python3 extensions/index-naming/scripts/validate_index_naming.py --dry <目录>`（只读预览不合规清单）。
- **约束**：只治理 Markdown 目录索引；node_modules/.git/dist 等程序索引不进入知识图谱。来源：hermes_memory 全盘索引拓扑审计（2026-08-12，367 个 index 路径）。

> 注：mirror 总线（跨窗口观察）是**独立功能**，协议与脚本已移出本仓库，见独立仓库 [lkh-cq/mirror-bus](https://github.com/lkh-cq/mirror-bus)（含 mirror-bus-spec、soul-echo-spec 与运行时脚本）。

## 版本与成熟度

- 项目版本只有一个，读取 `project.version`。
- 模块版本是独立演进号，不代表整个项目版本。
- `stable` 表示已进入冻结运行链；`experimental` 表示接口已登记但仍需证据或使用经验。
- 新方案先进入迁移或实验层，不直接覆盖冻结本体。
- 每次默认分支发布必须先通过自动校验；相同版本不得指向两个不同提交。

### 版本更新

版本与变更历史以 [`references/version-provenance.md`](references/version-provenance.md) 为唯一记录（process-transparency 扩展 → Endoscope 全链路实验实现 → 多时间尺度再注入实验组合，版本演进见该文件）。仓库规则禁止版本号漂移到 manifest/provenance 之外，README 不重复登记。

## 资产与授权

阿比盖尔是为本项目创作的 AI 辅助原创角色资产，来源于项目所有者提供的角色设定与参考，不是第三方素材。其使用受本仓库 [`LICENSE`](LICENSE) 约束。

本仓库当前保留所有权利。公开可见不等于授权复制、修改、分发或再许可；如需开放复用，将由项目所有者另行选择并发布明确的开源协议。

## 维护

提交前运行：

```bash
python3 scripts/validate_bundle.py
python3 scripts/validate_endoscope.py
python3 scripts/endoscope.py selftest
# 有 R 环境时：
Rscript scripts/endoscope_r.R selftest
```

确定性校验只检查结构与可执行约束，不宣称理解语义。涉及本体、交付行为或复杂任务流程的修改，还必须做独立前向测试。详细规则见 [`CONTRIBUTING.md`](CONTRIBUTING.md)。
