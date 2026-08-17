# 决策记录 0002 — frozen core bundle 冻结挂起

- 日期: 2026-08-17
- 状态: 已采纳 (Task C 挂起)

## 裁决

frozen/core_bundle.lock 与 SKILL.md 总线联系中的 `version: 3.3.0 / commit: 875bda6`
保持愿景不变, 暂不填 sha256 digest。Task C (bundle freeze + digest) 挂起, 待
consciousness-bus 仓库 3.3.0 正式提交并推送后, 以真实 commit + 内容 digest 回填。

## 证据 (2026-08-17 观测)

- `git cat-file -t 875bda6` (consciousness-bus) → fatal: not a valid object name; 本地全 ref 无此 commit
- `git ls-remote origin | grep 875bda6` → 远程亦无
- consciousness-bus 真实 HEAD: `b8ed778` (v3.2.2 tag); `references/project-manifest.yaml` 工作区已改 3.3.0 但未提交
- 结论: 875bda6 为不存在之幽灵 commit, 不可冻结; 冻结须以真实发布状态为锚

## 后续动作

1. consciousness-bus 3.3.0 commit + push 后: 回填 lock 的 commit 与 sha256, 同步 SKILL.md 总线联系
2. 未冻结期间, frozen core 语义以 lock 文件愿景字段 (source/version/commit) 为准, sha256 待补
