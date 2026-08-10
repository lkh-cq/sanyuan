# sanyuan · 持续工作流（AGENTS.md）

本仓库是 `consciousness-bus` 技能仓库，也是**跨 agent 的持续工作流**：规则层常驻、深度管线按需展开。
本文档对所有 agent 生效（Claude Code / Codex / Gemini CLI / Hermes 等通用读取，作为 `CLAUDE.md` 的可移植替代）。
项目完整协议见 `SKILL.md`；冻结本体与职责边界以 `references/architecture.md` 为权威。

## 每轮开始时

读取 `reference/flow/active-state.json` 确定当前模式（`armed`|`deep`|`direct`；文件不存在则视为 `armed`）。
状态由 `scripts/harness_state.py` 维护，会话中以其为权威，不要凭记忆推断模式。

## 模式选择

| 模式 | 何时用 | 加载入口 |
| --- | --- | --- |
| 直接 | 单步问答、无需跨材料保持结构 | 不展开总线 |
| 快筛 | 筛选/比较，任务边界清楚 | `references/fast-filter-recipe.yaml` |
| 深度 | 多材料、多阶段、长任务 | `references/research-recipe.yaml` |
| 代码干预 | 代码存在归一化损失/外部写入风险 | `references/endoscopic-code-actuation.md` |
| Obsidian | 检索/注入集成的实现、测试、维护 | `integrations/obsidian/README.md` |
| 持续工作流 | 跨 agent/多轮保持协议，或批量审计代码风险 | [harness-continuous](extensions/harness-continuous/SKILL.md) |

## 激活协议

1. 首个实质任务先列模式并询问"要进入深度模式吗？"，**未确认不展开完整管线**。
2. 确认后执行 `python3 scripts/harness_state.py set --mode deep` 落盘，再加载对应 `references/` 模块。
3. 简单问题直接回答，保持 `armed`/`direct`，不展开总线（遵守 SKILL.md 纪律）。

## 硬规则（每轮生效）

- 启发式风险分数、排序 ≠ ρ/θ/证据强度；禁止重命名伪装为概率或 ρ。
- 降级必须显式；缺少可计算输入时用定性状态或区间，不伪造精确数值。
- 读者端交付用自然语言，不暴露内部节点、边、关系代码、裸箭头或 YAML 账本（反例免疫 #12）。
- 不修改 `references/architecture.md`（冻结本体）、`agents/openai.yaml`；版本只读 `project-manifest.yaml#project.version`。
- 修改任何模块路径、配方或 Schema 后运行 `python3 scripts/validate_bundle.py` 及相关校验。

## 常用命令

- 模式状态机：`python3 scripts/harness_state.py start|inject|show|snapshot|persist`；`set --mode deep|direct|armed`
- 单文件只读探针：`python3 scripts/endoscope.py probe <path>`
- 完整管线：`python3 scripts/endoscope.py pipeline --task-family <family> --source <path>`
- 批量审计：`bash scripts/harness_audit.sh <file...>`

## MCP

本仓库提供 MCP 服务器 `extensions/harness-continuous/mcp/server.py`（stdio，多 agent 通用），
暴露 `mode_status` / `set_mode` / `run_pipeline` / `probe_source` 四个工具。
支持 MCP 的 agent 可自行注册（`.mcp.json` 为 Claude Code / Codex 通用格式）；注册与使用见
[harness-continuous](extensions/harness-continuous/SKILL.md)。
