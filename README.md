# 三元三才·意识总线

<p align="center">
  <img src="assets/mascot-abigail.webp" alt="阿比盖尔，三元三才项目吉祥物" width="240">
</p>

<p align="center">
  <strong>阿比盖尔 / 塞壬种子</strong><br>
  象征可缓慢生长、可迁移、可再组织的认知新芽。
</p>

意识总线是面向复杂科研、知识整理、项目规划与长上下文任务的认知预处理协议。它先限定任务边界，再分离内容与关系，最后把内部结构转译为读者可以直接理解的结果。它不是现实机制、证明系统或通用 Agent。

当前项目版本以 [`references/project-manifest.yaml`](references/project-manifest.yaml) 的 `project.version` 为唯一来源；正式版本由通过校验的 `v<version>` Git tag 标记。

## 从哪里开始

| 你要做什么 | 读取入口 |
| --- | --- |
| 理解项目本体与职责边界 | [`references/architecture.md`](references/architecture.md) |
| 快速筛选、比较或压缩信息 | [`references/fast-filter-recipe.yaml`](references/fast-filter-recipe.yaml) |
| 科研深度分析与多材料整合 | [`references/research-recipe.yaml`](references/research-recipe.yaml) |
| 分析论文写作逻辑与证据缺口 | [`references/reading-topology.md`](references/reading-topology.md) |
| 输出可读的文献逻辑段落 | [`references/reader-facing-analysis.md`](references/reader-facing-analysis.md) |
| 在代码生成中探测高危点、截断输出并限制修改层级 | [`references/endoscopic-code-actuation.md`](references/endoscopic-code-actuation.md) |
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
| 代码风险干预 | Endoscope 以探针和 Bloodtesting 校准控制继续生成、截断、审核、局部修改或 NO_TOUCH |
| 读者端交付 | 将内部拓扑转译为连贯、简明、可独立阅读的自然语言 |

最短理解方式：

> 先限定任务边界，再分离内容与关系，最后只读取当前任务真正需要的上下文。

## Endoscope / Bloodtesting

Endoscope 是实验性代码干预扩展，不修改冻结本体。它把“继续生成完整源码”变成一个可被风险事件打断的动作：先用最小探针定位数据、依赖和副作用层面的首次“出血点”，再由输出闸门决定继续、`CUT_OUTPUT -> REVIEW` 或 `NO_TOUCH`。

仓库提供 [`references/endoscope-bloodtesting.yaml`](references/endoscope-bloodtesting.yaml) 的 10 组嵌套复合代码对照夹具，以及轻量控制器 `scripts/endoscope.py`。风险权重仍是待实测校准的启发式，不解释成真实错误概率，也不伪造 ρ 数值。

## 三元语法与文献分析

三元语法在当前项目中是阅读拓扑方法：它观察论文实际上如何组织信息、推进论证与承载证据。节点编号、关系代码、内部箭头和矩阵只用于工作层；正式产物必须说明作者先写什么、如何承接或推进、证据支持到哪里。

无注释简图不能替代文字分析。图表只有在显著提升理解时使用，并写全名称、关系含义、证据来源和图例。

## 仓库结构

```text
.
├── .github/workflows/       # 自动校验与版本标签
├── agents/                  # GPT/Codex 界面元数据
├── assets/                  # 图标、吉祥物与 5 张 Canvas
├── references/              # 本体、协议、配方、来源、扩展与 Schema
├── scripts/                 # 确定性结构校验与轻量 Endoscope 控制器
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
- 实验扩展：Endoscope/Bloodtesting、八卦耦合矩阵、多重归一化诊断等；
- 机器约束：项目清单、配方、验收用例与全部 Schema。

所有模块路径都登记在 [`project-manifest.yaml`](references/project-manifest.yaml)，校验脚本会检查断链、孤儿文件、YAML、Canvas、配方顺序、版本生命周期与验收用例结构。

## 版本与成熟度

- 项目版本只有一个，读取 `project.version`。
- 模块版本是独立演进号，不代表整个项目版本。
- `stable` 表示已进入冻结运行链；`experimental` 表示接口已登记但仍需证据或使用经验。
- 新方案先进入迁移或实验层，不直接覆盖冻结本体。
- 每次默认分支发布必须先通过自动校验；相同版本不得指向两个不同提交。

## 资产与授权

阿比盖尔是为本项目创作的 AI 辅助原创角色资产，来源于项目所有者提供的角色设定与参考，不是第三方素材。其使用受本仓库 [`LICENSE`](LICENSE) 约束。

本仓库当前保留所有权利。公开可见不等于授权复制、修改、分发或再许可；如需开放复用，将由项目所有者另行选择并发布明确的开源协议。

## 维护

提交前运行：

```bash
python3 scripts/validate_bundle.py
```

确定性校验只检查结构与可执行约束，不宣称理解语义。涉及本体、交付行为或复杂任务流程的修改，还必须做独立前向测试。详细规则见 [`CONTRIBUTING.md`](CONTRIBUTING.md)。
