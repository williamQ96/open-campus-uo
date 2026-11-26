# 校园四处场地的树木配准与净空核对

2026-11-24。本地预览依据校方树木台账、2024 航片和 Knight Campus 竣工资料细化局部植被。树木位置使用台账坐标，树高、冠幅及枝叶形态为近似。Knight Campus 东南侧的四株使用通用阔叶树形，树种资料仍待核。范围内的第三方影像只用于对照。

| 场地 | 本地模型更新 |
| --- | --- |
| Knight Campus | 撤下三株与两栋楼相交的背景程序树。Building 1 东南侧按校方位置重建 7254、7256、7257 和 7259。按现场带宽和立面净空收窄部分南北冠幅。 |
| Kalapuya Ilihi Hall | 撤下南翼屋面内与东侧铺装上的两株错位程序树。按 7074–7076 三个登记点重建 Vine Maple 种植组。 |
| Oregon Hall | 将穿入西立面的一株程序树替换为四株按 5825–5828 登记的 Norway Maple。 |
| Gerlinger 与 EMU | 将试点树 18、262 和 177 配准到 Japanese Maple 802、Katsura 800 和 American Elm 6353。Gerlinger Field Green 的航片显示树 147 所在点为开阔草地，撤下该程序树。 |

Knight Campus Building 2 的 2024 航片显示施工期轮廓。校方资料确认该楼在 2026 年 3 月 30 日开放，原程序树 58 的位置位于竣工建筑内部。 [Knight Campus 年度报告](https://knightcampus.uoregon.edu/annual-report-2026) · [校方树木登记图层](https://fass-ig-web1.uoregon.edu/arcgis/rest/services/DistributedEdit/CampusTrees/FeatureServer/0) · [2024 州航片](https://imagery.oregonexplorer.info/arcgis/rest/services/OSIP_2024/OSIP_2024_SL/ImageServer)。

[场地植被生成器](../scripts/build-site-planting.py)、[试点树配准](../data/metadata/registered-pilot-trees.json)与三份场地配准记录包含可编辑尺寸、源锚点、照片链接及哈希。新植被随场地包通过源索引校验后加载。锚点错误时回到该场地的原外部和树木。

## 核对结果

- 以 519 个有效建筑轮廓筛出 23 个可能重叠的树位。逐处核对当前三角网格，发现 17 个表面相交案例。本批消除了其中七个。其余候选保留待复核。
- 新增 11 棵登记树。树干到最近建筑轮廓至少 1.352 米，到已核对路线边至少 14.691 米。新树与所在场地建筑网格的表面相交检查无命中。Gerlinger 的树 18 由 54 对相交三角面降到零。
- 批次撤下六株背景树的 1,440 个索引。三份场地包保留既有建筑和铺装表面。Kalapuya、Oregon 导出文件中的部分三角面排序发生变化，Jaqua 重新剖分了 12 个共面三角面，核对后的覆盖面相同。
- 核对五组前后视图、桌面和移动运行、519 个建筑选择和入口数据、407 个源批次成员、139 段道路以及 17 处原屋面处理。已配准的试点树从 8 株增为 11 株。
- 现有两个程序化乔木源层仍各有 300 株。实际显示 273 株试点树和 270 株背景源树。另有此次启用的 11 棵场地树及先前已配准的 Moss Street 水栎。
- 本次为植被组的局部细化。户外台账有 114 项 L2 和 418 项独立 L1，植被组仍为 L1。未提交、推送或发布。
