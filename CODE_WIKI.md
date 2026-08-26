# 意识总线（三元三才）Code Wiki

> 本文档是对本仓库的工程化代码 Wiki 说明，覆盖整体架构、模块职责、关键类与函数、依赖关系与运行方式。
> 定位说明：本仓库以「认知预处理协议 + 文档规范 + 确定性校验脚本」为主，不是传统应用型代码仓库；代码集中在 `scripts/`、`extensions/*/scripts/` 与 `integrations/`。

## 0. 文档说明与事实记录

- **分析日期**：2026-08-26（Asia/Shanghai）
- **仓库基线**：`main` 分支，最近合并 `extension-sanyuan-router 运行时链路总控`
- **项目版本**：以 [references/project-manifest.yaml](file:///workspace/references/project-manifest.yaml) 的 `project.version` 为**唯一版本源**；本 Wiki 按仓库规则**不内联具体版本号**（`scripts/validate_bundle.py` 禁止项目版本号出现在 manifest/provenance 之外）。
- **运行验证**：本文档所述 4 个 Python 校验命令已在沙箱实际执行并通过（详见 §7 运行记录）。

---

## 1. 项目概览

### 1.1 它是什么

意识总线（三元三才）是一个面向**复杂科研、知识整理、项目规划与长上下文任务**的认知预处理协议与 Skill 包。它不声称是现实机制、证明系统或通用 Agent，而是：

> 先限定任务边界（`B_T`），再分离内容（元信息空间 `M`）与关系（互信息空间 `H`），最后把内部结构转译为读者可以直接理解的结果。

### 1.2 核心本体（冻结，唯一权威源）

冻结本体只维护在 [references/architecture.md](file:///workspace/references/architecture.md)，其余文件不得另建副本：

| 概念 | 含义 |
| --- | --- |
| 三才（藏） | 天才=规律 / 地才=环境 / 人才=实践 |
| 三题（归） | 天题=信息的本来样貌 / 地题=读取方式 / 人题=读取记录 |
| 藏 vs 归 | 藏=信息储存（保存具体内容）；归=信息流通（形成抽象规律） |
| 天地人拓扑 | 天 ↔ 地 ↔ 人；地管信息流与止，不携带固有方向 |
| 互 | 独立关系观测空间，`FlowEvent ⊂ 互`，**不是**第四个本体实体 |
| ρ / θ | `ρ + θ = 1`；ρ 管收束、θ 管切换；不是正确率/错误率 |
| n 位聚焦 | 离线/深睡重建路由，调用时 O(1) 查表 |
| 耦合态 | 连接 StoreNode 与 MutualNode 的检索/写入事务封套 |

### 1.3 权威层级

1. 用户最新明确表述 → 2. `architecture.md` 冻结本体 → 3. `project-manifest.yaml` 登记 → 4. 当前激活模块 → 5. 历史 Skill/Canvas/归档 → 6. Agent 推断。

---

## 2. 整体架构

### 2.1 分层架构

```text
来源层
├── 用户原话锚点 (original-anchors.md)
└── 历史理论来源 (sanyuan-daobian-framework.md, 八卷二十八章浓缩)

预处理层
├── 任务边界 B_T (task-boundary.md)
├── 三思而后行 (think-before-responding.md)
├── 子任务拆分 (task-decomposition.md)
└── 元/互独立归一化 (meta-normalization.md / hu-normalization.md)

观测与藏归层
├── 元信息空间 M：三才藏 → StoreNode
├── 互信息空间 H：MutualNode / FlowEvent
├── 三题归：ReadNode
└── 耦合态 CouplingState：连接内容与关系的检索/写入事务

控制层
├── ρ 收束 (rho-convergence.md)
├── θ 切换 (theta-switching.md)
├── n 位聚焦 (n-focus.md)
└── 缓存波与压缩 (cache-wave.md / condense-protocol.md)

交付层
├── 内部结果：保留节点/关系/路径/证据压力/缺口
└── 读者结果：自然语言段落 (reader-facing-analysis.md / output-contract.md)
```

### 2.2 两条执行链

- **科研深度分析**（[research-recipe.yaml](file:///workspace/references/research-recipe.yaml)）：`冻结输入 → 任务边界 → 独立研判 → 子任务拆分 → M/H 独立编码与归一化 → 跨空间一致性 → 藏归与耦合态登记 → n 位聚焦 → ρ 收束 → θ 边界检查 → 内部合成 → 读者端转译 → 缓存波更新`（16 步，含功能贞验与耦合态登记）。
- **快速信息筛选**（[fast-filter-recipe.yaml](file:///workspace/references/fast-filter-recipe.yaml)）：`简化边界 → 最小 M/H 提取 → 快速掩码匹配 → ρ/θ 控制 → 低成本功能检查 → 缓存波更新`。约束：**不得把元或互降为零**，只允许降低轴数与关系深度。

### 2.3 仓库目录结构

```text
/workspace
├── .github/workflows/validate.yml   # CI：4 个校验 job + 自动版本标签 + 清理 agent 分支
├── agents/openai.yaml               # GPT/Codex 界面元数据（display_name、default_prompt）
├── assets/                          # 吉祥物阿比盖尔、Agent 图标、5 张 Canvas
├── extensions/                      # 可选子模块（4 个，各含 SKILL.md + scripts/）
│   ├── process-transparency/        #   过程透明：决策日志四字段 + archive_wsl.sh
│   ├── index-naming/                #   index 命名规范 v2.0 + validate_index_naming.py
│   ├── sanyuan-router/              #   运行时链路总控 + router_health.py
│   └── systematic-retrieval/        #   系统化检索分支 + validate_retrieval_spec.py
├── integrations/obsidian/           # Obsidian 插件(main.js) + Python sidecar 元数据/env
├── references/                      # 只读规范层：本体/协议/配方/来源/扩展/Schema（80+ 文件）
├── scripts/                         # Python/R 参考实现与确定性校验
│   ├── endoscope.py                 #   Endoscope 0.2 参考控制器（747 行，stdlib only）
│   ├── endoscope_r.R                #   base R 适配器（137 行，零包）
│   ├── multiscale_reinjection.py    #   多时间尺度再注入参考运行核（307 行）
│   └── validate_*.py                #   3 个确定性校验器
├── CONTRIBUTING.md                  # 提交/评审/发布规范
├── LICENSE                          # All rights reserved (lkh-cq, 2026)
├── README.md                        # 人类读者入口
└── SKILL.md                         # Skill 运行入口（选择运行强度 + 主流程 12 步）
```

> 命名空间约定：`references/` = 本 Skill 随附的**只读规范**；`reference/` = 任务运行时状态根目录（`source/ store/ read/ flow/ routing/`），仅在用户要求持久化且允许写入时创建。

---

## 3. 主要模块职责

模块登记、路径与生命周期均以 [project-manifest.yaml](file:///workspace/references/project-manifest.yaml) 为唯一事实源。生命周期：`frozen`（冻结本体，1 个）→ `stable`（运行链，16 个）→ `experimental`（接口已登记，9 个）→ `source`（来源，2 个）。

### 3.1 核心层（stable）

| 模块 (module_id) | 版本 | 职责 |
| --- | --- | --- |
| core-rho-convergence（ρ收束） | 3.0.0 | 注意力收束引擎，`ρ=ρ_raw/(1+θ'/θ_critical)`，维护 ⌘ 注意力向量库，管「在当前边界内往哪走」 |
| core-theta-switching（θ切换） | 1.4.0 | 场景边界失效检测，θ 触发决策矩阵（<0.15 继续 / 0.15-0.30 裂隙 / 0.30-0.50 重识别 / ≥0.50 强制切换），只喊「该走了」不指路 |
| core-deep-conscious（n位聚焦） | 3.0.0 | 工作集约束到 `b_n` 位；离线 Dijkstra 建路由表，调用时 O(1) 查表；gated-cascade 门控丢弃被拒项 |
| core-cache-wave-dynamics（缓存波） | 1.0.0 | 底层理论层：涨潮(Ω=1)/退潮(∇E超阈)/深睡(dθ'/dt 加速) 三相位；`θ'` 跨上下文残留单调不减；H≠Ω 虚假信心差 |
| core-condense-protocol（condense） | 0.2.0 | 压缩前注意力保存协议：五步提取活跃向量/张力对/已推翻/锚点(≤10)，以 `[ATTENTION CONDENSE]` 打包 |

### 3.2 预处理层（stable）

| 模块 | 版本 | 职责 |
| --- | --- | --- |
| preprocessor-task-boundary | 0.1.0 | 编译 `B_T={task_goal, F_T, forbidden_loss, epsilon_T, required_spaces, optional_spaces, meta_axes, hu_axes}`；路由门判快速/科研配方 |
| preprocessor-meta-normalization | 0.1.0 | 元空间（三才层）独立归一化，输出 `M_T`；功能距离约束 `D_f ≤ ε_T`；s_M 连续信号 + q_M 离散路由码 |
| preprocessor-hu-normalization | 0.1.0 | 互空间独立归一化，输出 `H_T`；关系全集（直接/复合/路径残差/流止/转换/反馈/条件/时序）；路径残差强制保护 |
| preprocessor-think-before-responding | 0.3.0 | 三思而后行：输出前先用自身注意力向量独立研判（ρ/θ 必填），检测讨论被对方框架窄化 |
| preprocessor-task-decomposition | 0.3.0 | 复杂任务拆子任务，各自独立 B_T/藏归/ρθ；合成取并集并保留来源链 |

### 3.3 藏归与关系层（stable / 实验）

| 模块 | 版本 | 职责 |
| --- | --- | --- |
| branch-zang-gui（藏归调度器） | 0.3.0 | 只做调度：路由判断→三才藏→FlowEvent→三题归→上下文编译→回写；管理 ID 与路径规范 |
| branch-sancai-store（三才藏） | 0.3.0 | 藏：三才编码保存具体内容，写 StoreNode（`reference/store/{id}.yaml`） |
| branch-santi-read（三题归） | 0.3.0 | 归：三题读取形成抽象规律，写 ReadNode（`reference/read/{id}.yaml`） |
| observation-hu（互信息空间） | 0.1.0 | 定义互空间结构、9+ 轴、MutualNode 基本单元；不执行归一化 |
| zang-gui-cycle / store-write-spec | — | 藏归循环（版本链不覆盖）与耦合态写入封套规范（CouplingState = ≥1 StoreNode + ≥1 MutualNode + 可选 ReadNode） |

### 3.4 分析与交付层（stable）

| 模块 | 版本 | 职责 |
| --- | --- | --- |
| extension-reading-topology | 0.2.0 | 三元语法阅读拓扑（非写作生成器）：observed_topology / evidence_pressure_map / topology_gap_map |
| extension-reader-facing-analysis | 0.1.0 | 内部拓扑 → 自然语言段落（2-4 句论述单元），默认隐藏内部编码 |
| extension-modality-boundary | 0.1.0 | 模态可见性边界：text_topology vs evidence_topology vs claim_evidence_gap |
| validation-framework-pitfalls | 0.1.0 | 13 条反例免疫清单，命中即停止自动迁移 |

### 3.5 实验扩展层（experimental）

| 模块 | 版本 | 职责 |
| --- | --- | --- |
| extension-endoscopic-code-actuation | 0.2.0 | Endoscope/Bloodtesting：TaskProfile→NSL→Probe→minimal revival→E/S/O 三闸门→BloodRecord→calibration |
| extension-multiscale-reinjection-kernel | 0.1.0 | 多时间尺度信号分层 + 循环再注入 + ρ/θ 门控（CONVERGE/REFRAME），最小运行核 `scripts/multiscale_reinjection.py` |
| extension-yijing-coupling-matrix | 0.1.0 | 八卦双坐标 + 64 态转移矩阵（无数据保持 unknown，不填伪权重） |
| extension-multi-norm-diagnosis / frozen-definitions / double-observation-space | 0.1.0 | 多重归一化诊断 / V3.2.0 冻结定义参考 / 元-互双观测空间架构 |
| extension-process-transparency | 0.1.0 | 决策日志四字段（conclusion/evidence/assumption/verification）+ 翻转三级预警 |
| extension-index-naming-norm | 0.1.0 | 知识库 index 命名 v2.0（层级=上游文件夹数、三段式） |
| extension-sanyuan-router | 0.1.0 | Hermes/Obsidian 运行时链路总控（L1-L9 拓扑、事故 runbook） |
| extension-systematic-retrieval | 0.1.0 | 系统化检索分支：三阶段检索（全量拓展→审核→收束）+ 6 步循环 + 7 类盲点 + 4 类来源指南 + RetrievalPlan schema |
| extension-archive-ingestion | 0.1.0 | 归档方案迁移协议（stable 生命周期） |

---

## 4. 关键类与函数说明

### 4.1 `scripts/endoscope.py` — Endoscope 0.2 参考控制器

纯 Python 标准库（`argparse/ast/hashlib/json/re/shutil/subprocess/tempfile/collections/pathlib`）。常量：

- `GATE_EXECUTION` = OPEN / CONTINUE_DIAGNOSTIC / PAUSE_BEFORE_SIDE_EFFECT / STOP
- `GATE_STATE` = OPEN / FILTERED / QUARANTINED / DISCARD
- `GATE_OUTPUT` = OPEN / REVIEW_REQUIRED / BLOCKED / REPLACE
- `COST_RANK` = cheap(0) / medium(1) / expensive(2) / unknown(3)
- `PATTERNS`：11 组正则信号（destructive_write / external_write / dynamic_exec / shell / concurrency / broad_exception / r_global_assign / r_coercion_sensitive / na_sensitive_branch / credential_or_permission）
- `SEVERITY`：信号→严重级（critical/high/medium/info）

关键函数：

| 函数 | 职责 |
| --- | --- |
| `stable_id(prefix, *parts)` | SHA-256 前 12 位生成稳定 ID（`pt_/probe_/sh_/nsl_/evt_`） |
| `load_profiles / compile_profile` | 加载并校验 TaskProfile 注册表（schema_version 须 = 0.2.0），编译带 `profile_id` 的任务画像 |
| `python_ast_observation(text)` | 用 `ast.parse` 提取 imports/definitions/嵌套深度；语法错误返回 parse_error 详情 |
| `regex_findings(text)` | 静态正则信号扫描（source=static-regex） |
| `run_r_adapter(path)` | 探测 `Rscript`，调用 `endoscope_r.R probe`；不可用时返回 None（能力降级） |
| `probe_source(path)` | 核心探针：文件→语言语义观察 + 信号列表 + summary（lines/scope_hint/signal_count/irreversible_write） |
| `normalize_omitted / build_shadow_ledger` | 把归一化快照的 `omitted_features + recovery_refs` 编译为 NSL（Normalization Shadow Ledger） |
| `revive_shadow(ledger, profile, event)` | 按词元命中打分排序 shadow，选最小恢复集合（`rank_is_probability=False`） |
| `gate_decision(S,B,U,D, ...)` | E/S/O 三闸门决策：`R=0.25S+0.35B+0.25U+0.15D`；tainted/irreversible 强制 QUARANTINED/BLOCKED |
| `derive_axes(probe, profile)` | 由 probe 观察与 profile 风险默认值推导 S/B/U/D（0..3） |
| `run_pipeline(...)` | 全链路编排：TaskProfile→probe→NSL→revival→axes→gate→ρ事件→delivery |
| `validate_blood_record / append_blood_record / iter_jsonl / calibrate_records` | Bloodtesting：记录校验/追加 JSONL/校准汇总（**永不自动晋升策略**，`auto_promote=False`） |
| `selftest()` | 确定性自测：profiles/shadow/revival/gates/python_probe/r_probe/blood |
| `main()` | CLI：`profile / probe / shadow-build / revive / gate / pipeline / blood-record / calibrate / selftest` |

### 4.2 `scripts/multiscale_reinjection.py` — 多时间尺度再注入参考核

- **枚举**：`Timescale`(FAST/INTERMEDIATE/SLOW/STATIC)、`Persistence`(TRANSIENT/SESSION/PERSISTENT)、`Scope`(LOCAL/REGIONAL/GLOBAL)、`Fanout`(DENSE/SPARSE/BROADCAST)、`Gate`(CONVERGE/REFRAME)
- **数据类（frozen）**：
  - `Source`(kind/channel/source_ref)
  - `Temporal`(observed_at/timescale/persistence/ttl_ms)
  - `Propagation`(scope/fanout/hop_limit)
  - `SignalEnvelope`：路由头；`__post_init__` 校验必填与区间；`slow_lane` 属性；`fingerprint()` 对路由元数据做 SHA-256（不解引用 payload）
  - `ReinjectionFrame`：frame_id / delta_refs / persistent_refs / revived_refs / rho / theta / gate / active_routes / shadow_refs
- **状态与路由**：
  - `_StoredSignal`(signal/fingerprint)
  - `ReinjectionState`：`ingest()` 仅当新信号或元数据变化返回 True；`persistent_payload_refs()` 只返回引用不重放 payload
  - `MultiTimescaleReinjection`：`orient(rho)` 保 `ρ+θ=1`；`ingest_many()`；`compile_frame()` 由 `θ ≥ reframe_theta` 决定 REFRAME 或 CONVERGE，`revive_ids` 仅 REFRAME 生效
- **函数**：`utc_now()`、`_selftest()`

### 4.3 `scripts/endoscope_r.R` — base R 适配器

- `json_escape / json_scalar / json_value`：base R 最小 JSON 序列化（零依赖）
- `line_signal(lines, pattern, signal, severity, fixed)`：按行 grep 生成信号
- `probe_file(path)`：`parse()` 语法检查 + 8 组 R 信号（r_global_assign / destructive_write / external_write / dynamic_exec / concurrency / r_coercion_sensitive / na_sensitive_branch / environment_mutation）
- `selftest()`：临时文件自测；CLI 支持 `probe FILE` / `selftest`

### 4.4 校验脚本

| 脚本 | 校验内容 |
| --- | --- |
| `validate_bundle.py` | SKILL frontmatter；architecture authority=frozen-ontology；manifest 路径登记与孤儿文件；生命周期一致性；项目版本唯一性；Markdown 链接；research-recipe 步骤序；acceptance-tests 结构；YAML 可解析；agents/openai.yaml；Canvas 文件节点；仓库必需文件 |
| `validate_endoscope.py` | TaskProfile 协议版本与字段；Bloodtesting 夹具与闸门枚举；5 个 Endoscope JSON Schema（2020-12）；调用 `endoscope.py selftest` |
| `validate_multiscale_reinjection.py` | 2 个多尺度 Schema；导入参考运行核并跑 CONVERGE/REFRAME 场景断言 |

### 4.5 扩展脚本

| 脚本 | 职责 |
| --- | --- |
| `extensions/index-naming/scripts/validate_index_naming.py` | index 命名 v2.0 只读校验；`--dry` 输出建议新名；永不写入；退出码 0/1/2 |
| `extensions/sanyuan-router/scripts/router_health.py` | L1-L9 全链路健康检查：三桥 stdio 握手（initialize→tools/list）、8765 sidecar、路由派生新鲜度、DB/插件存在性 |
| `extensions/process-transparency/scripts/archive_wsl.sh` | 两阶段归档：WSL 侧先 tar 原地压缩 → 再 mv 到 D 盘；`now` / `status` 子命令 |
| `extensions/systematic-retrieval/scripts/validate_retrieval_spec.py` | 检索协议结构校验（3 阶段/6 步循环/7 盲点/4 来源）；`--plan FILE` 校验运行时 RetrievalPlan；只读；退出码 0/1/2 |

### 4.6 Obsidian 集成（`integrations/obsidian/`）

- `plugin/main.js`（399 行，esbuild 打包产物）：`SanyuanContextRouter` 插件；`SanyuanClient` 客户端（loopback/远程白名单检查、Bearer token、JSON 请求到 sidecar `:8765`）。源为 `src/main.ts` + `src/client.ts`。
- `python/`：包名 `sanyuan-obsidian`（v0.1.0），console_script `sanyuan-obsidian = sanyuan_obsidian.__main__:main`；定位 SQLite FTS5 检索 + 可选 embedding/rerank + 读取投影 + REST API（stdlib-only）。**仓库内仅保留 egg-info 元数据与 `sidecar.env`，Python 源不在本仓库**（`sidecar.env` 配置 SiliconFlow `bge-large-zh-v1.5` embedding 与 `bge-reranker-v2-m3` rerank、端口 8765、DB `obsidian-memory.db`）。

---

## 5. 依赖关系

### 5.1 模块依赖图（来自 manifest）

```text
conscious-rho (ρ)
├── unconscious-theta (θ)  depends_on: conscious-rho
├── deep-conscious (n位)   depends_on: conscious-rho, unconscious-theta, cache-wave
├── think-before-responding depends_on: conscious-rho, unconscious-theta
└── cache-wave (底层三相位)

task-boundary-compiler (B_T)
├── meta-normalization     depends_on: task-boundary-compiler
├── hu-normalization       depends_on: task-boundary-compiler
├── endoscopic-code-actuation depends_on: conscious-rho, task-boundary-compiler,
│                                        meta-normalization, hu-normalization (+可选 process-transparency)
└── multiscale-reinjection-kernel depends_on: conscious-rho, unconscious-theta,
                                             task-boundary-compiler, meta-normalization, hu-normalization

reading-topology ← reader-facing-analysis depends_on: reading-topology
archive-ingestion ← process-transparency / index-naming / sanyuan-router
                    (三者均 depends_on: archive-ingestion)
```

### 5.2 外部运行时依赖

| 依赖 | 用途 | 必需性 |
| --- | --- | --- |
| Python 3.10+（stdlib） | `endoscope.py` / `multiscale_reinjection.py` | **必需**（无第三方依赖） |
| PyYAML | `validate_bundle.py` / `validate_endoscope.py` 读取 YAML | **校验必需**（CI 用 `pip install PyYAML`） |
| R（base R，`Rscript`） | `endoscope_r.R` 适配器 | **可选**：缺失时 Python 控制器显式报告降级（`r_probe: PASS:fallback`），不中断控制链 |
| Obsidian（插件 API） | `integrations/obsidian/plugin/main.js` | 可选集成 |
| SiliconFlow API / obsidian-memory DB | sidecar embedding/rerank 与 FTS5 检索 | 可选集成（`sidecar.env` 配置） |
| Hermes MCP 环境（mcp1x-venv） | sanyuan-router 巡检 L1-L3 桥 | 可选（依赖外部 `~/.hermes` 部署） |

> 明确**非**硬依赖（未来可选增强）：Tree-sitter、LSP、`data.table`、`igraph`、`torch`、C++ 后端。

### 5.3 只读/运行时目录约定

- `references/` = 只读规范（Skill 随附），`reference/` = 任务运行时状态。二者不可混淆（PITFALL）。
- 归档 `reference/` 运行时默认不进入 Git 包（manifest `archive.runtime_included: false`）。

---

## 6. 项目运行方式

### 6.1 一键维护校验（提交前必跑）

```bash
# 需要 PyYAML（首次）
python3 -m pip install --disable-pip-version-check PyYAML

python3 scripts/validate_bundle.py
python3 scripts/validate_endoscope.py
python3 scripts/endoscope.py selftest
# 有 R 环境时：
Rscript scripts/endoscope_r.R selftest
python3 scripts/validate_multiscale_reinjection.py
```

### 6.2 Endoscope CLI 用法

```bash
python3 scripts/endoscope.py profile <task_family>          # 编译 TaskProfile
python3 scripts/endoscope.py probe <file.py|file.R>         # 只读探针（不改文件）
python3 scripts/endoscope.py shadow-build <snapshot.json>   # 由归一化快照编译 NSL
python3 scripts/endoscope.py revive <ledger.json> \
    --task-family <family> --event-json '{"signals":[...]}' # 最小恢复候选
python3 scripts/endoscope.py gate \
    --scope 1 --blast 1 --uncertainty 1 --dependency 1      # E/S/O 三闸门
python3 scripts/endoscope.py pipeline --task-family <family> \
    --source <file> --snapshot <snapshot.json>              # 全链路
python3 scripts/endoscope.py blood-record <record.json> --append <records.jsonl>
python3 scripts/endoscope.py calibrate <records.jsonl>      # 只出候选，不自动晋升
```

退出码：`0`=成功，`2`=可预期错误（输出 `{"status":"ERROR","error":...}`）。

### 6.3 扩展脚本

```bash
# index 命名规范 v2.0 校验（--dry 只读预览建议新名）
python3 extensions/index-naming/scripts/validate_index_naming.py --dry <知识库根目录>

# sanyuan-router 链路巡检（退出码 0=全绿 / 1=有 FAIL）
python3 extensions/sanyuan-router/scripts/router_health.py

# systematic-retrieval 检索协议/计划校验（退出码 0/1/2）
python3 extensions/systematic-retrieval/scripts/validate_retrieval_spec.py
python3 extensions/systematic-retrieval/scripts/validate_retrieval_spec.py --plan <plan.yaml>

# 过程透明归档（WSL→压缩→D盘）
bash extensions/process-transparency/scripts/archive_wsl.sh now|status
```

### 6.4 CI（`.github/workflows/validate.yml`）

- `validate` job（Python 3.12 + PyYAML）：跑 4 个 Python 校验。
- `endoscope-r` job（r-lib/setup-r）：`Rscript scripts/endoscope_r.R selftest`。
- `tag` job（仅 main push）：读取 `project.version` 创建不可移动 `v<version>` 标签；标签已指向其他提交则发布失败。
- `cleanup-merged-agent-branches`：清理已合并的 `agent/*` 分支。

### 6.5 贡献与版本发布

- Conventional Commits；一个提交一个意图；提交前跑 §6.1。
- 版本唯一源 = `references/project-manifest.yaml#project.version`；模块版本独立演进。
- 冻结本体只改 `architecture.md` 并同步清单/来源/Schema/配方/验收。

---

## 7. 运行验证记录（2026-08-26，沙箱实测）

| 命令 | 结果 |
| --- | --- |
| `python3 scripts/validate_bundle.py` | PASS（需先 `pip install PyYAML`） |
| `python3 scripts/validate_endoscope.py` | PASS |
| `python3 scripts/endoscope.py selftest` | PASS（`r_probe: PASS:fallback`，沙箱无 R，符合降级设计） |
| `python3 scripts/validate_multiscale_reinjection.py` | PASS |

---

## 8. 补充阅读索引

- 入门：[README.md](file:///workspace/README.md) → [SKILL.md](file:///workspace/SKILL.md) → [architecture.md](file:///workspace/references/architecture.md)
- 机器约束：[project-manifest.yaml](file:///workspace/references/project-manifest.yaml)（模块/版本/路径/Schema 登记）、[acceptance-tests.yaml](file:///workspace/references/acceptance-tests.yaml)（16 个行为验收用例）、[output-contract.md](file:///workspace/references/output-contract.md)
- 版本历史：[version-provenance.md](file:///workspace/references/version-provenance.md)
- 反例免疫：[framework-pitfalls.md](file:///workspace/references/framework-pitfalls.md)
- 实验链路：[endoscopic-code-actuation.md](file:///workspace/references/endoscopic-code-actuation.md)、[endoscope-task-profiles.json](file:///workspace/references/endoscope-task-profiles.json)、[endoscope-bloodtesting.yaml](file:///workspace/references/endoscope-bloodtesting.yaml)、[multiscale-reinjection-kernel.md](file:///workspace/references/multiscale-reinjection-kernel.md)
