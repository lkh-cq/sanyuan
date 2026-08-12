---
name: index-naming-norm
description: "index 命名规范 v2.0 —— 知识库目录索引的命名、分层与拓扑审计。Use when 索引整理、index命名、层级治理、知识库结构、拓扑审计、index 文件重命名、全库索引注册。作为 consciousness-bus 的知识整理子模块加载；不要因普通的一步问答而展开。"
---

# index 命名规范 (v2.0) 扩展

> 模块: extension-index-naming-norm
> 版本: 0.1.0 (experimental) —— 扩展包版本;规范本体版本见标题 v2.0(两者独立:规范冻结 v2.0,skill 包迭代 0.1.0)
> 日期: 2026-08-12 | 取代: 旧 `L0-001` 序号规范 (v1.0, 2026-08-07, 用于 master_index.csv 治理)
> 来源: hermes_memory 全盘 index 拓扑审计 (见 [references/index-scan-audit-20260812.md](references/index-scan-audit-20260812.md)) + 规范冻结
> 触发: 用户冻结 (2026-08-12): "我们需要一个新的规范, index 命名规范"
> 定位: consciousness-bus 的**知识整理子模块** —— 把"目录索引文件怎么命名、怎么分层"编译为可校验规则。

---

## 与 consciousness-bus 的关系（知识整理子模块）

本扩展是 consciousness-bus 的知识整理子模块:

- **输入**: 一个知识库根目录 (如 `/mnt/d/hermes_memory`)
- **输出**: 该目录下 index 文件的命名规范 + 不合规清单 (拓扑审计)
- **边界**: 只治理目录索引文件 (Markdown) 的命名与层级; 不进入 M/H 归一化主流程, 但为知识整理类任务提供执行期间的命名约束。

| consciousness-bus 概念 | 本扩展的对应 |
|------------------------|-------------|
| 任务边界 B_T | 扫描根目录 = 治理边界; 目录层级 = 边界内的结构 |
| 元信息空间 M | index 文件名携带的三段元信息 `<date>.<内容>.<层级>` |
| 知识整理任务类型 | 索引命名规范 = 知识整理子任务的可执行约束 |
| archive-ingestion (归档迁移) | 过渡保留项 (`_index.md` / `COLOR_INDEX.md` / `GEO_ROOT_INDEX.md`) 不参与重命名 |

---

## 一、层级定义（命名层级 = 上游目录的文件夹个数）

| 层级 | 位置 | 上游文件夹个数 | 说明 |
|------|------|----------------|------|
| 0 | 根目录 | 0 | 全库总 INDEX |
| 1 | 根文件夹 | 1 | 每个根文件夹的 main branch index |
| 2 | 次级文件夹 | 2 | 根文件夹下的子分支 |
| 3 | 三级文件夹 | 3 | 子分支下的子分支 |
| n | n 级文件夹 | n | 依此类推 |

例: `/mnt/d/hermes_memory/reference/papers/T1/oa/` 的 index 层级 = 4 (reference=1, papers=2, T1=3, oa=4)

## 二、命名规则

### 规则 1: 根文件夹的 main branch index（层级 1）

- 命名: **按内容命名或编号**（不用固定 `_INDEX.md`）;按内容命名时语义名须以 `_index` 结尾（如 `memory_index.md`）,否则校验脚本判不合规
- 结构: `index.<date>.<内容>.<层级>` 亦可，或直接内容语义名（如 `memory_index.md`）
- 必须: 文件第一行(标题下)加**小标题**，标引该目录下具体内容，方便下一级 index 索引

示例:
```markdown
# memory 主索引 (层级 1)
> 内容: 持久记忆层——画像/编码规范/耻辱柱/免疫记忆
> 下级: memory/ 无子目录
> 回链: [[_index]]
```

### 规则 2: 子分支 index（层级 ≥ 2）

- 命名: 严格 `index.<date>.<内容>.<层级>`
  - `<date>`: YYYYMMDD
  - `<内容>`: 该目录主题（中文或英文短词）
  - `<层级>`: 数字 = 上游目录文件夹个数
- 示例: `index.20260812.记忆研究.2.md`（位于 workspace/wf_001_memory_research/，上游 2 个文件夹）

### 规则 3: 根目录总 INDEX（层级 0）

- 文件名: 保留 `_index.md`（全库唯一总入口）。**仅根目录的 `_index.md` 保留;层级 ≥1 的 `_index.md` 一律按规则 1/2 改造**（校验脚本口径一致）
- 内容: 登记全部层级 1 main index + 全库索引注册表

## 三、新旧规范过渡

| 项 | v1.0 (旧) | v2.0 (新) |
|----|-----------|-----------|
| 命名 | L0-001 / L1-042 序号 | 按内容命名/编号 + index.<date>.<内容>.<层级> |
| 层级判定 | get_level() FOLDER_MAP | 上游目录文件夹个数（显式数字） |
| 适用 | master_index.csv 条目 | 文件系统目录索引文件 |
| 保留 | — | `_index.md`（根）、`COLOR_INDEX.md`、`GEO_ROOT_INDEX.md` 不参与重命名 |

## 四、当前目录映射表（2026-08-12 全盘扫描，58 个目录索引参与改造；层级=上游文件夹个数）

完整 58 项映射见 [references/index-mapping-20260812.md](references/index-mapping-20260812.md)。

层级分布: 层级 1 ×10, 层级 2 ×19, 层级 3 ×12, 层级 4 ×4, 层级 6 ×12, 层级 8 ×1。

## 五、批量重命名执行注意

- 重命名会破坏所有指向旧名的 wikilink（Obsidian 以文件名匹配）
- 执行前必须: 全库 grep 旧名 → 同步更新 wikilink
- 执行后必须: 重新登记 `_index.md` 全库索引注册表 + 刷新 MCP FTS
- CSV 索引 (master_index.csv) 不参与命名改造，保持数据格式
- 重命名前先 dry-run: 用 [scripts/validate_index_naming.py](scripts/validate_index_naming.py) `--dry` 预览建议命名，列出受影响 wikilink

## 六、维护约定

1. 新建目录: 先按层级数字创建 `index.<date>.<内容>.<层级>` 并登记根 `_index.md`
2. 根文件夹级: 内容语义命名优先（可读性），子分支严格三段式
3. 小标题必须存在: 目录下第一行用 `> 内容:` 标引具体内容，供下一级索引引用
4. 只读预览: 重命名前 dry-run 列出受影响 wikilink

## 七、校验工具

`python3 extensions/index-naming/scripts/validate_index_naming.py --dry <扫描根目录>`

- 递归扫描指定目录，识别 index 文件（Markdown）
- 按 v2.0 校验: 层级数字 = 上游目录文件夹个数、三段式 `index.<date>.<内容>.<层级>`
- 输出不合规清单 + 建议新名（`--dry` 只读预览，不写入）
- 排除运行时/构建噪声: `node_modules/`、`.git/`、`dist/`、`__pycache__/`、`.Rproj.user/`

## 八、边界 (不做的事)

- 不重命名任何文件（本扩展只输出规范与校验清单，重命名由用户/其他流程执行）
- 不修改 CSV 索引 (master_index.csv)
- 不改内容级 wikilink；只规范 index 文件自身命名
- 不替代 archive-ingestion（归档后路由）与 master_index.csv 治理
