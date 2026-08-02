# 模态可见性边界

## 目的

模态可见性边界记录当前工作环境能看到什么、不能看到什么, 以及这些缺失会怎样影响阅读拓扑。

缺多模态不是证据少一点, 而是可能把"文本声称的拓扑"误判为"证据实际呈现的拓扑"。

## 核心区分

~~~yaml
text_topology:
  scope: author_claims_in_text
  confidence: null

evidence_topology:
  scope: figures_tables_images_video_raw_data
  confidence: null

claim_evidence_gap:
  status: unverified | aligned | weak_support | contradicted | unavailable
~~~

## 边界记录

~~~yaml
modality_boundary:
  available_modalities:
    - text
  partial_modalities: []
  missing_modalities:
    - figures
    - supplementary_images
    - protocol_video
    - raw_data_visuals
  affected_nodes:
    - evidence_support
    - spatial_localization
    - temporal_process
    - method_reproducibility
    - quantitative_visual_check
  consequences:
    - mark_claim_as_text_only
    - downgrade_evidence_topology_confidence
    - require_external_visual_review
~~~

## 重大流程隐患

| 缺失维度 | 风险 | 处理 |
| --- | --- | --- |
| 图像证据 | WB、IF、IHC、HE 等质量不可复核 | 文本支持标记为 claim-only |
| 图表结构 | panel、坐标轴、统计标记、分组关系不可见 | 禁止建立强 evidence edge |
| 空间关系 | 组织定位、病灶边界、细胞定位缺失 | 降级地题读取置信度 |
| 时间过程 | 处理时长、采样顺序、动态变化缺失 | 避免把并列关系读成因果链 |
| 量化视觉 | 条带强弱、散点分布、离群点不可查 | 降低证据压力等级 |
| 方法动作 | 取材、培养、染色、分选动作不可见 | 标记人题实践记录不足 |
| 版式结构 | PDF 图文邻近、脚注、补充材料引用丢失 | 保留顺序不确定性 |
| 原始形态 | 矩阵、谱图、流式门控、原图不可见 | 区分原始观察与作者解释 |

## 执行规则

1. 任何缺失模态不得被静默当作不存在。
2. 在 text-only 环境中, 结论最多称为正文阅读拓扑。
3. 涉及图像质量、空间定位、方法动作和原始数据形态时, 必须标记 `modality_boundary`。
4. 如果证据主要在图表或补充材料中, 但当前环境不可见, 对应证据边不得升级为强支持。
5. 多模态缺口优先影响地题与人题, 因为空间、材料、操作和图像证据常不完整承载于正文文本。

## 与三元三才的映射

- 天题: 信息的本来样貌。缺原始图像或数据时, 天题读取不完整。
- 地题: 读取方式。缺版式、图表结构、空间关系时, 地题受损最重。
- 人题: 读取记录。缺方法动作、操作视频或实验流程图时, 人题记录必须降级。
- 互: claim 与 evidence 之间的关系应记录为 MutualNode 或路径残差, 不嵌入 StoreNode。
