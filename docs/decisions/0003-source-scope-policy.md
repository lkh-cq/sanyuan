# 决策记录 0003 — source_scope 校验策略与发布责任分离

- 日期: 2026-09-02
- 状态: 已采纳
- 来源: Fullstack 只读复核结论 (P0 #3/#4/#5) + 幸存 hive-main 加固

## 裁决 1 — source_scope 必须 fail-closed 校验 (P0 #3)

`source_scope` 不再只约束 `^source://` 前缀。`boundary.validate_source_scope`
对每条作用域执行 fail-closed 校验，schema 只做结构层第一道过滤：

| 类别 | 拒绝形式 |
| --- | --- |
| 等价全局通配 | `*`、`**`、`source://*`、`source://**`、`source://*/**`、`md://*`、`md:///**` |
| 路径穿越 | `source://../etc`、`source://project/../../etc` |
| 编码穿越 | `..%2f`、`%2e%2e`、`%2E%2E`、`%5c`（编码分隔符/点段一律拒绝） |
| 无锚点 | `source://`、`source:///`、非 URI 字符串 |

接受条件：至少一个具体（非通配）路径段，如 `source://project-a/**`、
`md:///project/**`。`**` 只允许出现在具体锚点之后。

## 裁决 2 — Fullstack 与 hive-main 发布责任分离 (P0 #4)

- Fullstack（0.4.0a2 本地原型）与 hive-main 是**不同发布单元**，禁止共用
  remote、tag 前缀或分支保护配置。
- hive-main 版本标签固定为 `hive-v*`；Fullstack 若恢复，须独立仓库 + 独立 tag。
- 任一单元发布前必须通过 `scripts/release_check.py`：版本源一致、工作区干净、
  commit 与 tag 闭环，缺一不可。

## 裁决 3 — 未绑定真实证据的状态禁止晋升 (P0 #5)

- 任何 `repo_verified` / `stable` 之类状态，在绑定真实宿主身份、receipt
  （真实命令 + 退出码 + 标准化输出哈希 + 执行环境）之前，只视为**协议层状态机**，
  不视为可信事实。
- 禁止把本地工作区测试结果当作已发布功能；发布判断只认远端可复现证据。

## 影响

- `src/sanyuan_hive/boundary.py`：新增 `validate_source_scope` / `validate_boundary`。
- `src/sanyuan_hive/schemas/boundary-task.schema.json`：收紧 `source_scope` pattern。
- `tests/test_boundary.py`：新增等价通配/穿越/编码否定测试。
- `.github/workflows/hive-ci.yml`：新增 ruff/mypy/bandit/pip-audit/md-links/release 门。
- `scripts/release_check.py`、`scripts/check_md_links.py`：新增发布与链接门。
