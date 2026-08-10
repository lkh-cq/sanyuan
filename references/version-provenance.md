# 版本来源与迁移

## 当前基线

- 项目：意识总线 / 三元三才
- 运行基线：读取 `project-manifest.yaml#project.version`
- 日期：2026-07-27
- Skill 封装日期：2026-07-30
- 激活原则：任务边界优先；元信息空间与互信息空间独立编码、独立归一化；跨空间一致性后再进入藏归与 ρ/θ 总线。

## 输入包指纹

| 输入 | SHA-256 | 角色 |
| --- | --- | --- |
| `意识总线_总项目_v3.1.0(2).zip` | `9ee15870249931f07630ab0dd761703138e75115225b2ff6e174a733efb6f600` | 工程基线与旧正式模块 |
| `意识总线_总项目_v3.2.0skill.zip` | `55965fa9a4322b82697a234ea0a62f4e9b4da5bcd4f09c7ebaf802703cb925e8` | 当前权威内容基线 |
| `多版本Skill功能验证与对比.zip` | `32629328ed4dfce0b40094f77fb9ee3950a8a3a56ab0c375a9ccf9c5ff425524` | deep-conscious 多版本模拟与对照材料 |

## V3.1.0 → V3.2.0

1. 在所有过滤前新增任务边界 `B_T`。
2. 将单一 SVD 多重归一化迁入历史层，激活元归一化 `M_T` 与互归一化 `H_T`。
3. 将“互”冻结为独立关系观测空间，保持 `FlowEvent ⊂ 互`。
4. 新增直接互、复合互、路径残差、MutualNode 与跨空间一致性检查。
5. 保留 ρ收束、θ切换、缓存波和 n位聚焦的既有数学职责。

## Skill 工程化调整

1. 仅在顶层 `SKILL.md` 使用 Skill 触发元数据；原子模块改为按需读取的 references，避免多个嵌套 Skill 无法自动路由。
2. 将项目规范存入只读 `references/`；保留任务运行时 `reference/`，不改变藏归协议。
3. 排除旧 ZIP、编码损坏文件、重复版本和静态审计报告，避免它们进入运行上下文。
4. 保留五张正式 Canvas 作为资产。
5. 新增实时验证脚本和行为验收用例，替代静态“PASS”文本。

## 已修复的不一致

- 将根加载链中的“多重归一化过滤”修正为“任务边界 → 元/互独立归一化 → 跨空间一致性”。
- 将根文档尾部版本从 3.1.0 修正为 3.2.0。
- 删除测试报告中“互=FlowEvent PASS”的错误断言，以 `FlowEvent ⊂ 互` 为唯一正式关系。
- 删除未随 Skill 分发的 archive 路径，保留本文件中的迁移指纹。

## 2026-08-03 读者端交付修订

本次为非本体修订，V3.2.0 的三才、三题、互、FlowEvent、ρ/θ 与 n位聚焦定义不变。

1. 将节点、边、关系代码、YAML 账本和 `B_T/M_T/H_T/Z_T` 明确限定为内部工作表示。
2. 新增读者端分析交付规范，要求文献拓扑转译为段落级自然语言。
3. 把科研配方的“内部结果合成”与“读者端转译”拆成连续但独立的步骤。
4. 默认隐藏内部审计结构；仅在用户明确要求时，于主要结果之后追加独立审计块。
5. 新增行为验收项，禁止无注释简图、裸箭头和内部简写替代正式分析。

## 2026-08-03 首次公开发布硬化

本次仍属于 V3.2.0 首次标签发布前的基线修复，不改变冻结本体。

1. 以 `project-manifest.yaml#project.version` 作为唯一项目版本源，模块版本单独登记生命周期。
2. 移除校验脚本中的项目版本、测试数量和测试 ID 硬编码；确定性校验只负责结构，不冒充语义验证。
3. 将冻结本体与职责分离表收敛到 `architecture.md`，入口和 README 只保留导航。
4. 恢复唐朝花瓶、时空地理人文信号与“只记录联系”的用户原话锚点。
5. 从原始《三元道辩体系》文档生成八卷二十八章浓缩来源，并显式保留证据边界。
6. 新增耦合态写入封套与 Schema，保持 StoreNode、ReadNode、MutualNode 分离。
7. 新增实验性八卦六十四态矩阵接口；无数据转移保持未知。
8. 恢复 13 条反例免疫清单，删除 `condense-protocol.md` 的孤立作者字段。
9. 增加权利声明、提交规范、自动校验和不可移动版本标签流程。
10. 收敛 `agents/openai.yaml`，删除未经验证的平台产品声明。

## 2026-08-03 V3.2.1 安装上下文兼容修订

本次为安装兼容性补丁，不改变冻结本体或运行配方。

1. 仓库发布上下文继续禁止手工声明未经验证的产品支持。
2. GPT 安装上下文允许平台协调器向 `agents/openai.yaml` 写入平台管理的产品字段。
3. 确定性校验继续覆盖运行文件；平台生成的展示元数据不作为本体或能力证据。

## 2026-08-07 V3.2.2 过程透明实验扩展

本次登记 `process-transparency` 实验模块，不修改冻结本体。

1. 探索性任务采用“结论—证据—假设—验证”四字段决策日志，降低事后自圆其说污染。
2. 同一决策点反复翻转时逐级预警并允许冻结当前决策。
3. 该扩展与元/互归一化、archive-ingestion 互补，但不替代 ρ/θ 或冻结本体。

## 2026-08-08 V3.2.3 Endoscope 全链路实验实现

本次将 Endoscope 从单一代码风险脚本升级为三元归一化阴影驱动的实验运行时，不修改 `references/architecture.md`。

1. Endoscope 模块升级至 0.2.0，完整链路为 `B_T → TaskProfile → M/H normalization → NSL → Probe/Event → minimal revival → E/S/O → BloodRecord → calibration candidate`。
2. 正式复用元/互归一化的 `omitted_features + recovery_refs` 生成 Normalization Shadow Ledger；不把旧 SVD 低方差方向复活为门控依据，也不复制第二份完整上下文。
3. 新增 11 类任务 TaskProfile；Probe 从属于任务场景，TaskProfile watch 只能加权已经由事件/关系证据命中的 shadow，不能单独触发复活。
4. Python 3.10+ 标准库作为控制面；base R 零包依赖 adapter 负责 `parse()` 与低成本 R 静态信号。R/Tree-sitter/LSP/torch/C++ 均为可选增强，缺失时必须显式降级。
5. Execution / State / Output 三闸门独立；解释污染可以继续安全诊断而阻断最终输出，不可逆副作用必须 `PAUSE_BEFORE_SIDE_EFFECT + NO_TOUCH`。
6. 新增 NSL/Event/Gate/Profile/BloodRecord JSON Schema，以及 12 组 Bloodtesting 夹具（包含 PDE 截断污染与 Lasso 支持集替代）。
7. Bloodtesting 校准只生成 candidate 状态，固定 `auto_promote=false`；禁止自动写回 ρ、模型权重或稳定策略，必须经过 shadow replay、A/B 与显式 promotion。
8. Endoscope 与 `process-transparency` 互补：Observation Event 可作为决策日志 evidence，推断必须保留在 assumption 层。
9. GitHub CI 增加 Python Endoscope 验证和独立 base R adapter 自测；只有两者与 bundle validator 都通过才允许默认分支发布标签。

## 对验证材料的解释边界

多版本对比包是固定随机种子下的模拟测试，可用于比较 deep-conscious v2.1 与 v3.0 的工程表达、覆盖度和稳定性；它不是对意识理论、认知机制或外部任务有效性的实证证明。

Endoscope 的 Bloodtesting 夹具同样只是协议校准起点，不是通用 coding benchmark。工程自测通过只证明合同与参考实现自洽；真实 Agent 上的误报、漏报、首次出血、错误传播、恢复效率和 output 节省必须由前向运行数据支持。

## 2026-08-10 Obsidian 长期集成分支

本次在独立 `integration/obsidian` 分支登记实验性检索适配器，不修改冻结本体，也不把分支状态作为默认分支正式发布。

1. Python 核心提供 SQLite FTS5、可选 Doubao/Ark embeddings、sidecar 自有向量表、严格 G1/G2/G3 检索级联与透明启发式重排。
2. REST sidecar 默认只绑定回环地址；API 密钥保留在 Python 进程环境，Obsidian 插件不保存 embedding 凭据。
3. 插件是可独立迁移的 TypeScript 源包，不加载时联网、不后台扫描 Vault，只在显式命令中发送查询、当前路径与可选 `sanyuan_axes`。
4. S5 生成临时 ReadProjection；缺少 MutualNode 时保持 `incomplete`，不得伪装成 Schema 完整的 CouplingState。
5. 注入格式服从当前 `read-injection.md`，不复活把地题画成固有输出方向的旧式箭头表达。
6. 路由只使用离线预计算表的 O(1) 精确查找；缺少路由表、解析器或 query axes 时显式降级，不在调用路径运行最短路搜索。

## 2026-08-10 workflow/continuous 分支

本次在 `workflow/continuous` 分支登记 `harness-continuous` 实验模块，把 sanyuan 仓库改造为跨 agent 的持续工作流；不修改冻结本体，也不以分支状态作为默认分支正式发布。

1. 根级 `AGENTS.md` 作为跨 agent 常驻前门（Claude Code / Codex / Gemini CLI / Hermes 通用读取），替代对单次 skill 注入的依赖；不另建 `CLAUDE.md` 专属副本。
2. 状态机 `scripts/harness_state.py` 维护 `armed → deep|direct`，状态落盘于运行时 `reference/flow/active-state.json`（`.gitignore` 忽略，不提交），对话压缩不丢。
3. 批量审计 `scripts/harness_audit.sh` 对文件列表逐个跑 `endoscope.py probe`（只读）并合成按闸门严重度排序的 JSON 报告；只依赖 bash + python3 stdlib。
4. MCP 适配器 `extensions/harness-continuous/mcp/server.py`（stdio）暴露 `mode_status` / `set_mode` / `run_pipeline` / `probe_source`；MCP 为多 agent 通用协议，`mcp` 包是仓库首次引入的外部依赖，仅限该适配器。
5. 本扩展只负责"规则常驻 + 深度按需"，不替代 SKILL.md 主流程，不改变 endoscope.py 的确定性协议，不写回 ρ、权重或稳定策略。
