# Open Campus: UO

以 Blender 为核心、可跨引擎复用的 University of Oregon（Eugene）校园三维资产库与浏览器预览项目。

**状态：项目规划与仓库初始化。尚无真实校园数据、重建模型或可运行预览。仓库为 private。**

## 两个仓库的分工

| 仓库 | 负责内容 |
| --- | --- |
| [Open Geospatial-to-3D Reconstruction Pipeline](https://github.com/williamQ96/open-geospatial-to-3d-reconstruction-pipeline) | 可迁移到其他地区的点云、地形、影像处理，Blender 生成与导出，元数据约定和验证工具 |
| [Open Campus: UO](https://github.com/williamQ96/open-campus-uo)（本仓库） | UO 区域配置、数据来源记录、校园 Blender 资产、场景与瓦片清单、Three.js 下游预览 |

通用算法放在 Pipeline 仓库。本仓库保存校园实例及其内容，通过固定版本的流水线生成资产；不复制一份独立的重建实现。

## 目标闭环

```text
经核验的地理数据 + 自采照片
  → 通用重建流水线
  → 可编辑 Blender 资产库
  → GLB/glTF + 地理元数据 + 场景清单
  → Three.js / Godot / Unity / Unreal
```

`.blend` 保存可编辑源资产；GLB/glTF 是优先交换格式。Three.js 只消费导出物。游戏引擎中的交互、碰撞配置和导航由各自适配层负责。

## 第一个里程碑

围绕 Memorial Quad 选择约 300 × 300 米的试验区，先完成地形、建筑白模、独立资产导出和浏览器检查，再逐栋提高精度。这个范围是规划切片，实际边界与坐标原点尚未确定。

## 数据与发布约束

- 按后续对话决定，排除 UO 内部 GIS，不以申请校方数据作为前置条件。
- 优先调查 USGS 3DEP、DOGAMI OLC、USDA NAIP 和自采照片；具体数据集的覆盖、日期、坐标与使用条件仍需逐项确认。
- 第一版不纳入 OSM、Microsoft Building Footprints、Oregon 汇编建筑轮廓、Eugene City GIS 或 Google Maps/Earth 3D 作为核心资产来源。
- 仓库当前保持 private。GitHub Pages 是未来可选部署目标，目前没有启用、发布网站或上传资产。
- 代码与资产的许可证尚未选定；项目名称中的 “Open” 不代表已授权公开分发。

## 项目文档

- [架构与资产约定](docs/architecture.md)
- [首个闭环与后续路线](docs/roadmap.md)
- [原始讨论与最终决策](docs/source-discussion.md)
- [数据目录说明](data/README.md)

规划来自 [UO校园三维建模技术 — 分享对话](https://chatgpt.com/share/6ae54fb0-e6cc-83e8-8958-51a084c6b7cb?ogimg=plain)，已于 2026-10-30 读取完整的五轮讨论。
