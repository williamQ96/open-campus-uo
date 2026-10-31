# 原始讨论与最终决策

来源：[UO校园三维建模技术](https://chatgpt.com/share/6ae54fb0-e6cc-83e8-8958-51a084c6b7cb?ogimg=plain)。2026-10-30 已读取完整五轮讨论。本文件保留项目相关结论，不复制对话中的个人资料或邮件草稿。

## 讨论演进

1. 调查 GIS、LiDAR、摄影测量、3DGS 等校园重建技术。
2. 曾讨论 Unreal 可探索校园，但后续明确调整为跨引擎通用资产。
3. 用户要求以 Blender 资产库为核心，支持 Godot、Unity、Three.js 等下游，并先完成可重复的端到端闭环。
4. 用户拒绝依赖可能限研究教学用途的 UO GIS，要求替代资源。最终路线变为核验公开地理数据，并独立提取建筑轮廓与几何。
5. 用户要求浏览器预览；讨论提出 Three.js + Vite 与未来 GitHub Pages 部署。

## 当前生效的范围

- 通用重建工具与 UO 校园资产实例分成两个仓库。
- Blender 为主要创作环境，GLB/glTF 与元数据负责跨引擎交付。
- 先做 Memorial Quad 小切片，再逐区域、逐建筑迭代。
- UO 内部 GIS 不作为依赖，也不执行原讨论中的邮件申请。
- 初版核心资产不使用 OSM、Microsoft/Oregon 汇编建筑轮廓、Eugene GIS 或 Google 3D 数据。
- Three.js 消费流水线导出结果；3DGS 是可选增强。
- 按本次创建请求，两个仓库均保持 private；尚不公开发布。

## 候选入口与证据边界

原讨论提出 [USGS 3DEP](https://www.usgs.gov/3d-elevation-program/about-3dep-products-services)、[DOGAMI LiDAR](https://www.oregon.gov/dogami/lidar/pages/help.aspx)、[USGS 数据下载入口](https://www.usgs.gov/the-national-map-data-delivery/gis-data-download)及 [EarthExplorer](https://earthexplorer.usgs.gov/)。v0.1 已完成实际数据下载与核验，记录在 [source-audit.json](../data/metadata/source-audit.json)；采用 NOAA 托管的 DOGAMI 点云，排除 AOI 全 NoData 的 DEM。

原讨论中的版本号、价格、性能目标、数据许可和部署额度属于讨论时的建议或外部信息，未作为本项目已验证事实。具体数据、工具和托管方案在实际采用时重新核验；不把早期 Unreal/GIS 方案覆盖后续用户决定。
