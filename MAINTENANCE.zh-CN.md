[English](MAINTENANCE.md) | **简体中文**

# 长期维护约定

首轮优先完整、可辨识场景，允许明确记录且可编辑的合理推测；精细和写实程度通过长期纠正提高，不以完整扫描或照片级还原阻断可用首版。见 [v0.7 纠正记录](docs/zh-CN/visual-refinement-v0.7.md)和[上游方法](https://github.com/williamQ96/open-geospatial-to-3d-reconstruction-pipeline/blob/main/docs/zh-CN/progressive-modeling.md)。

采用的图片／照片原件统一维护在 [`data/reference-images/`](data/reference-images/README.zh-CN.md)，随资产修改更新作者、许可、日期、用途、署名和 hash。使用允许开放分发、修改与导出的来源；保留历史排除记录并选择许可明确的替代素材。通用规范／校验工具放上游，CI 固定其版本，与重建锁、viewer 运行时锁独立。

上下游均持续维护，仓库现均为 public。上游负责通用重建方法、自动化、验证、交换格式与浏览器模板；下游负责具体地图的数据、身份、模型、材质、品牌与细化。

重建锁与 viewer 模板锁独立。推进重建版本前先做小区域比较；模板升级按旧文件 hash 核查，拒绝覆盖本地共享代码修改，保留项目数据和部署身份。自动白模不得覆盖人工精细资产。通用修复返回上游，地区特定修正留在下游。

代码／模板代码采用 Apache-2.0，原创文档和原创模型／设计贡献采用 CC BY 4.0；保留 NOTICE、署名与第三方条款，见[协议说明](LICENSING.zh-CN.md)。独立地理精度、其他地区与引擎、任意 CRS、增量重建和 LOD 仍按证据逐步实现。
