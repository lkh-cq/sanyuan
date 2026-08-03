---
name: yijing-coupling-matrix
module_id: extension-yijing-coupling-matrix
description: "八卦双坐标与六十四态转移矩阵的实验性数据接口。"
category: experimental
version: 0.1.0
---

# 易经耦合矩阵接口

本模块保存《三元道辩体系》第四章提出的“八卦 × 八卦 = 六十四态”算子雏形。它是实验性表示，不属于冻结本体，不证明《易经》的历史本质，也不替代互信息空间。

## 八卦编码

按上、中、下三位记录：

| 卦 | 编码 | 十进制 |
| --- | --- | ---: |
| 乾 | `111` | 7 |
| 兑 | `110` | 6 |
| 离 | `101` | 5 |
| 震 | `100` | 4 |
| 巽 | `011` | 3 |
| 坎 | `010` | 2 |
| 艮 | `001` | 1 |
| 坤 | `000` | 0 |

编码只是离散地址，不自带吉凶、质量或事实判断。

## 双坐标

`C_info` 保存可直接观察或可回到来源的状态：上卦、下卦、六爻排列、卦名、原文位置与观测条件。

`C_coupling` 保存分析者对两组三位状态之间关系的记录：方向、条件、转换、反馈、证据与不确定性。它必须引用来源，不得把结构相似直接写成现实因果。

```yaml
C_info:
  upper_code: "111"
  lower_code: "000"
  state_id: 56
  source_anchor: ""
  observed_text: ""

C_coupling:
  relation_type: conditional | transform | feedback | observed_transition
  conditions: []
  evidence_refs: []
  uncertainty: ""
```

原始理论曾把上卦、下卦与卦辞分别解释为天题、人题、地题。该映射与当前冻结三题定义不完全同构，因此只保留为来源假说；运行时使用中性的 `upper_state`、`lower_state` 与 `relation_record`。

## 六十四态地址

令上卦十进制值为 `u`，下卦为 `l`：

```text
state_id = 8u + l,  u,l ∈ {0,…,7}
```

由此得到 `0…63` 的稳定地址。地址顺序不等于传统卦序；如需使用文王卦序，必须另存显式映射，不得静默替换。

## 64×64 转移矩阵

定义稀疏矩阵 `T[a,b]` 记录从状态 `a` 到 `b` 的已观察转移。没有语料、规则或实验数据时，所有单元保持 `unknown`，不得自动填成 0、1、概率或吉凶分值。

每条非空转移至少保存：来源、观测单位、方向、条件、计数或权重的计算方法、置信区间或不确定性。汉明距离、变爻数量或传统解释可以作为候选特征，不能在未声明时充当转移规则。

## 与当前架构的接口

- `C_info` 可引用 StoreNode 或 ReadNode；`C_coupling` 可引用 MutualNode。
- 一组状态与关系可登记为 CouplingState，保持内容节点和关系节点分离。
- 本模块只在用户明确讨论八卦、六十四态或耦合矩阵时加载。
- 任何历史、医学或现实推断仍须通过任务边界与证据验证。
