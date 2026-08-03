# 藏与耦合态写入规范

> StoreNode 保存具体内容，MutualNode 保存关系，CouplingState 把二者登记为可检索的写入事务。三类对象保持分离。

## 1. 核心写入单元

完整入库单元是耦合态，不是孤立事实。这里的“耦合态”是封套：它引用一个或多个 StoreNode、至少一个 MutualNode，并可选引用 ReadNode；它不把内容和关系压成同一字段，也不是第四本体实体。

```text
StoreNode(s) + MutualNode(s) + optional ReadNode(s)
                         ↓
                   CouplingState
```

孤立 StoreNode 可以暂存，但必须登记为 `incomplete` 或进入待补关系队列，不能声称已完成耦合。关系只有在端点、条件、来源和证据边界可追溯时才进入完整耦合态。

## 2. ID 与路径

```text
StoreNode:     store_{layer}_{YYYYMMDD}_{seq}
MutualNode:    hu_{YYYYMMDD}_{seq}
ReadNode:      read_{YYYYMMDD}_{seq}
CouplingState: coupling_{YYYYMMDD}_{seq}
```

运行时相对路径：

```text
reference/store/{store_id}.yaml
reference/read/{read_id}.yaml
reference/flow/{mutual_id}.yaml
reference/flow/{coupling_id}.yaml
```

## 3. 耦合态格式

写入必须符合 [schema-coupling-state.schema.yaml](schema-coupling-state.schema.yaml)：

```yaml
coupling_id: coupling_20260803_001
store_refs:
  - store_tian_20260803_001
  - store_di_20260803_002
  - store_ren_20260803_003
read_refs: []
mutual_refs:
  - hu_20260803_001
coupling_summary: "钴呈色规律经窑场材料与温度边界进入窑匠烧制实践。"
conditions:
  - "来源与材料检测均指向同一批样本"
evidence_boundaries:
  - "原料产地仍有争议"
status: observed
topology_level: local
signal: medium
provenance:
  source_anchors:
    - "source/paper-a#p12"
  created_at: "2026-08-03T00:00:00Z"
version: 1.0.0
```

`coupling_summary` 必须描述交互或转换过程，不能只写“相关”。假说、争议和缺失分别使用 `hypothesized`、`disputed`、`incomplete`，不得用置信度掩盖状态差异。

## 4. 证据类型与边界

StoreNode 的证据类型继续使用：`excavation`、`text`、`experiment`、`user_input`、`observation`、`literature`。

每个耦合态同时保存：

- 可回到原材料的位置；
- 关系端点与观测方式；
- 关系成立条件；
- 当前证据只支持相关、条件、转换还是因果；
- 冲突、缺失与可替代解释。

## 5. 版本规则

- 已写入节点与耦合态不原地覆盖；新信息产生新版本并用 `supersedes` 连接。
- 归结论进入下一轮藏时创建新节点，不改写来源节点。
- 耦合态版本变化不自动提升其证据强度或生命周期状态。

## 6. 写入后验证

1. 按 Schema 校验 StoreNode、MutualNode、ReadNode 与 CouplingState。
2. 读回文件头部与尾部并检查非空。
3. 检查所有引用 ID 均存在或被明确标记为待补。
4. 检查 `coupling_summary`、条件、来源和证据边界不为空。
5. 检查任务运行时内容没有写进 Skill 的只读 `references/`。

## 7. 禁止

- 禁止把内容、关系与读取记录压成一个不可追溯字段。
- 禁止把 MutualNode、FlowEvent 或独立事实直接命名为完整耦合态。
- 禁止在藏节点中写入无来源的抽象规律。
- 禁止把旧六耦合界面重新设为基础本体。
- 禁止把地固定为地理物质条件或赋予固有方向。
- 禁止使用绝对路径。
