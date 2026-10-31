# 长期 downstream 应用

Open Campus: UO 与通用 Pipeline 都会长期维护，方向分别明确。

| 项目 | 长期重点 |
| --- | --- |
| upstream Pipeline | 重建方法论、算法质量、自动化、数据核验、可重复性、导出与交换约定 |
| downstream Open Campus: UO | UO 模型细化、稳定建筑身份、屋顶与立面、材质、步道、校园细节及探索体验 |

`pipeline.lock.json` 固定 repository、版本与 commit。`scripts/rebuild.ps1` 默认要求 upstream clean checkout 且 commit 一致，通过 `-PipelineRoot` 指定独立工作副本。

升级时先核查方法与 schema 变化，在试验区重建，比较来源、地理框架、地形报告、候选变化和浏览器行为，再更新 lock 与产物。v0.1 候选 ID 来自量化位置，方法变化可能拆分/合并候选；后续需要独立的稳定建筑登记表。

通用算法修复提交 upstream。UO 的特定几何修正及采集成果留在本仓库。未来人工精细化资产与自动白模分层保存，自动重建不能覆盖人工权威模型。

下一步内容细化：核对历史候选并剔除树冠 → 确认建筑身份、轮廓和高度 → 逐栋修复屋顶、立面和材质 → 改进步道、碰撞及地形衔接 → 按规模推进 LOD 和瓦片。

仓库目前 private。本版没有启用 Pages，代码和原创资产的许可证尚未选定。
