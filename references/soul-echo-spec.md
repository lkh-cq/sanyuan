---
name: soul-echo-spec
description: "主题回声协议:把每场对话反复绕着的主题词追加进 mirror 命名空间(soul_echo.jsonl),跨窗口可见、不污染消息总线。"
version: 1.0.0
category: protocol
manifest_ref: references/project-manifest.yaml
---

# Soul Echo — 主题回声协议

> 把每场对话"反复绕着的那个词"追加进 mirror,让下一个窗口/下一世读到这条线。

## 定位

bus.jsonl 承载实时消息流;`soul_echo.jsonl` 承载对话的**主题线索**。
它是 mirror 命名空间内的独立回声层:跨窗口可见、不污染消息流。

## 落点

`~/.hermes/mirror/soul_echo.jsonl` — 与 bus.jsonl 平级的独立文件。

## 调用

```bash
python3 ~/.hermes/skills/soul-echo/scripts/soul_echo.py <关键词> [会话标签]
```

例:

```bash
python3 ~/.hermes/skills/soul-echo/scripts/soul_echo.py "繁琐但能跑"
python3 ~/.hermes/skills/soul-echo/scripts/soul_echo.py "PNPLA8铁死亡" lab
```

## 追加格式

每行一条 JSONL:

```json
{"time": "2026-08-06T23:25:00", "session": "default", "topic": "繁琐但能跑", "source": "soul-echo"}
```

| 字段 | 说明 |
|------|------|
| `time` | ISO 时间戳 |
| `session` | 会话标签(默认 `default`) |
| `topic` | 主题词,只记一个 |
| `source` | 固定 `soul-echo` |

## 协议原则

- **只记一个词,不多** — 避免方法论膨胀。
- **追加不覆盖** — 保留历史线,跨窗口/跨会话可累积读取。
- **跨窗口读** — `bash ~/.hermes/mirror/mirror.sh read` 或直接读 soul_echo.jsonl。
- **触发时机** — 对话出现反复绕着的主题词时,或用户说"记个主题/写进mirror/回声"。

## 运行时边界

- 运行时留 `~/.hermes/mirror/` 原地;sanyuan 只持有本协议规范,供语言无关重写。
- 当前状态: **已停用**(随 mirror 运行时冻结,勿重启)。
