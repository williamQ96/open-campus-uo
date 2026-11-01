[English](README.md) | **简体中文**

# 图片与照片素材目录

本目录是 Open Campus: UO 持续维护的素材原件库，当前包含 **9 张开放许可的地面照片、2 张有日期的 USDA NAIP 航拍图、5 张项目设计图和 1 张 CC0 角色皮肤纹理**。保存下载字节；航拍记录明确服务端拼接／裁剪、重采样与重投影。原设计／运行文件保持原位，台账链接相同字节副本。Gerlinger Hall／Annex 扩充建筑照片；第二张航拍覆盖完整 2 × 2 公里，用于推断地面材质。

- [manifest.json](manifest.json)：逐图文件、作者、来源／下载链接、拍摄／访问／核验日期、许可依据、用途／建筑 ID、修改、SHA-256 与字节数。
- [ATTRIBUTION.md](ATTRIBUTION.md)：每张图的署名和许可链接。
- [evidence.json](evidence.json)：来源声明摘录和人工核验记录。
- [原 v0.6 建模参考记录](../metadata/visual-pilot-references.json)：保留历史引用及不分发的原因。
- [上游通用规范和校验工具](https://github.com/williamQ96/open-geospatial-to-3d-reconstruction-pipeline/blob/main/docs/zh-CN/reference-media.md)。

## 照片与用途

| 建筑 | 归档内容 | 时间与限制 |
| --- | --- | --- |
| [Knight Library](photos/knight-library/) · `roof-6684e091` | 历史北立面两个斜视角、外墙灯具细节 | 立面 2018-07-11；灯具 2017-06-26。第二张并非独立侧立面测绘。 |
| [Johnson Hall](photos/johnson-hall/) · `roof-906c030e` | 正面柱廊、背面入口 | 背面 2012-07-25；正面拍摄日期未知，2006-06-06 是上传日期，不能当作拍摄日期。 |
| [Erb Memorial Union](photos/erb-memorial-union/) · `roof-266f13fd` | 历史 University Street／Fishbowl 入口、修缮后外观 | 2013-10-19 入口属于 2016 修缮前；2017-11-03 外观不代表 2026 现状。 |

这些照片已用于 [v0.7 模块化地标细化](../../docs/zh-CN/visual-refinement-v0.7.md)。最初建图库没有重生成 v0.6，其[历史报告](../../docs/zh-CN/visual-pilot.md)仍保留；之后 v0.7 依据本图库和 [2024-06-08 NAIP 航拍](aerial/naip-2024-pilot-rgb.png)重新生成美术层，尺寸仍为近似，无照片贴图。[精确导出请求／地理参考](../metadata/naip-2024-reference.json)随 PNG 单独保存。

## 设计图片与输出

[project](project/) 保留未经修改的 AI 概念图和 Open Courtyard 品牌图。概念图只说明画风，不是校园照片、实际模型截图或地理数据；AI 来源与权利范围见台账和[原始设计来源](../../design/architectural-toon-realism/provenance.json)。标识生成源码在 [design-logo.py](../../scripts/design-logo.py)。

v0.6 与 v0.7 运行截图留在 [docs/images](../../docs/images/)，以 `related_outputs` 单独登记，不混作照片输入。设计档案、原品牌 PDF、调色板保留原位置。本素材库位于网页 `public/` 之外，不增加网页运行下载量。

## 许可与后续接收

第三方照片按各自 **CC BY 4.0、CC0 或 PD-self** 保持原状；USDA 航拍按明确声明的公有领域状态记为 `LicenseRef-PD-USGov`，不统一重授项目许可。按要求署名 Gary Halvorson／Oregon State Archives、Rick Obst；公有领域照片也记录 Daderot、Adam850 便于追溯。原创设计按[项目协议](../../LICENSING.zh-CN.md)中拥有权利的范围提供，不授予商标权或机构背书。

此前参考过的 3 张 UO 官方照片尚未确认公开分发许可，**只保留历史来源链接**、排除状态和替代素材 ID，不把照片字节或贴图放进公开包。用户提供的 Google Maps 卫星截图仅说明关注区域，没有导入、描摹或作为模型／贴图来源，也没有导入 Google 瓦片或三维资产。

以后采用图片前，先确认允许开放分发、修改和资产导出，再保存原件、逐图登记。避免授权不明、NC、ND 和平台受限素材，使用许可明确的替代来源。记录原图／修改版本关系；新增图片或用途时同时更新台账和署名，并检查衍生资产的适用条件。日期、朝向、修缮前后与近似限制也是参考依据的一部分。

## 核查

在本仓库根目录、准备好上游 checkout 后：

```powershell
python ../open-geospatial-to-3d-reconstruction-pipeline/scripts/check-reference-media.py --root .
```

CI 的 `reference-media` job 固定上游校验工具 commit，检查图片登记、字段与 hash 一致性；不能替代人工授权判断或建筑精度核验。本次不更改独立的重建锁与 viewer 运行时锁。

## 完整场景地面参考

[2024-06-08 全场景 NAIP 拼接图](aerial/naip-2024-main-campus-rgb.png)用于[本地迭代 13](../../docs/zh-CN/phase13-environment-comfort.md)，[两幅源图、导出请求和地理参考](../metadata/naip-2024-main-campus-reference.json)另存。运行时仅使用原创调色／顶点色材质，不把照片当纹理。这是有日期的航拍，不是实时卫星地图。
