# Chi Omega 与 Delta Delta Delta 外部拆分核对

2026-11-24。本地默认场景将原来合在 `roof-c85e8e54` 的两栋社团建筑拆为独立外部。两栋均按 Knight Library 样例核对比例、可辨识构件、可编辑来源与默认场景行为，审核为 L2。

| 场景 ID | 建筑及边界 | 可见特征 |
| --- | --- | --- |
| `roof-c85e8e54` | Delta Delta Delta House，851 E 15th Ave，州轮廓 1841240 | 两个主屋脊、低后翼、浅色横板、深色窗板、带方柱的南门廊和三个三角饰件。沿用原场景 ID。 |
| `state-1841241` | Chi Omega House，1461 Alder St，州轮廓 1841241 | 红砖、高低交叉坡屋顶、露天后翼屋面、双烟囱、西侧凸窗、石饰拱门与金属雨棚。用州轮廓编号登记独立 ID。 |

原 919.5 平方米候选与两个州轮廓分别重叠 517.863 和 289.286 平方米。州轮廓、市政门牌、税地和 2024 航片支持各自的物理边界。Chi Omega 的国家名录场地页和外部描述支持屋脊、砖砌山墙、两种凸窗和雨棚。2024 街景支持后翼板饰与 Delta Delta Delta 的南立面。开窗净尺寸、局部饰件、未清楚可见的后侧细节和实地门槛为近似。[校方地址](https://blogs.uoregon.edu/uofsl/chapterhousesmap/) · [Chi Omega 国家名录](https://npgallery.nps.gov/GetAsset/2f3c9521-f2e5-4d45-a6af-8b985782121a#page=35) · [州电影办公室外观资料](https://rs.locationshub.com/location_detail.aspx?id=051-10037903) · [Delta Delta Delta 街景](https://www.google.com/maps/@?api=1&map_action=pano&pano=SujA5J7XDeg5krYm1rJ75w&viewpoint=44.043329%2C-123.0794384&heading=0.11)。

[可编辑配准与来源](../data/metadata/chapter-house-exterior-review.json)记录两组轮廓、分段屋面、接近点、资料哈希和拆分关系。原创几何由[生成脚本](../scripts/build-chapter-house-exterior-review.py)导出。加载器校验新增 ID、原候选、原批次范围与登记地址的对应关系。描述文件与源锚点核对完成后同时加载两栋。错误包恢复以前的合并候选。

## 验证

| 2017 高程比较 | 原模型命中与误差中位数 | 新模型命中与误差中位数 |
| --- | ---: | ---: |
| Delta Delta Delta | 502 / 510，0.705 米 | 510 / 510，0.074 米 |
| Chi Omega | 288 / 402，0.875 米 | 402 / 402，0.137 米 |

- 两期共比较 1,824 个屋面采样点。以上 2017 数值是与拟合参考的对照。两栋各有高低屋面验证点，另有六组前后视图。
- 原批次移除 880 个固定三角面，逐项校验保留顶点属性、索引与 12 个邻近候选 ID。
- 检查 7,710 条路线边。两栋分别可搜索和到达，两处原合并网格封堵的通道点允许通过。最近模型与路线边距离 2.853 米。
- 桌面和移动端保留 516 个建筑选择、410 个源批次成员、139 段道路、550 株树和 17 个独立屋面处理。破损网格、地形哈希异常、末段锚点异常和错误拆分关系的回退经过核对。
- 台账有 108 项 L2、421 项独立 L1 和 21 条历史映射。本地更新未提交或发布。[室外台账](asset-refinement-inventory.md)。
