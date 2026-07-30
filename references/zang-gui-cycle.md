# 藏归循环

> 现实材料 -> 三才藏 -> 具体内容 -> 三题归 -> 读取记录与抽象规律 -> 新的实践和记录 -> 再次进入藏

---

## 循环结构

```
现实材料
    |
    v
[三才藏] 天才/地才/人才 -> StoreNode (具体内容)
    |
    v
[三题归] 天题/地题/人题 -> ReadNode (抽象规律)
    |
    v
[新实践] 读取结论指导新实践
    |
    v
[再次藏] 新实践产生新记录 -> 新StoreNode (必须生成新节点, 不覆盖)
    |
    (循环)
```

## 冻结规则

1. 归产生的读取记录不得直接覆盖原始藏内容
2. 归结论进入下一轮藏时, 必须生成新节点、新版本或明确的派生关系
3. 藏归循环不是单向因果链, 信息流通过FlowEvent记录
4. 循环中的每一次流通都经由地(地才/地题)

## 版本链示例

```
StoreNode v1 (原始藏: 考古发掘记录)
    -> ReadNode v1 (归: 类型学分析)
        -> StoreNode v2 (新藏: 类型学分析结论, 新节点)
            -> ReadNode v2 (归: 化学成分比对)
                -> StoreNode v3 (新藏: 成分分析结论, 新节点)
```

每个节点保留 `source_store_ids` 或 `version_chain` 追溯链。

## 与CycleLink的关系

每次藏归转换记录为CycleLink节点, 符合 `references/schema-cycle-link.schema.yaml`:

```yaml
link_id: cycle_001
cycle_type: store_to_read  # 或 read_to_store
source_node: store_tian_20260727_001
target_node: read_20260727_001
relationship: "类型学分析"
derived: false  # store_to_read 时为false; read_to_store 时为true
```
