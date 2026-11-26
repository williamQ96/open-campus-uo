# Villard Street 与 Garden Avenue 六栋住宅外部核对

2026-11-24。本地默认预览将三个跨门牌的旧候选拆为六栋。州轮廓、市政地址点、独立税地和 2024 年航片核对建筑分界。按 Knight Library 项目样例逐栋检查形体、主要立面、比例、材质、可编辑来源和场景行为后，六栋登记为 L2。

| 外部模型 | 场景 ID | 核对的特征 |
| --- | --- | --- |
| 1848 Villard St | `roof-5d371770` | 低四坡屋面、突出的入口、浅色横饰和北端车库。 |
| 1878 Villard St | `state-1841280` | 交叉屋脊、两组临街山墙、带柱门廊和砖烟囱。 |
| 1989 Villard St | `roof-a0566b7b` | 浅黄横板、两段临街坡顶、低雨棚及车库门板。 |
| 1991 Villard St | `state-1830735` | 深色四坡顶、两处天窗、灰色横饰、前廊红门和不等宽窗带。 |
| 1923 Garden Ave | `roof-3ce27cdc` | 分段浅坡屋面、灰色竖条板、长方窗、东侧外楼梯和平台。 |
| Treetops Apartments，1933 Garden Ave | `state-1841318` | 两翼带小山墙的凸窗、中央内退入口、棕色檐饰及河侧阳台。 |

Villard 两组以 2024 年 7 月街景为立面参照。另用校方登记核对 1848 的门牌和历史编号，用 2019 年房源外观照确认 1878 的双山墙和砖烟囱。1923 的街景和房源外观照显示竖条立面和楼梯。Treetops 的名称、立面、入口及河侧阳台由物业资料确认。局部开窗、门槛、遮挡处的立面、1923 楼梯踏步及河侧阳台尺寸按现有证据估算。模型使用原创几何和颜色，照片只作参照。 [Villard 北段街景](https://www.google.com/maps/@?api=1&map_action=pano&pano=5utOjbzI32nHfVfKoDcp-w&heading=281) · [Villard 南段街景](https://www.google.com/maps/@?api=1&map_action=pano&pano=_m4HxUvpUp3pwnOpyQSmdQ&heading=90) · [1923 Garden 外观](https://www.zillow.com/homedetails/1923-Garden-Ave-APT-4-Eugene-OR-97403/453861709_zpid/) · [Treetops 物业资料](https://www.mallardproperties.net/portfolio)。

[可编辑配准](../data/metadata/villard-garden-exterior-review.json) 记录源哈希、分段屋面、立面参数、拆分关系和入口。几何用[生成脚本](../scripts/build-villard-garden-exterior-review.py)导出。三条原 ID 分别保留给 1848 Villard、1989 Villard 与 1923 Garden。另三栋各自用州轮廓号登记。校验三段源网格后，查看器同时加载六栋。

## 核对结果

| 2017 年屋面参考 | 旧模型命中 | 新模型命中 | 绝对高差中位数，旧 → 新 |
| --- | ---: | ---: | ---: |
| 1848 Villard | 124 | 141 | 0.670 → 0.370 米 |
| 1878 Villard | 111 | 173 | 1.620 → 1.023 米 |
| 1989 Villard | 129 | 160 | 0.852 → 0.394 米 |
| 1991 Villard | 53 | 78 | 0.742 → 0.275 米 |
| 1923 Garden | 365 | 423 | 0.508 → 0.363 米 |
| Treetops | 325 | 361 | 1.868 → 0.332 米 |

- 两期共核对 2,749 个屋面射线和七组前后渲染。原模型与新模型的中位数按各自命中点计算，2017 年表格使用建模参考数据。1878 Villard 和其他树冠覆盖处的高差仍较大。
- 三个源批次合计移除 1,800 个三角面。保留的顶点属性、索引及 104 个源批次邻居逐项一致。
- 核对 7,710 条路线边、六处可到达入口与九个碰撞点，三个原先封闭的点现在可通过。默认场景有 519 个建筑选择、407 个源批次成员、139 段道路、550 株树和 17 个独立屋面处理。
- 本地生产预览验证损坏的模型、错误地形哈希及第三段源锚点异常均回退到三个原候选。分阶段、启用与重复导出的网格和描述文件逐字节一致。
- 室外台账有 114 项 L2、418 项独立 L1 和 21 条历史映射。此次变更留在本地，未提交、推送或发布。 [室外台账](asset-refinement-inventory.md)。
