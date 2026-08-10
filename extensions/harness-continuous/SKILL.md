# Harness 持续工作流扩展

> 模块: extension-harness-continuous
> 版本: 0.1.0 (experimental)
> 来源: 2026-08-10 workflow/continuous 分支
> 定位: 让 sanyuan 仓库成为跨 agent 的持续工作流——规则层常驻、深度管线按需展开。

---

## 一、解决的问题

**Skill 多轮丢失**: `consciousness-bus` 是单次上下文注入，长对话经 compaction 后指令被压缩，协议不再被遵守。
本扩展用跨 agent 的机制（常驻规则文件 + 磁盘状态 + MCP/脚本）把规则层固定住，不依赖任何一家 agent 的专属注入。

## 二、核心机制：三通道

1. **规则层常驻**：根 `AGENTS.md`（Claude Code / Codex / Gemini CLI / Hermes 等通用读取）。
   每个会话/任务开始时读取 `reference/flow/active-state.json` 确定当前模式。
2. **磁盘状态机**：`scripts/harness_state.py` 维护 `armed → deep|direct`，状态落盘在
   `reference/flow/active-state.json`，对话压缩不丢。
3. **按需能力**：
   - MCP 服务器 `extensions/harness-continuous/mcp/server.py`（stdio，多 agent 通用）暴露
     `mode_status` / `set_mode` / `run_pipeline` / `probe_source`；
   - 批量审计用 `scripts/harness_audit.sh <file...>`（bash + python3 stdlib，任何 agent 可直接跑）。

## 三、激活协议

1. 会话/任务开始：读状态文件确认模式（默认 `armed`）。
2. 首个实质任务：列模式并询问"要进入深度模式吗？"；未确认不展开。
3. 确认后 `python3 scripts/harness_state.py set --mode deep` 落盘，再加载对应 `references/` 模块。
4. 简单问题直接答，保持 `armed`/`direct`，不展开总线。

## 四、每轮自动注入（可选，agent 专属）

默认是"按需读取"，任何 agent 都能用。若要每轮强制注入一行，可在各自 harness 配置把
`python3 scripts/harness_state.py inject` 挂到"每轮开始"：
- Claude Code：`.claude/settings.json` 的 UserPromptSubmit hook（本仓库不提交该文件，各用户自配）
- 其他 agent：等价于各自"每轮开始"回调里跑同一命令

## 五、与 sanyuan 的关系

| sanyuan 模块 | 本扩展的对应 |
|--------------|-------------|
| task-boundary-compiler | armed/direct 门控 = 任务边界先行于任何管线 |
| meta/hu-normalization | deep 模式才展开的归一化管线 = 深度按需 |
| extension-endoscopic-code-actuation | 批量 probe = 代码干预的规模化入口 |
| condense-protocol | snapshot/persist = 压缩前保存状态 |

## 六、触发条件

- 在 sanyuan 仓库内使用任何 agent，需要跨多轮保持协议
- 需要批量审计代码风险、或把仓库当长期工作流持续调用

## 七、边界（不做的事）

- 不替代 `SKILL.md` 主流程，只负责"规则常驻 + 深度按需"
- 不修改冻结本体 / `references/architecture.md`
- 不改变 `scripts/endoscope.py` 的确定性协议，只是批量化调用它
