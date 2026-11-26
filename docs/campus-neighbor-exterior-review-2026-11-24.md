# 校园周边七栋外部核对

2026-11-24。各栋对照 Knight Library 外部的比例、辨识度、主要构件、场景衔接和可编辑来源审核为 L2。

| 场景 ID | 名称与地址 | 建模及证据 |
| --- | --- | --- |
| `roof-4286ad30` | Coho Townhouses 南排，633 E 14th Ave | 南北屋脊、横木板、金属窗舱和南端首层后退门廊。沿用原有北排 ID 和独立入口关系。[市政住宅清单](https://www.eugene-or.gov/AgendaCenter/ViewFile/Item/3?fileID=10) |
| `roof-2cbfcd06` | Pi Kappa Alpha House，1472 Kincaid St | 复建高低两翼和东院，南侧采用通窗，北翼采用面向院子的窄窗格。大学登记确认现名；市政旧照片反映早期立面。[学校地址](https://blogs.uoregon.edu/uofsl/chapterhousesmap/) · [市政建筑调查第 178 页](https://www.eugene-or.gov/DocumentCenter/View/24803/Eugene-Modernism-1935-65#page=178) |
| `roof-e17be27c` | Christus House，1834 Potter St | 保留 L 形两翼、高低屋顶和低翼两排光伏。临院面重建窄雨棚与砖烟囱，旧市政照片所标门牌为 1830 Potter。[市政建筑调查第 177 页](https://www.eugene-or.gov/DocumentCenter/View/24803/Eugene-Modernism-1935-65#page=177) |
| `roof-f89a9211` | St. Thomas More Newman Center，1850 Emerald St | 依据 2024 年街景重建 Emerald Street 的陡斜屋面、四处白边窗罩、绿色玻璃入口和屋檐标记。高位平顶仍有原拟合约束。[教堂官网](https://www.uonewman.org/visit.html) |
| `roof-cea1e466` | Hayward House Apartments，1290 E 18th Ave | 保留东西向双坡屋顶。加入两层临街外廊、钢栏杆、入口阶梯和外廊下的架空停车位。[物业资料](https://www.apartments.com/hayward-eugene-or/h0dg2e0/) · [校方现场调查](https://darkwing.uoregon.edu/~schlossb/papers/Yanik_bikeparking.pdf#page=12) |
| `roof-04683fef` | Aldersgate Apartments，1436 Alder St | 复建蓝色端墙、三层南外廊、交错外梯以及架空停车层。尺寸根据航片及 2024 年照片估算。[校方现场调查](https://darkwing.uoregon.edu/~schlossb/papers/Yanik_bikeparking.pdf#page=12) |
| `roof-5e7ce49c` | The 1840，1840 Agate St | 两段平屋面、深红色门和栏板、暖色外墙及临巷黑格栅楼梯。东翼标高沿用原拟合。[历史建造记录](https://oregonnews.uoregon.edu/lccn/sn85042472/1962-01-04/ed-1/seq-12.pdf) |

[配准文件](../data/metadata/campus-neighbor-exterior-review.json)保存七处 2024 年航片的请求和哈希、2024 年街景链接、原模型和屋面来源。重建源是[生成脚本](../scripts/build-campus-neighbor-exterior-review.py)与该配准文件。外部包由原创几何组成。背侧开窗、材料细部与入口实地尺度为近似。

## 验证

- 核对 14 组前后视图、11,779 个保留屋面射线点。六栋经过核对的原拟合屋面与新模型交点在浮点精度内一致，另核对 Christus House 新烟囱的标高。Newman Center 高位屋面保留原平顶标高，边饰采样差最大 0.205 米，临街斜面另测。
- 检查 7,710 条路线边，模型和路线最小距离约 3.418 米。东院和架空地面保留通道，七处建模接近点在桌面端和触屏可达。
- 用四个源批次的原始锚点删除七段共 1,656 个三角面，逐项核对其余顶点属性、索引与场景 ID。破损网格、地形哈希异常和最后一段源锚点异常均恢复先前场景。
- 默认场景有 515 个可选建筑、411 个源批次成员、139 段道路、550 株树和 17 个其余独立屋面细化。重复导出及生产包经过哈希比对。室外台账有 106 项 L2、422 项独立 L1 和 21 条历史映射。[室外台账](asset-refinement-inventory.md)。

本次更新仅在本地。
