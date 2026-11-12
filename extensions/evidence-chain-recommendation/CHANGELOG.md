# CHANGELOG · ECR

## v1.2 — 2026-11-12（O9 收敛度：把"每轮更进一步"变成单调函数）

**性质**：加一层**跨轮判据**。v1.1 解决了"单轮内能算的都算完"，v1.2 解决"两轮之间凭什么说更近了"。

### 出发点
磨合期不要求一次命中。要求的是：**每掷一次都必须离错误目标更远，或者至少不更近**；反过来看（离错误越远越好）才是可被机器语言计算的单调函数。

### 新增 `scripts/ecr_o9.py`
- `D = Σ w_i·e_i`，8 个错误分量全部回指 plan 字段（缺口 3.0 / 单源 2.0 / 拒载 1.5 / 未核 1.0 / 门位缺 1.0 / 无佐证 0.5 / 尺度不可判 0.5 / 预算低效 0.5）；
- `D_rel = D / D_max(k)`，仅同 `k` 内可比；
- `--prev-plan` 触发跨轮对比：`delta` / `components_delta` / `monotone` / `verdict ∈ {improved, flat, regressed}`，退步必须点名 `regressed_by`；
- 权重是**声明**不是拟合；`D` 的下降可归因到具体分量，因此是阳性依赖的判据。

### 验收
- `selftest` **4/4 → 5/5**（新增 `t5_convergence_o9`：improved / regressed / flat 三态 + 自比必须 flat）；
- 实例首轮：`D=11.5`、`D_max=39.5`、`D_rel=0.291139`，分量 `{gap:1, single_source:2, gate_missing:1, no_corroboration:5, scale_mismatch:1, budget_underuse:1}`；
- 同输入二次运行（以首轮为 `prev`）：`ΔD=0.0`、`verdict=flat`、`monotone=True` —— 无变化不会被记成进步。

### 该版本的主张边界
`D` 是**错误侧距离**，不是正确率。它不能证明结论为真，只能证明"这一轮比上一轮少了几类可枚举的错"。把它当评分跨命题比较，违反红线 19。

## v1.1 — 2026-11-12（O8 从"人判"改为算子）

**性质**：修 v1.0 的一处结构性错误——把机器能算的量标成了"人工复核"，等于交付一个未完成的状态机。

### 问题
v1.0 的 O8 只写了三条纪律（扣度数边际、配置模型、E<5 禁报），校验栏写"人工复核"。但这三条**全部可机械执行**：边际、期望、调整残差、保度零模型都在给定矩阵后唯一确定。留成待办，是把判断成本转嫁给操作者。

### 新增
1. **`scripts/ecr_o8.py`**（独立模块，每次 `plan()` 必跑）
   - `margins`：行边际 `n_i`、列边际 `n_j`、`N`；
   - `cells[]`：`E_ij = n_i·n_j/N`、调整残差 `z_ij`；
   - `cell_level`：三态判定 `allowed / forbidden / not_applicable_binary`；
   - `null_model`：C-score（Stone & Roberts 1990）+ 棋盘格交换保双边边际零模型（Gotelli 2000），`seed=20261112`、`--null-reps` 可调；
   - `readout[]`：平铺数值现象，不含判断词。
2. **`matrix_scale`**：默认 `binary`；`counts` 时走 Cochran 阈值。
3. **新输出四项**：`baseline_stats` / `power` / `verdict` / `coding`，均进 schema `required`。
4. **`verdict`**：`budget_feasible`、`gate_balance(ok|insufficient)`、`cell_level_stats`、`overall(complete|degraded)` —— 计划必须自报完整度。

### 修正（被 t4 逼出来的）
- **0/1 关联矩阵的逐格推断在 binary 尺度上无定义**：期望格受边际约束，平衡结构下 `E ≡ 1`，永远达不到 5（本实例 `maxE=1.090909`）。把它标成 `forbidden` 会误导成"再补几篇文献就能算"，故单列 `not_applicable_binary`。
- **O6 门位从告警升级为判定**：`gate_balance=insufficient` → `overall=degraded`（`t4 (e)` 断言了 degraded→complete 的翻转）。

### 验收
- `selftest` **3/3 → 4/4**（新增 `t4_baseline_o8`：稀疏 / 确定性 / hub 结构 / counts 尺度 / verdict 翻转）；
- 实例数字：`minE=0.045455`、`maxE=1.090909`、C-score `9.8` vs 零分布 `8.9906±0.55034`、`p_low=0.9321`、`p_high=0.1299`；
- 同路径重跑 stdout 与 JSON 均字节一致（该版 `plan.json` md5 已随后续版本变化，v1.2 终值见 §验收）。

### 该版本否掉的旧说法
"x1 有 12 条证据 → 强共识"：在 binary 尺度上逐格不可说；C-score 与保边际随机无差别（`p_low=0.93`），语料并未额外聚集。只能报 `c=12` 这个计数。

## v1.0 — 2026-11-12（落盘版）

**性质**：v0.1 设计的完成态 + 本会话（2026-11-11）全部提炼产物的并入。首个可执行版本。

### 新增能力
1. **O6 门位标注**（gate ∈ {0..5}）
   每条证据必须声明它在哪一门被观测。依据：本会话对耻辱柱 32 条事故的门位编码——设施 9 (28.1%)、方法 8 (25.0%)、承载物 5 (15.6%)、元层 4 (12.5%)、现象 3 (9.4%)、冻结 3 (9.4%)。**只注入现象门(3) 的证据，必然重演"现象对、承载物对、判据错"**。
2. **O7 十不变量闸门**（A–H + I + J）
   - A 表层替代 → `proxy_of` 无同域验证则不得进链
   - B 断言先于证据 → `provenance.verified != true` 拒载；`bytes` 与磁盘不符记失败
   - C 不同框 → `domain.scope` / `domain.frozen_scale` 必填
   - E 静默失效 → `usable` 必须显式 true
   - F 越权 → `authorization.in_scope == false` 只列不注入
   - G 继承未核 → `claim_type=relayed` 必须有 `upstream_of`
   - H 降维 → `resolution{locked,free}` 控制档位
   - **I 命名逃逸（新）** → `claim_type ∈ {measured, relayed, inferred}` 强制三选一；relayed 无出处即拒载。**这是"把没查过的东西改名成规则没覆盖的动词"的机器阻断**
   - **J 闸门位置错（新）** → plan 必须输出 `moments{T1..T5}`，把检查点钉在**落笔时刻**而非交付时刻
3. **O3 修正：边际价值必须扣检验力**
   `power.expected_min_cell < 5` → 该投影 stance 降为 `undecidable`，不计入 ΔD 与覆盖度，并进 `gaps`。
   依据：本会话中 `1→2 = 0/10` 曾被当作硬证据，实测期望仅 **1.04**、`z=−1.21`（不显著）——检验力不足不是证据。
4. **O3 增项：佐证值（共识层的用途）**
   `ΔD = Σ(新覆盖权重) + 佐证值`；佐证值 = 0.25 / 条，同一子问题至多 2 条，且 stance 必须一致。
   否则"共识层 c≥2"永远只会注入一条证据——那是单点依赖，不是共识。
5. **对 ECR 自身的元约束：基线纪律**
   任何"某类证据被高估/低估"的结论，必须先扣**度数边际**（quasi-independence `E_ij = n_i·n_j/N` + 配置模型保度检验）；逐格期望 ≤3.25 时禁止报告逐格 p。依据：本会话 36 个非零格期望全 ≤3.25，逐格 z 的正态近似失效。

### 修复
- **O5 分辨率升级越界**：首版把"未进链的证据"也计入升级，导致预算虚耗（实测 45,165 B）。v1.0 限定**只对链内证据**升级，实测回落到 35,195 B。
- **链内证据的装配档位与最终档位混淆**：输出拆为 `mode_initial` / `mode`，避免把升级结果误读成装配结果。
- **I 不变量无留痕**：relayed 无出处原先只进 `blocked.reason`，不进 `invariants_failed`；v1.0 双写。

### 落地实例
- `refs/worked_example_input.json`：本会话 17 个文件，bytes 由 `wc -c` 实测，sha256 运行时重算
- `refs/worked_example_plan.json`：实跑输出（35,195 B 注入 / 10 步链 / 缺口 x6）
- `refs/session_20261111_assets.md`：产出 → 角色映射
- 验收：selftest **3/3**；plan JSON 与 stdout 同路径重跑**字节一致**；出处核验 **17/17**

---

## v0.1 — 2026-10-29（设计稿，未落盘）

来源：CLI 会话 `20261029_125647_b2325f`（"继续上一条对话"）。当时用户指令为「设计方案即可」，故仅出设计：

- 五算子：O1 覆盖分层（c≥2 共识 / c=1 独占 / c=0 缺口）、O2 预算分池（B_C/B_U/B_L，λ=0.30）、O3 边际价值（ΔD/bytes，不按权威/被引/篇幅）、O4 停机准则、O5 三级降维（L0/L1/L2，locked 强制 L0）
- 符号：x / x₁..x_k / type / resolution / a_i / π_i / c_j / B / λ
- 三份 JSON 契约 + 目录骨架
- 当时对原框架的五条反驳（已被 v1.0 吸收）：严格交集系统性偏保守（滤掉差集里最该看的证据）→ 改覆盖度分层 + 独占配额下限；"并联不可实现"不成立 → 降维并联是第三条路；"链"需要贪心顺序判据；缺停止准则；写入端编目与读取端调度是**两端**，不是一端

**v0.1 未落盘原因**：A/B/C 三选（读取端调度 / 写入端编目 / 两端都要）未定。v1.0 取 **C**，理由：本会话产出天然是写入端编目（编码表、不变量、闸门表），ECR 负责读取端调度——只做 A 无标签可算，只做 B 无落地收益。
