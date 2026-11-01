# 校园扩展：照片语法与柔化背景

[English](../campus-expansion.md) | **简体中文**

2026-10-31，校园扩展批次。继续 Architectural Toon Realism，提炼建筑特征与重复规律，允许合理推测，精度由长期纠正提升，不追求照片级复制。

- **重点建筑：**Knight Library、EMU、Johnson Hall 保留原模型并补浅浮雕、窗格／雨棚、窗台等构件；新增细化 Gerlinger Hall 与 Gerlinger Annex 的山花、雨篷、拱窗、圆形装饰及老虎窗。
- **校园重点区：**135 个历史建筑记录采用砖／石色板、简化屋顶、重复窗格与入口；该区域是可编辑的艺术优先级范围，不是官方校界。
- **外围背景：**399 个记录使用原创可开源 low-poly 住宅／低层楼／仓库构件，按稳定 ID 固定随机类型、屋顶和配色，减少窗格细节。

**随机只改变外观，不改变建筑位置。**534 个记录的原始 ID、占地轮廓、基础／屋顶高度记录、道路与街区结构均保留。原地形、导航图和碰撞目录不改变；这不意味着旧数据的年代或精度得到提升。

新增两张 Rick Obst 于 **2013-10-19** 拍摄的 **CC BY 4.0** 原照，原样归档，并与 Commons 的原文件 SHA-1 校验一致。[Gerlinger Hall](../../data/reference-images/photos/gerlinger-hall/exterior-2013.jpg) 提供对称窗列、砖立柱、三角山花、酒红雨篷；[Gerlinger Annex](../../data/reference-images/photos/gerlinger-annex/exterior-2013.jpg) 提供高拱窗、浅色上部、圆形装饰与重复老虎窗。立面朝向、模块数量、尺寸和隐藏面仍为推测。来源、许可、下载地址与校验值见[证据](../../data/metadata/campus-expansion-photo-evidence.json)和[素材署名](../../data/reference-images/ATTRIBUTION.md)。照片不作为贴图嵌入运行模型。

保留原 300 棵 NAIP 引导的示意树，另增加 300 棵程序化推测的树与校园草地；新增部分不是从新航片提取的树木清单。

Settings → Display → **Background haze** 默认开启：重点区清晰，外围在 210 米过渡区内渐进降饱和度、降低对比并染上淡雾色。效果依赖固定世界区域，镜头移动不会让边界跟随。雾化属于浏览器显示，GLB 保留标准 PBR。通过顶点插值和合并背景网格控制成本：470 个匿名记录合并成 21 个运行时网格，保留全部身份；64 个建筑组仍可独立选择，包含全部 63 个已命名建筑。模型约 25.4 MB，比旧 14 建筑试验区更大；一次软件渲染总览观测为 209 draw calls，不据此承诺硬件帧率。

可编辑模型位于 `assets/campus-expansion/eugene-campus.blend`，GLB 位于 `apps/web-preview/public/scene/campus-expanded.glb`；旧试验区 Blender 保持不变。参数、逐建筑选择和审计见英文文档。新艺术层如实记录本地未提交的方法版本；历史重建与旧模型来源不改写。更新前保留手动编辑。

Blender 源文件保留 534 个可独立编辑的建筑对象，共 542 个源网格；仅在导出时合并副本，运行模型为 93 个网格。

发布状态见开发日志；本批将运行时锁提升到已提交上游版本，艺术层仍保留真实生成时的方法哈希及 dirty 状态，不假装重建。项目开发日志只在下游维护，通用方法在上游单独记录。
