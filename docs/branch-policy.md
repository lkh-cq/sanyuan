# 双主干治理与分支政策

## 分支身份

| | main | hive-main |
|---|---|---|
| 目标 | 通用任务处理、会话隔离 | 单任务多通道并行解算 |
| 状态身份 | session/task scope | hive_id + B_T generation |
| 跨任务策略 | 严格隔离 | 零默认耦合; 显式 import bridge |
| 版本标签 | v* | hive-v* |
| Python 包 | sanyuan-bus | sanyuan-hive |

## 硬性规则 (MUST)

1. hive-main 是 orphan branch, 不从 main 继承提交历史。
2. 禁止 main 与 hive-main 之间 merge / rebase / cherry-pick。
3. 两条主干独立 CI 文件、包名、版本源、缓存键、构建产物与 release tag。
4. 分支保护必须拒绝来自另一主干的合并提交, 并要求隔离测试通过。
5. 分支名固定 hive-main (禁止 main/hive: 与 refs/heads/main 引用文件路径冲突)。

## 冻结核心唯一通道

core_bundle: 完整、只读、带来源指纹的版本包导入; runtime_state_shared 恒为 false。

## 发布责任分离 (ADR 0003)

- hive-main 与 Fullstack 是不同发布单元, 禁止共用 remote / tag 前缀 / 分支保护。
- hive-main 版本标签固定 `hive-v*`; 发布前必须通过 `scripts/release_check.py`
  (版本源一致 + 工作区干净 + commit/tag 闭环)。
- 未绑定真实证据 (宿主身份/receipt/执行产物) 的状态不得晋升为可信稳定。

## 迁出条款

hive-main 成熟到需独立 issue/release 治理时可无损迁出为单独仓库; 迁出前不得反向耦合 main。
