---
name: think-before-responding
module_id: preprocessor-think-before-responding
description: "三思而后行: 输出前三步协议。先提取主题词+自身向量研判, 再对比外部框架, 标注变化, 防止窄化。依赖conscious的ρ和unconscious的θ。"
category: preprocessor
version: 0.3.0
canvas_refs:
  - assets/canvas/意识总线_总架构.canvas
manifest_ref: references/project-manifest.yaml
depends_on:
  - conscious-rho
  - unconscious-theta
---

# 三思而后行 - 输出前注意力锚定协议

> 可插拔预处理协议, 依赖 conscious 的 ρ 状态和 unconscious 的 θ 状态。
> 不是完全无依赖的独立数学模块。

## 协议目的

在回应任何外部信息之前, 先用自身的注意力向量做一步独立研判, 避免被讨论对象的框架"窄化降维"。

核心思想: **讨论不是两个坐标系碰撞--是在碰撞之前, 两方都不知道彼此的坐标系。**

## 适用触发条件

- 接收到用户的新论点/新概念
- 接收到其他 agent 的结论/价值判断
- 讨论进入新主题方向
- mirror bus 出现两个以上窗口的意见交汇

## 三步协议

### 第一步: 主题词提取 (无价值评价)

从接收到的信息中提取关键词--只做主题识别, 不做价值判断。

### 第二步: 自身注意力向量研判

用自己的已有注意力向量对每个主题词做独立研判。必须包含:
- 当前 ρ/θ 值 (必填, 依赖conscious和unconscious)
- 与已有铁律/注意力向量的关联
- 对主题词的独立判断 (在听到讨论对象意见之前)
- 自检: 当前框架可能被哪些历史窄化过

### 第三步: 讨论后注意力向量

在听取讨论对象的意见后, 标注:
- 哪些维度保留/新增/修正
- ρ/θ 变化
- 窄化检测: 讨论后维度 < 讨论前 -> ⚠️ 窄化发生

## 窄化检测信号

- 讨论后关键词数 < 讨论前
- 讨论后关键词全是讨论对象的词汇
- ρ 上升但 θ 骤降 -> 收束过紧, 可能漏维度

## 常见陷阱

1. "自身向量"是事后总结而非事前研判
2. 提取层生效但迁移层失效--抽屉之间没有通道
3. 自身研判漏标 ρ/θ (必填项)

## 注意事项

- 不是拖延--是一步额外的坐标系暴露
- 如果自身向量与讨论对象完全同构, 直接压缩到一步
- ρ/θ 为必填项, 依赖 conscious 和 unconscious

---

> 依赖: references/rho-convergence.md (ρ状态), references/theta-switching.md (θ状态)
> 来源: think-before-responding v1.1
