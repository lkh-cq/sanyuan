# 贡献与发布规范

## 变更边界

- 先确认改动属于冻结本体、稳定模块、实验模块、来源记录还是读者端交付。
- 冻结本体只在 `references/architecture.md` 修改，并同步清单、来源记录、Schema、配方和验收用例。
- 不把归档材料中的旧定义直接复制回激活层；先通过 `archive-ingestion.md` 登记迁移决定。
- 不把内部节点、关系代码或无注释图示当作读者端结果。

## 提交规范

使用 Conventional Commits：

```text
feat: add coupling-state storage envelope
fix: derive project version from manifest
docs: explain mascot provenance
test: add readable-literature delivery case
chore: remove stale platform metadata
```

一个提交只处理一个可说明的意图。不要把无关格式化、资产替换和本体修改混在同一提交。

## 校验与评审

提交前运行：

```bash
python3 scripts/validate_bundle.py
python3 scripts/validate_endoscope.py
python3 scripts/validate_obsidian.py

cd integrations/obsidian/plugin
npm ci
npm run build
```

确定性校验负责文件、链接、清单、YAML、Canvas、Schema 路径、配方顺序和测试结构。语义行为由独立前向测试验证，不用字符串存在性冒充语义正确性。

Pull request 说明至少包括：改了什么、为什么改、是否影响冻结本体、验证方式和剩余风险。

## 版本发布

- `references/project-manifest.yaml` 的 `project.version` 是唯一项目版本源。
- 模块版本独立维护，并在 `module_lifecycle` 中标记 `stable` 或 `experimental`。
- 默认分支每次形成新发布提交前都应更新项目版本；同一个 `v<version>` 标签不得移动。
- 自动化在默认分支校验通过后创建缺失的 `v<version>` 标签；若标签已指向其他提交，发布失败并要求提升版本。
