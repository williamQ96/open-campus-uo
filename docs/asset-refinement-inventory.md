# Open Campus: UO 资产精细化清单

更新于 2026-11-26。清单记录本地模型与后续工作，发布状态另记。

## 等级和适用范围

- **0 级**：仅白膜。
- **1 级**：简单渲染。项目原先以此作为 Knight Library 以外现有资产的基线。
- **2 级**：以用户指定的 Knight Library 外部为项目比较样例。已列入 L2 的外部逐栋核对体量、主要立面、场景整合与模型验证结果。
- **3–5 级**：上游已记录正式定义。L3 使用平面图或简单图片并结合推断，L4 对照真实照片并允许合理推断，L5 对照真实照片或建模数据力求接近完全复现。评级方式见[上游等级及适用范围](https://github.com/williamQ96/open-geospatial-to-3d-reconstruction-pipeline/blob/main/docs/zh-CN/asset-refinement-inventory.md#等级及适用范围)。
- **空白等级**：资产尚未创建或等级不适用。空白不是 0 级；未创建的单栋室内不能算作已经完成白膜或 1 级。

## 清单与统计

[打开可筛选的 CSV 明细](asset-refinement-inventory.csv)（UTF-8 BOM，适合电子表格）。每行包含稳定 ID、区域、资产类型、名称、存在状态、等级、证据路径、下一步和未知事项。 状态代码与母仓库模板一致：`existing` 表示现有，`planned` 表示待创建。所有 `INT:` 计划项目前仍使用共用教室作运行时回退。

| 范围 | 明细行 | 当前状态 |
| --- | ---: | --- |
| 建筑外部及独立室外设施 | 664 | 610 项 L2、0 项独立 L1、54 项停用或并入模型的 L1 历史记录 |
| 各建筑独立内部 | 663 | 均标为未创建，等级留空，当前进入时使用共用教室 |
| 室外植被、景观、道具及角色动物 | 15 | 15 组 L2 |
| 共用室内 | 1 | 现有 L1 共用教室 |
| **合计** | **1,343** | **680 项现有，663 项独立室内待创建** |

源场景的 534 个建筑候选包括 64 个独立节点和 470 个批次成员。科学楼群配准增加了 Pacific 和 Columbia 两个场景 ID，社团建筑拆分增加了 Chi Omega 的独立 ID，Villard 与 Garden 住宅拆分增加了三个独立 ID，大学区南停车楼拆分增加一个独立 ID，973 Hilyard 新增一个此前缺失的建筑 ID，1515 Hilyard 合并候选拆分增加两个独立 ID，957/971 Hilyard 拆分增加一个独立 ID，E 15th 巷侧楼、950 Alder Suites 和 1125 Alder 校方设施维护楼各新增一个此前缺失的建筑 ID。区域字段沿用项目艺术优先区及背景制作分区。部分记录可能对应同一建筑、树冠或其他候选，需要逐项确认。

项目现有一套通用教室，所有建筑暂时使用该模板。CSV 的 `INT-SHARED` 为共用模板 L1，每个 `INT:建筑ID` 为待建的专属内部，等级留空。[通用教室](../assets/interiors/README.md)。

两个程序化乔木源层各含 300 株。本地默认预览显示试点区 273 株及背景源树 253 株。Pioneer Cemetery 另有 121 个按高程及航片估算的树冠。Knight Campus、Kalapuya Ilihi 和 Oregon Hall 保留 11 株按台账建模的场地树，Moss Street 另有配准水栎。[植被核对](outdoor-tree-registration-2026-11-24.md)。种植现状、尺寸及入口标高仍待实地核对。资料优先使用已获许可的照片与公开资料，记录来源、日期、使用权和待验证尺寸。

## 室外 L2 目标核对

景观已按地点与构件建立单独的覆盖核对。首批 Pioneer Cemetery 的八条主路、东入口台阶、石牌、纪念碑和部分墓碑及植被已经在本地验证。其他景观继续按道路、雕塑、标识、花坛、植物及构筑物逐处核对。[室外景观台账](landscape-l2-inventory.md) · [Pioneer Cemetery 复核](pioneer-cemetery-landscape-review-2026-11-26.md)。

室外目标追踪 679 条记录，包括 664 条建筑外部及独立室外设施和 15 个植被、景观、天空、道具及户外活动资产组。共用教室和 663 条计划室内记录另列。当前有 610 项 L2 外观、15 组 L2 室外资产，独立在用 L1 为 0 项，另保留 54 条合并或停用后的历史映射。历史映射涉及 Garden、Franklin、Millrace、Villard、1261 Alder 旧住宅、旧 Sacred Heart 医院地块、EMU、Frohnmayer、Hendricks、Lawrence、Earl、Moss Street、Walton、Lillis、PLC、Lokey Education、东北科学楼群、Knight Campus、Hayward Field、Central Lutheran Church、The Studies at 19th、1544 Alder 的旧局部、Walnut Path 步桥旧网格、967 Patterson 旧建筑、Arena 前广场、Walnut 停车区、铁路跨线桥、储冷罐地块、Knight Library 西侧草坪、Grace Lutheran Church 旧分段、Hamilton Hall 五段已拆网格、Franklin 沿线两处停车区旧网格及 Patterson 原 YMCA 已拆网格，原 ID 和等级记录保存在 CSV。默认场景有 610 个可选建筑及独立设施。评级按项目样例逐项核对形体、主要可见细节、比例与材质、可编辑来源和验证结果。[上游等级说明](https://github.com/williamQ96/open-geospatial-to-3d-reconstruction-pipeline/blob/main/docs/zh-CN/asset-refinement-inventory.md#等级及适用范围)。

Alpha Omega House、Fire Station 13、Birch 和 Fairmount 一带三栋住宅及 634–640 East 16th Alley 完成 L2。Patterson 旧 YMCA 归入历史映射，现状开敞地和铺装纳入 ENV-05。桌面和手机均已逐项核对 610 个默认可选建筑及独立设施的 ID。[最后一组外观复核](neighborhood-exterior-closeout-2026-11-26.md)。

959 Franklin、Hayward Inn 的 Franklin 屋翼及 Best Western New Oregon 的两处建筑外部完成 L2。两处露天停车区旧屋面转入历史映射，铺装纳入 ENV-05。[外部核对](franklin-riverfront-closeout-2026-11-26.md)。

Hamilton Hall 旧址现为 Great Lawn 和 Duck Dunes。三片沙排球场及草坪步道记入 ENV-05，1680 East 13th Avenue 配套用房成为独立 L2 外观。五段旧建筑归入历史映射。[现场与模型核对](hamilton-great-lawn-duck-dunes-2026-11-26.md)。

Alder 和东 12 至 14 街再完成十四栋外观。Patterson 保留抬高中庭和南露台，The Ellis 与 Chapter at Eugene 独立建模，751 East 14th 的三栋小屋保留物理间距。[十四栋外观复核](east-thirteenth-blocks-review-2026-11-26.md)。

Alder、Kincaid 和东 16 至 18 街的 20 栋新增 L2。Grace Lutheran Church 恢复连续屋面、露天庭院和带柱檐廊。Camelot、Talisman 和 The Arcade 的开放空间已保留。[西侧复核](west-alder-kincaid-exterior-review-2026-11-26.md)。

Riverfront Parkway 恢复四跨铁路桥、三座桥墩和桥下连续铺面。储冷罐作为独立室外设施纳入 L2，Knight Library 西侧草坪恢复可通过。[室外设施复核](riverfront-plant-infrastructure-exterior-review-2026-11-26.md)。

Villard、Orchard、Moss、Walnut 和东 15 街十栋建筑完成 L2。Courtside 与 Skybox 保留露天庭院，1530 Orchard Alley 和 1365 Villard 保留有顶开放空间。Arena 前广场和 Walnut 停车区恢复铺地。[东侧复核](villard-orchard-walnut-exterior-review-2026-11-26.md)。

东 20 至 21 街八段旧网格重建为 13 栋 L2 外观。2090 Hilyard 两条市政记录对应一栋，五处原连体分别设 ID，2028 Kincaid 保留带双柱的可走入门廊。[南侧外观复核](south-university-east-twentieth-exterior-review-2026-11-26.md)。

Patterson、Hilyard 和东 11 街七处建筑完成 L2。967 Patterson 的 Sigma Phi Epsilon 会所另设 ID，保留已拆旧屋面的历史记录。1050 与 1052 Hilyard 和 751 与 755 East 11th 的门牌分别共用一栋模型。[西侧外观复核](patterson-hilyard-exterior-review-2026-11-26.md)。

Bardell、Buckingham、Chevy Chase 和 Merewether 周边 18 栋住宅完成 L2，保留 3370 Bardell 的连接屋翼及 592 Merewether 跨出东侧地形的屋面。Walnut Path 运河步桥纳入 ENV-05，旧建筑网格存为历史映射。[住宅与步桥复核](bardell-buckingham-and-walnut-path-review-2026-11-26.md)。

东 12 至 15 街周边二十四栋外观完成 L2。Campus Court 保留两条露天缝，766 East 15th 保留贯通车道，1360 Alder 两翼可独立选择，640 与 745 East 15th 均保留露天庭院。[二十四栋外观复核](northwest-blocks-review-2026-11-26.md)。

Alder 南段、Harris、Kincaid 与东 19 至 20 街周边二十九栋外观完成 L2。1860 Alder 保留露天采光庭，1884 Alder 保留架空停车和露天楼间楼梯，1875 Alder 的两翼保持连通。960 和 980 East 19th 各自可选。[二十九栋外观复核](southwest-exterior-review-2026-11-26.md)。

Hilyard、Alder 和东 14 至 18 街周边二十八栋外观完成 L2。Campus Quads 重建南向通廊和车道开口，Delta Gamma 恢复四柱门廊，648 East 17th 保留露天内庭和东侧停车开口。东 15 街巷两栋现状车库楼按 2025 年航片重配准。[二十八栋外观复核](hilyard-blocks-review-2026-11-26.md)。

Garden、Franklin 和 Millrace 周边十五栋外观完成 L2。2125 Franklin 重建露天泳池庭院与分层停车甲板，2117 酒店保持独立，三栋 Franklin 商铺可分别选择。1769 空地、2125 后侧屋影和两个旧局部网格保留历史记录。[十五栋外观复核](garden-franklin-review-2026-11-26.md)。

Villard、Orchard 和 Millrace 周边十八栋外观完成 L2。1907 Garden 保留建筑下的水道，五组独立屋顶保留间距。East 18th 的旧巷道轮廓停用，小棚另设独立 ID。[十八栋外观复核](villard-orchard-garden-review-2026-11-26.md)。

Fairmount、Sunset 等街区十三栋建筑达到 L2。2285 Parkside 保留露天环形庭院，30 Sunset 保留车棚开口。Walnut 小屋顶从 1820 的旧候选拆出，两个 Rose 门牌继续共用一栋模型。[十三栋外观复核](fairmount-sunset-hillside-review-2026-11-26.md)。

360 与 362 Sunset Drive 原合并为一栋。按各自的市政轮廓和地块拆分后，两栋屋顶相距约 6.166 米，各自可被搜索和选中。360 保留双车库、绿色遮阳篷和高露台，362 重建两层阳台。[Sunset Drive 外观核对](sunset-drive-pair-review-2026-11-26.md)。

Orchard、Villard 与 Fairmount 周边十六栋外部登记为 L2。六处拆分保留实测图上的屋面间距，东 19 街 1978 号恢复开放停车棚，Orchard 1994 号保留两片光伏阵列。Villard 1996 号同地块的独立附属建筑保留单独 ID，其用途待核。[十六栋外部核对](orchard-villard-hillside-review-2026-11-26.md)。

Fairmount、Moss 与 McMorran 周边十一栋外部登记为 L2，新增东 19 街 1836 号和 Fairmount 2241 号。保留 McMorran 2303 号的开放连廊、1911 Moss 的退入式门廊及 Fairmount 2415 号朝泳池的双层露台。1911 Moss 与东 19 街 1820 号仍对应同一个场景 ID。[十一栋外部核对](fairmount-moss-slope-review-2026-11-26.md)。

Columbia、Moss 与 Agate 周边十四栋外部登记为 L2。两家咖啡馆、巷侧楼、两栋 Emerald Apartments 和东 19 街 1445 号可独立选择。Agate 两家店共用雨棚，各有独立门廊。新增 Columbia 2003 号独立外部，并按 2021 年外观照重建 Columbia 1980 号的木瓦外墙和双车库。[十四栋外部核对](columbia-moss-frontages-review-2026-11-26.md)。

Agate 与 Emerald 周边八栋外部登记为 L2。The Studies at 19th 统一两段旧网格并保留两个天井与西侧架空停车。Tom's Market 采用 2024 年临街形态，东 20 街 1460 与 1470 号独立可选。[八栋外部核对](agate-emerald-frontages-review-2026-11-26.md)。

Emerald 与 Onyx 周边十一栋外部登记为 L2。1959 Onyx 西栋和巷侧楼共用门牌但可分别选择。增补 1940 Emerald Alley 的独立外部，分开东 20 街 1405 和 1425 号，并复核 1361 东 21 街门廊、1959 Onyx 巷侧楼梯及四处估算接近点。[十一栋外部核对](emerald-onyx-frontages-review-2026-11-26.md)。

Trinity House 和 Onyx 周边七栋建筑登记为 L2。东 20 街 1256 号和东 19 街 1262 号获得独立 ID，两处屋间隙通过核对。1931 Onyx Alley 西侧架空停车开口保持地面净空，并保留立柱和后墙碰撞。[八栋外部核对](onyx-university-frontages-review-2026-11-26.md)。

南缘八栋建筑登记为 L2。Harris 街 2039 号与 2061 号独立可选，University 街 2028 号后侧体量也设立独立模型。两个间隙与 Potter 街 2086 号关闭的院门通过碰撞核对。[南缘八栋外部核对](southern-boundary-exterior-review-2026-11-26.md)。

Harris、Potter 和东 20 街十栋建筑登记为 L2。六个原 ID 保留，四栋拆分建筑新增独立 ID。四处间隙、1925 Harris 雨棚及 1959 Harris 台阶与挡墙均通过碰撞核对。[十栋外部核对](harris-potter-exterior-review-2026-11-26.md)。

Central Lutheran Church、东 19 街三栋住宅以及 University 街 1910、1940、1960 和 1976 号登记为 L2。教堂两个旧网格并为一栋，保留露天内院。University 街四栋住宅各自可选，三个间隙通过碰撞检查。[八栋外部核对](potter-university-exterior-review-2026-11-26.md)。

Theta Chi、Delta Tau Delta、Potter 街 1860 号、Onyx 街 1930 和 1976 号以及 University 街 1941 号均沿用原 ID 登记为 L2。Theta Chi 恢复完整建筑轮廓。六处估算接近点都在桌面和手机生产预览中通过导航核对。[六栋 South University 临街外部核对](south-campus-frontages-review-2026-11-26.md)。

Onyx 街 1866 与 1870 号、东 19 街 1208 号主屋与后车库、University 街 1825 号与 Onyx 巷 1840 号均已拆成独立的 L2 外部。保留三个原场景 ID，并新增三个拆分 ID。验证覆盖三处建筑间隙和四处估算接近点。[六栋外部拆分核对](onyx-university-split-exterior-review-2026-11-26.md)。

Sigma Nu、东 18 街 1306 号和 Emerald 街 1874 号均已沿用原 ID 升为 L2。分别恢复四根通高门廊柱、开敞低檐和后侧外楼梯、两层蓝色立面与四坡屋顶，并登记三处临街接近点。[South University 三栋建筑外部核对](south-university-exterior-review-2026-11-26.md)。

Onyx House（Onyx 街 1850、1852 号）已登记为 L2，沿用原场景 ID。重建交叉浅坡屋顶、南侧低翼、巷侧底层两端开口和东门廊台阶。[Onyx House 外部核对](onyx-house-exterior-review-2026-11-26.md)。

东 19 街 1340 号公寓已登记为 L2，沿用原场景 ID。重建交叉屋脊、蓝色立面、院内二层外廊和楼梯，并登记北侧临街接近点。[1340 号外部核对](east-nineteenth-court-exterior-review-2026-11-26.md)。

Alton Baker 公园两座凉亭及 Best Western New Oregon 的 Franklin 侧翼已登记为 L2。1 号凉亭有新增场景 ID。两处已拆建筑从默认场景移除，原 ID 保存在历史台账中。[凉亭和酒店外部核对](alton-franklin-exterior-review-2026-11-26.md)。

东 17 街 625–627 号、东 16 巷 630–632 号和东 19 街 640 号东侧楼体升为 L2。东 17 街旧合并模型拆成三个独立对象。东 16 巷 634–640 号按市政轮廓和高程建模，主要立面仍待核实，保留 L1。[西边界外部核对](west-boundary-exterior-review-2026-11-26.md)。

Parkside Place、东 20 街 1131 号和东 21 街 1039、1145 号共四栋建筑外部已登记为 L2。沿用原场景 ID，恢复连通屋面、车库前段、退入式下层及两栋临街凸窗。Parkside 和 1145 号分别登记一处步行接近点。[四栋外部核对](hilyard-south-exterior-review-2026-11-26.md)。

Lorax Manner、Campbell Club、Woodside Manor、东 19 街 1065–1079 号与 746 号、东 18 街 750 号共六栋建筑外部已登记为 L2。沿用原场景 ID，补建塔楼、门廊、分段屋顶、阳台和外楼梯。Woodside Manor 保留市政轮廓中的四处开口。[六栋外部核对](alder-harris-exterior-review-2026-11-26.md)。

东 19 街 Sigma Chi 会馆、1456／1458 号与 1355 号三栋建筑外部已升为 L2，保留原场景 ID。恢复会馆东侧雨篷及庭院走廊、1456／1458 号的共用门廊和 1355 号的开敞停车层与西走廊。[东 19 街外部核对](east-nineteenth-exterior-review-2026-11-26.md)。

2300 Parkside Lane 已登记为 L2，保留原场景 ID。市政轮廓、航片与挂牌资料支持开敞车棚、木格栅门、高窗和沿坡三层露台。露台及楼层标高为近似值。[Parkside 外部核对](parkside-exterior-review-2026-11-26.md)。

1800 和 1850 Millrace Drive 共用一栋 L2 外部，按市政轮廓恢复高低屋面、设备组、带状窗和北侧有雨篷的入口。两个门牌均可搜索并导航到同一栋楼。[Millrace 外部核对](millrace-research-exterior-review-2026-11-26.md)。

Phi Kappa Psi 会馆、东 8 街 642 号、1414 Alder 和 Eugene 蒸汽厂四栋外部已登记为 L2，沿用原场景 ID。模型包括会馆三拱入口、商铺退入式木饰面入口、公寓外楼梯及架空区、蒸汽厂高窗和分层屋顶。[四栋外部核对](northwest-infill-exterior-review-2026-11-26.md)。

Deschutes 附近的固定人物 PERSON:dan-carrere 已登记为本地 L2。风格化模型包含带帽带的弧形帽檐、面部与胡须轮廓、格纹衬衫和接地步态，保留原有路线和资料卡交互。[固定人物核对](fixed-person-dan-carrere.md#l2-appearance-and-walking-review)。

通用校园学生和松鼠 LIFE-01 已登记为 L2。步行接地、松鼠九关节动作、纪念广场西侧步道与八段草地活动路径均纳入本次核对。松鼠为通用模型，树上路线与物种仍属示意。[校园活动核对](campus-life-l2-2026-11-26.md)。

草坪、铺装、道路与步道 ENV-05 已登记为 L2。Riverfront Parkway 铁路桥下铺面恢复连续，Knight Library 西侧草坪保留原路径和地面。[铁路桥与草坪复核](riverfront-plant-infrastructure-exterior-review-2026-11-26.md)。Arena 前广场恢复接缝，Walnut 停车区恢复标线和三处种植岛。[东侧铺地证据](villard-orchard-walnut-exterior-review-2026-11-26.md)。纪念广场恢复北侧 X 形步道和南侧环道，更新对应导航并保留六处树池。139 条在用道路与步道记录已重建为两组地表，其中 96 条至少有一段按市政记录核对宽度与材质。[铺装与道路核对](paving-corridors-l2-2026-11-26.md)。

地形与地表覆盖 ENV-04 已登记为 L2。全范围地表更新 62,339 个高程点，按 USGS 水域多边形重着色，并以 2024 年航片判断地表类型。全部 608 段入口接近线和 7,705 条源路径边的高程采样一致。[地形与地表核对](landcover-l2-2026-11-26.md)。

灌木、林下植物和种植带 ENV-03 已登记为 L2。Knight Library 和 Johnson Hall 北侧共重排三处种植床并保留中央通行空间。默认场景采用 75 株重建灌木、五组重建蕨类和三组既有详细蕨类。植物物种与种植株数仍待实地核实。[林下植物核对](understory-l2-2026-11-26.md)。

背景乔木 ENV-02 已登记为 L2。默认场景换用 269 株轻量树形，收窄四处靠近建筑的树冠，撤下 Flock13 屋面内的旧程序树。配准场地树继续由各自场地模型显示。[背景乔木核对](context-trees-l2-2026-11-26.md)。

试点乔木 ENV-01 已登记为 L2。重建 273 株乔木的树干、分枝和树冠，沿用 11 株登记树的场景坐标，并针对建筑收窄七处枝冠。Gerlinger Annex 北侧一株推断树干在同一航片冠幅内向北调整两米。[试点乔木核对](pilot-trees-l2-2026-11-26.md)。

Fairmount 东南侧的 281、365、366 Sunset，2275、2281 Rose 和 2293 Birch 共六栋住宅外部已登记为 L2，并沿用原场景 ID。恢复玻璃山墙、可见屋面太阳能板、架空阳台、老虎窗及分段屋面。已设三处估计接近点。[六栋外部核对](southeast-fairmount-exterior-review-2026-11-26.md)。

台阶、露台及花坛 ENV-06 已登记为 L2。重建 Johnson Hall 和 Knight Library 的北入口台阶及栏杆，补建 EMU 西北侧圆形剧场，并细化 Oregon Hall 南侧抬高花坛。入口和露台标高按当前模型和地面估算。[室外硬质景观核对](pilot-hardscape-l2-2026-11-26.md)。

1517、1671、1680 Walnut，1879、1931 Moss，1991 E 19th，以及 Pi Beta Phi 和 Alpha Chi Omega 会馆共八栋外部登记为 L2，沿用原场景 ID。[Fairmount 和 Kincaid 外部核对](fairmount-kincaid-exterior-review-2026-11-26.md)。

Alder 与 E 13th 街角商铺、Gopuran、Flock13 和 The Duck Store 的四栋独立外部已登记为 L2。Chapter Alder 工地按 2026 年 9 月市政资料登记为 L2 景观，施工范围和保留建筑各自配准。[街区与施工场地核对](alder-thirteenth-exterior-review-2026-11-26.md)。

The Rive Eugene 已登记为 L2。700 E Broadway 现有的 12 层住宅替换同一位置的旧模型，沿用原场景 ID。模型恢复临街裙楼、带退入门厅的 Hilyard 入口、分层露台和屋顶泳池。[The Rive 外部核对](rive-eugene-exterior-review-2026-11-26.md)。

Alpha Tau Omega 会馆、1956 E 15th、1871 E 19th 和 Walnut 巷车库已登记为 L2。四栋各自沿用原场景 ID。会馆新增东侧接近路线，车库保留独立外观和空入口列表。[外部核对](millrace-fairmount-exterior-review-2026-11-26.md)。

试点家具 PROP-01 已登记为 L2。默认场景换用九张五英尺木长椅、十一盏橡果灯和 Tykeson 西南铺装的三环车架。坡度、建筑与通行边缘均按当前场景核对，实际安装点仍待实地核实。[家具核对](pilot-furnishings-l2-2026-11-26.md)。

Marlatt Apartments 两侧住宅、后方两层楼和 777 Annie Mims Lane 河滨设备楼已登记为 L2。庭院步道保持通行，设备楼以独立外观展示并保留闭合卷帘门。[Marlatt 与河滨核对](western-exterior-review-2026-11-26.md)。

UO East Station 主楼及 A、B 两栋附楼已登记为 L2。沿用三个 ID，分别恢复主楼金属四坡屋顶与南侧门廊、A 附楼窗带、B 附楼的斜向双坡顶。[三处东站外部核对](east-station-exterior-review-2026-11-26.md)。

Bushnell 东庭院的两个原模型已登记为 L2。Kellenberger 图书馆、Price 音乐楼及 Evans 礼拜堂保留相连楼体并恢复共用西入口。Burke-Griffeth 宿舍恢复西端餐厅、宿舍错层屋面和方庭立面。[东庭院外部核对](bushnell-east-exterior-review-2026-11-26.md)。

Goodrich Hall、1125 Alder 校方设施维护楼和 1145 Alder 砖楼已登记为 L2。Goodrich 恢复石砌正立面和 2025 年钟楼，1125 号独立登记并保留开放门廊，1145 号恢复烟囱与分段屋面。[三处外部核对](goodrich-quad-exterior-review-2026-11-26.md)。

950 Alder Suites、1075 Alder 的 Morse Center 和 1090 Alder 的 Pomajevich Hall 登记为 L2。原场景缺失的 950 号新增独立 ID，保留架空停车和临街阳台。其余两栋沿用原 ID，分别恢复体育馆分段屋面及教学楼的门廊、台阶和坡道。[三处外部核对](alder-bushnell-exterior-review-2026-11-26.md)。

天空与云层 ENV-07 已登记为 L2。新版天穹增加方向色彩，云层由 12 组低层积云和 6 组高处薄云组成，保留减弱动态设置并归档两层完整几何。[天空与云层核对](eugene-sky-l2-2026-11-26.md)。

通用入口标识 PROP-04 已登记为 L2。双扇门补齐门楣、门槛、外拉手和内推杆。323 处通用入口仍共用两组实例化网格，611 条入口的场景位置与接近点沿用上一版。[入口门组核对](entrance-portal-l2-2026-11-26.md)。

1401 Walnut、968 Alder 和 755 E Broadway 登记为 L2。Walnut 恢复校方办公室的四坡顶和分格窗，Alder 恢复巷侧砖墙与入口，Broadway 采用 2024 年 7 月的原 Motel 66 入口形态并保持雨棚下可通行。[三处外部核对](walnut-alder-broadway-exterior-review-2026-11-26.md)。

E 15th 临街楼与巷侧楼分别登记为 L2。临街楼恢复分坡屋顶、格栅和退台停车位。巷侧楼原场景缺失，本次恢复双山墙与外楼梯。两栋暂按位置命名，750 和 758 的门牌归属待核。[两栋外部核对](e-fifteenth-pair-exterior-review-2026-11-26.md)。

957、971 和 975 Hilyard 分别登记为 L2。957 恢复两层外走廊，971 恢复砖立面与独立四坡顶，975 恢复北侧外走廊。三栋与 973 分别可选。[三栋外部核对](hilyard-central-exterior-review-2026-11-26.md)。

1515 Hilyard、740 E 15th 与 1548–1549 Hilyard 已拆成三栋 L2 外部。740 号恢复两处停车棚开口与临街、巷侧楼梯，复式住宅恢复西侧木立面、阳台和双门。[三栋外部核对](hilyard-fifteenth-exterior-review-2026-11-26.md)。

Zebrafish International Resource Center 的 B0101 外部已更新为 L2。新模型按 2024 年航片和竣工照片补齐西侧扩建，区分深色压型金属、灰色砌块和原有铜色坡顶，并沿用原场景 ID。[扩建外部核对](zirc-exterior-review-2026-11-26.md)。

Hilyard Apartments 的 973 号楼在原场景缺失，现作为独立 L2 外部启用。市政门牌与 2024 年航片表明 973 和 975 是两栋分别登记的楼。新模型保留砖立面、灰色四坡顶和蓝色入口雨篷，西侧接近点可导航。[973 Hilyard 核对](hilyard-apartments-exterior-review-2026-11-26.md)。

自行车、滑板车与骑行者组 PROP-03 已采用 L2 模型。参考代表尺寸重建车架、轮轴、踏板和滑板车站板，两个车型均验证轮胎触地、骑行者接触与运行时碰撞包络。[骑行道具核对](cycle-props-l2-2026-11-26.md)。

旧 Sacred Heart 医院地块已采用 The Mark Eugene 一期施工快照。新场地作为 L2 室外资产组 ENV-08，按 2026 年 10 月 17 日照片呈现首层木框架、围栏和塔吊，并用 11 月市政通告核对 Hilyard 一侧封闭。经 2024 年航片复查，五条旧候选中一条对应已拆医院，另四条与可见屋面无重叠。五条原 ID 保留为历史记录。[施工场地核对](former-hospital-site-review-2026-11-26.md)。

本地预览已采用 PeaceHealth 1200 Hilyard 诊所、650 E 12th 南停车楼和 677 E 12th 北办公楼的 L2 外部。旧网格由两条来源记录拆成三处可选建筑，保留诊所与停车楼间的电梯连接。[诊所与停车楼核对](university-district-clinic-review-2026-11-26.md)。

本地预览已采用 770 E 11th、633 E 12th 和 666 E 13th 的三个 L2 外部。770 号与 722 号恢复保留的三层连桥，桥下可走。两座停车楼恢复开敞车层与分坡屋面，633 号西侧超出源地形的部分以航片注册。[大学区核对](university-district-exterior-review-2026-11-25.md)。

车辆道具组 PROP-02 已复核四种通用车型的形体、尺寸、轮胎触地点、碰撞和导出模型。20 个场景泊位均容纳对应车型，坡面接触仍有近似。该组记为 L2。[车辆道具核对](vehicle-l2-2026-11-25.md)。

源校园 GLB 中 64 个为独立建筑节点，470 个归在 21 个批次中。更新后的室外建筑台账含 241 个已有名称或历史映射的条目和 307 个未确认条目。暂定 Volcanology、Canterbury Court 和 Millrace 3 属于批次。在最初筛查的 470 个批次候选中，有 59 个找到覆盖至少 50% 模型足迹的 UO 候选，其余 411 个当时没有选定 UO 候选。批次继续按场景 ID 跟踪。[源场景清单](../apps/web-preview/public/scene/manifest.json) · [室外细化计划](exterior-refinement-plan.md)。

2026-11-23 本地默认预览已采用 Ford Alumni Center 与 Matthew Knight Arena 的成对场景，包含地形、碰撞及四个入口交互点。州足迹资料也已与全部 534 个建筑场景 ID 对照，其中 241 个在双向重合筛查中满足较高阈值。重合结果用于安排外形复核。两栋于 2026-11-24 通过项目内的 L2 审核，补齐幕墙横框、广场墙体、种植槽及台阶扶手。[成对场景](ford-arena-exterior-massing-2026-11-23.md#default-campus-preview) 和 [足迹筛查](exterior-refinement-plan.md#campus-footprint-comparison-2026-11-23)。

本地默认体育馆区域采用 McArthur Court、Esslinger Hall 和 Student Recreation Center 的三个独立外部。此次补齐 McArthur 东侧钢梯与角部装饰、Esslinger 西门门饰与南侧已见的屋面色，以及 SRC 东侧幕墙遮阳片和入口横窗。三栋经逐项审核为 L2。Esslinger 2026 年施工区的完工屋面，以及 SRC 扩建后的实测高程仍待核对。[模型及核对记录](athletic-block-exterior-2026-11-23.md#default-adoption-and-exterior-review-2026-11-24)。

本地默认预览已采用 15 个依据历史高程和 2024 年航片修正的背景屋面。新增 4 个在单独保留的 139 个历史高程样点上，各栋误差中位数的中位值从 1.145 米降至 0.168 米。建筑身份、门窗和屋缘现状仍待核实，台账按原场景 ID 保留 L1。[批量屋面对照](context-roof-refinements-2026-11-23.md#expanded-review)。

较早的默认预览累计移除 24 株落在铺装或草坪上的程序树及 3 株配对灌木，并配准 8 株树木。在当时筛查的 84 组建筑网格中，4 株仍与表面相交。此后试点层和背景乔木层已按当前场景重建。[初轮清理](pilot-tree-clearance-2026-11-23.md) · [台账配准及复核](pilot-tree-registration-2026-11-23.md)。

Knight Library 的默认模型已配准北立面、重建南翼，并按校方足迹更新碰撞。覆盖率从 71.52% 升至约 100%。北门交互已核验，台阶和平台标高仍为近似。该建筑保持 L2。[外壳配准与核验](knight-library-registration-2026-11-23.md)。

默认 EMU 外部采用 UO 033 的统一模型，恢复圆形草坪、Fishbowl 弧形窗带和西侧三处入口。五处接近点均经过浏览器核验，外部按 Knight 样例逐项审核后记为 L2。西门门槛、屋面设备和背侧细节仍为近似，草坪所属的景观组保持 L1。[EMU 启用记录](emu-green-exterior-2026-11-23.md#default-adoption-and-exterior-review-2026-11-24)。

本地默认预览采用 Canterbury Court 与 Millrace 3 的分段屋面。Canterbury Court 恢复约 288 平方米的露天庭院，补齐两层窗带、门面和带扶手短坡道后审核为 L2。Millrace 3 保留两排老虎窗和主屋脊，补齐南侧跨檐线玻璃、墙脚挂板、木入口架与铺装后审核为 L2。[庭院和工作室核对](compound-context-exteriors-2026-11-23.md)。

Johnson Hall 外部补齐中央抬高屋顶、东西两侧遮阳篷与南门的玻璃雨棚、阶梯和栏杆。在保留的 170 个历史样点上，新屋面的高差绝对值中位数为 0.256 米。结合已核对的北门廊，外部按项目样例审核为 L2。[Johnson 外部核对](johnson-rear-refinement.md#exterior-review-and-roof-registration-2026-11-24)。

Jordan Schnitzer Museum of Art 按校方底图、近年航片、历史点云和档案照片重建屋面及三处庭院，并补齐西门砖饰、台阶和东侧扩建的窗列与雨棚。前门往返与庭院碰撞已验证。外部对照 Knight Library 审核为 L2，细部尺寸和实地门槛标高仍为近似。[博物馆外部核对](museum-west-refinement.md#registered-exterior-and-courtyard-review-2026-11-24)。

Gerlinger Hall 和 Gerlinger Annex 采用配准后的双栋外部。Hall 恢复两排老虎窗、四座铜顶和三面主要立面。Annex 恢复分层平屋面、混凝土挂板、北侧玻璃立面和连廊。两栋保留独立建筑 ID，并各自对照 Knight Library 审核为 L2。连廊底面及实地门槛标高仍为近似。[Gerlinger 双栋外部核对](gerlinger-site-review-2026-11-24.md)。

Susan Campbell Hall 与 Hendricks Hall 已采用注册后的折坡屋面、砖女儿墙和庭院立面。Hendricks 补齐北侧旧餐厅翼，并把历史拆分屋顶并入同一外部。两栋各自对照 Knight Library 审核为 L2，入口高度与装饰尺寸仍为近似。[女校纪念四方院外部核对](womens-quad-exterior-review-2026-11-24.md)。

Chapman Hall 与 Condon Hall 采用配准后的分段平屋面、拱窗和陶瓦檐饰。Chapman 包含西门及北门，Condon 区分原楼、西楼梯塔和南扩建。两栋各自对照 Knight Library 审核为 L2，实地门槛和砖饰尺寸仍为近似。[纪念四方院外部核对](memorial-quad-exterior-review-2026-11-24.md)。

Fenton Hall 按校方足迹、屋面图与历史点云配准，恢复原楼四坡金属屋顶、东门栏杆、连接塔和西侧五层书库，并加入东侧主入口与 13th Avenue 南门的台阶和接近点。对照 Knight Library 审核为 L2，实地标高、后侧开窗和屋顶细节仍为近似。[Fenton 外部核对](fenton-exterior-review-2026-11-24.md)。

University Hall 与 Villard Hall 按校方足迹、翻修后照片和历史点云重建屋面与主要立面。前者恢复双塔与东西台阶，后者恢复四角塔、东门及西侧剧院连接。两栋分别审核为 L2。实地门槛、连接处构造和种植为近似。[历史校园核心区外部核对](heritage-core-exterior-review-2026-11-24.md)。

Miller Theatre Complex 重建分段屋面、Robinson 舞台塔、Hope 翼、西侧玻璃门厅与多段台阶，并把低位连接纳入剧院模型。西门往返、台阶外落脚点和接缝碰撞经过核对，外部审核为 L2。实地门槛、玻璃表现和后侧细节仍为近似。[Miller 外部核对](miller-exterior-review-2026-11-24.md)。

Allen Hall 恢复 1954 年西翼的窗带与九块示意浮雕，并重建旧 Journalism 翼、2012–13 年扩建屋面和东门玻璃立面。三个入口经过往返测试，室外审核为 L2。西侧下沉区深度、实地门槛和装饰尺寸仍为近似。[Allen 外部核对](allen-exterior-review-2026-11-24.md)。

Lawrence、Pacific 和 Columbia 按各自校方足迹重建并分别审核为 L2。Lawrence 恢复露天庭院，Pacific 与 Columbia 恢复架空连桥和桥下通道。Pacific、Columbia 的名称迁至定位正确的新 ID，旧位置继续保留为未确认候选。窗距、入口标高和部分背侧细节仍为近似。[科学楼群外部核对](lawrence-science-exterior-review-2026-11-24.md)。

Straub 与 Earl 按校方足迹和 2017 年扩建后地表数据重建，外部分别审核为 L2。Straub 恢复三拱西门、坡屋面、玻璃北门及两层扩建屋面。Earl 恢复五翼、低连接体、庭院和带肋窗带，两条旧网格保留历史映射。入口尺寸及 Earl 新屋面材料仍为近似。[Straub 与 Earl 外部核对](straub-earl-exterior-review-2026-11-24.md) · [2017 年地表数据](campus-surface-2017-2026-11-24.md)。

Catherine Cornwall Townhouses、Hilyard House、Campus Studios 和 Bushnell University 东 11 街 722 号的建筑外部审核为 L2。Hilyard House 保留露天中庭与四柱门廊，另外两座住宅保留街侧架空停车空间。东 11 街 722 号主体与相邻 770 号之间的连桥待并入相邻体量复核。[Hilyard 外部核对](hilyard-west-exterior-review-2026-11-24.md)。

1951 Onyx Alley、1772 Hilyard、Spencer Apartments、Eugene Institute of Religion、1010–1020 E 18th 和 1010 E 20th 六栋外部审核为 L2。东 18 街砖楼保留两处独立入口，三栋重建架空停车空间。Lane County 高程的屋面误差中位数六栋均下降，另一套历史高程五栋上升。[建筑外部核对](treated-roof-exterior-review-2026-11-24.md)。

Fairmount Boulevard 1705、1799、1834、1892、1925、2055 和 2094 号外部审核为 L2。1799 保留太阳能屋面和挑檐下方空间，1892 恢复街侧雨棚及巷侧木阳台，1925 恢复低坡屋面与窗带。[Fairmount 外部核对](fairmount-residential-exterior-review-2026-11-24.md)。

East Broadway 652、659、686、782 号和 Orchard 的 1432、1468–1476、1505、1838、2059 号外部审核为 L2。1468–1476 号保留上层下方的停车通道，1505 号恢复院落开口，1432 号保留架空门厅和外楼梯。[Broadway 与 Orchard 外部核对](broadway-orchard-exterior-review-2026-11-24.md)。

Franklin Boulevard 850 号 Womack Hall 与 1920–1960 号连体商业楼外部审核为 L2。Womack 恢复四层立面和双柱开放车道，商业楼保留一个场景 ID 并登记四处店面入口。[两处外部核对](franklin-complex-exterior-review-2026-11-24.md)。

Franklin Boulevard 1675、1809、1895、1917、1933 和 2091 号外部审核为 L2。1917 恢复倾斜光伏阵列，1933 保留屋面下凹区和黄柱前廊，2091 将开放加油棚与封闭店面分别登记碰撞。[Franklin Boulevard 外部核对](franklin-boulevard-exterior-review-2026-11-24.md)。

Bardell Avenue 3324、3330、3336、3344、3345 和 3355 号按州轮廓、市政门牌及两期历史高程配准，外部审核为 L2。3324 恢复抬高的山墙入口和两种宽度的车库门，3336 保留西侧浅色屋面，3345 恢复三扇车库门，3355 补齐入口拱形横窗。[Bardell Avenue 外部核对](bardell-avenue-exterior-review-2026-11-24.md)。

Villard Street 1401、1599、1637、1801、1969 和 1979 号通过 L2 核对。1401 重建沿街格栅和低屋面，1599 恢复巷侧双车库门，1969 保留整宽且可走入的前廊，1979 重建重叠山墙及后部亮色屋面。[Villard Street 外部核对](villard-street-exterior-review-2026-11-24.md)。

Garden Avenue 五栋通过 L2 核对。1848 号恢复临街山墙，1901 号重建西侧入口和外楼梯，1976 号登记两组屋顶太阳能板。Millrace Gardens 南北两栋共用 2001 号门牌，分别建模和选择。1907 号仍缺少清晰的立面资料，暂留 L1。[Garden Avenue 外部核对](garden-avenue-exterior-review-2026-11-24.md)。

Fairmount Boulevard 七栋住宅按州轮廓、市政地址及历史高程重建外部并审核为 L2。1780 号有敞开车库，1956 号恢复高低两片低坡屋面，1820 号将入口退入长檐下。[Fairmount 外部核对](fairmount-boulevard-exterior-review-2026-11-24.md)。

东校园六栋校方住房按校方编号、州轮廓和影像分别重建外部并审核为 L2。包括 1778 Villard 的凸出老虎窗和独立车库、1795 Moss 的双层山墙轮廓，以及 1848 Moss 的青灰色门廊檐饰。[东校园住房核对](east-campus-housing-exterior-review-2026-11-24.md)。

1915 Alder、Hess Apartments 与 Millrace Apartments 在保留原场景 ID 的基础上审核为 L2。已核对临街立面、入口和 Hess 架空停车层。[三栋住宅核对](alder-millrace-exterior-review-2026-11-24.md)。

Villard Street 四栋住宅与 Garden Avenue 两栋公寓已逐栋审核为 L2。三个原合并候选拆分后新增三个独立 ID，保留另外三个原 ID。已核对六栋入口、间隙、檐饰和分段屋面。[六栋住宅核对](villard-garden-exterior-review-2026-11-24.md)。

Chi Omega House 与 Delta Delta Delta House 已从合并体量拆为两个独立 L2 外部。州轮廓、市政地址和航片确认分界，历史名录与街景支持各自不同的屋面、门廊和开窗。[两栋拆分核对](chapter-house-exterior-review-2026-11-24.md)。

Coho 南排、Pi Kappa Alpha House、Christus House、Newman Center、Hayward House、Aldersgate 和 The 1840 已审核为 L2。街景确定了 Newman Center 的临街陡檐窗罩、Hayward House 和 Aldersgate 的外廊与架空层。[校园周边外部核对](campus-neighbor-exterior-review-2026-11-24.md)。

The Lewis、The Clark、Student Manor、Royal Terrace 与 Coho 北排已按市政地址、轮廓以及立面照片审核为 L2。保留原屋面和场景 ID。Royal Terrace 保留两翼之间的露天庭院和北侧檐下通道。[住宅外部核对](residential-exterior-review-2026-11-24.md)。

UO Annex、Rainier Building、1311 Franklin、University Business Operations Center 与 1715 Franklin 的外部审核为 L2。保留原场景 ID，新模型按证据区分四坡、双坡、屋顶凸起与办公楼分层体量。Business Operations Center 恢复临街拱窗，1715 Franklin 保留开敞庭院。[外部核对](office-exterior-review-2026-11-24.md)。

CPFM Warehouse and Shops、两座 Facilities Services Quonset、CPFM Administration 与 Romania Warehouse and Showroom 的外部审核为 L2。五栋保留场景 ID，按不同的浅坡、弧面和翘曲屋面重建，并登记校方名称。[建筑核对](facilities-exterior-review-2026-11-24.md)。

University Health Services、Central Power Station、Riley Hall、Student Tennis Center 与 Alder Building 的外部审核为 L2。五栋保留原场景 ID，四栋补登记校方名称。恢复 Health Services 扩建和露天内院、Power Station 的分层屋面和低附楼、Riley 下沉庭院、网球中心两道屋脊和 Alder 开放门廊。[外部核对](campus-frontage-exterior-review-2026-11-24.md)。

Hayward Field 按 2024 航拍和竣工资料恢复 U 形顶棚、木肋、看台、跑道、观景塔和北广场，审核为 L2。停用两块重复旧看台网格并保留历史映射。屋面高程、座席排布和出入口尺寸为近似。[场馆及 Canterbury 外部核对](hayward-canterbury-exterior-review-2026-11-24.md)。

Clinical Services、自然与文化史博物馆、Outdoor Program Barn 与 Agate Hall 的外部审核为 L2。保留四个场景 ID，Agate Hall 按 UO 147 补登记名称。恢复 Clinical 的不规则坡面、博物馆门廊、Barn 的光伏屋面及 Agate 的六组礼堂天窗。[外部核对](public-building-exterior-review-2026-11-24.md)。

Fine Arts Studios 的 Sculpture、Ceramics、Metalsmith/Jewelry 和 1600 Millrace Drive 审核为 L2。三座工作室使用可编辑的坡面、天窗和庭院连廊。1600 Millrace 恢复弧面入口与砖墙横带。四项保留原选择 ID 并按校方记录命名。[外部核对](northsite-millrace-exterior-review-2026-11-24.md)。

Knight Campus 一号楼和二号楼审核为 L2。重建一号楼折面玻璃、二号楼金属遮阳板和西侧退台，以及横跨 Franklin Boulevard 和 millrace 的两座连廊。建筑继续使用原选择 ID，原一号楼东南翼旧网格移入历史。[外部核对](knight-campus-exterior-review-2026-11-24.md)。

东北科学楼群七项审核为 L2，包括 Onyx Bridge、Cascade Annex East、Klamath、Huestis、Deschutes、Streisinger 和 Willamette。Onyx Bridge 保留西附楼与架空通道，东附楼用原 ID 单独选择。旧 Willamette 组合体按校方边界拆分，Huestis 按翻修后资料重建。[外部核对](northeast-science-exterior-review-2026-11-24.md)。

PLC、Lokey Education A/B 与 C 以及 Tykeson Hall 的建筑外部审核为 L2。PLC 保留塔楼、礼堂和低层翼的三个屋面高度及两处不同高程的庭院。Lokey C 用原 ID 注册为独立建筑；PLC 与 Lokey A/B 的三片重复旧网格保留历史映射。Tykeson 的屋高依据建筑师剖面和竣工照片估算。[外部核对](plc-lokey-tykeson-exterior-review-2026-11-24.md)。

Friendly Hall、Collier House 和 McKenzie Hall 的建筑外部审核为 L2。Friendly 依据施工前资料重建双门廊和分层屋顶，Collier 按调查恢复主屋、凸窗、门廊及低层附建，McKenzie 按历史高程保留下沉的东庭院并补建台阶、挡墙和廊柱。[三栋建筑的核对记录](friendly-collier-mckenzie-exterior-review-2026-11-24.md)。

Lillis Hall、Chiles Business Center、Peterson Hall、Anstett Hall 和 Computing Center 均审核为 L2。五栋保留原 ID，重新配准旧模型交错的实体边界，恢复两侧历史入口、Lillis 光伏立面、北圆厅及广场。一片由 Lillis 东翼覆盖的源网格转为历史映射。[楼群外部核对](lillis-complex-exterior-review-2026-11-24.md)。

Oregon Hall（UO 042）和 Jaqua 学术中心（UO 067）按校方平面、历史高程、2024 年航拍和外观照片重建，均审核为 L2。Oregon Hall 恢复南柱廊、北退台及南侧种植槽，Jaqua 恢复玻璃框架与水池，停用一株落在楼内的程序化树。[Oregon Hall 与 Jaqua 外部核对](oregon-jaqua-exterior-review-2026-11-24.md)。

Carson Hall（UO 076）和 Living-Learning Center 北楼（UO 065）、南楼（UO 064）按校方轮廓、2024 年航拍、2017 年历史高程及外观资料重建。三栋均审核为 L2，保留 Carson 主楼与北侧低屋面的高差、LLC 两栋的坡屋面、楼梯间和共享庭院。[Carson 与 Living-Learning Center 外部核对](carson-llc-exterior-review-2026-11-24.md)。

Cedar Hall（UO 205）和 Yasui Hall（UO 206）按 2024 年航拍、校方墙线和建筑师照片重建，保留两个共享庭院、庭院低楼及 Yasui 架空连廊下的穿行口，两栋均审核为 L2。经 2018 和 2024 年航拍交叉核对停用三片 Walton 旧网格并保留历史记录。[Cedar 与 Yasui 外部核对](cedar-yasui-exterior-review-2026-11-24.md)。

Bean Hall（UO 068）和 Unthank Hall（UO 207）按校方轮廓和 2024 航拍配准，保留原场景 ID，恢复两处庭院和楼间通道。两栋均通过 L2 核对。Bean 新增部分及 Unthank 的屋面和门槛高程使用近似尺寸。[Bean 与 Unthank 外部核对](bean-unthank-exterior-review-2026-11-24.md)。

Knight Law Center 按校方 UO 050 足迹重建九个屋面分区、Agate Street 拱门、东庭院及玻璃廊，保留原场景 ID 后审核为 L2。窗距、屋面设备、门槛及铺面尺寸仍为近似。[Knight Law 外部核对](knight-law-exterior-review-2026-11-24.md)。

East Campus Graduate Village 东、西楼各保留原场景 ID 并登记为 UO 146、145。两栋按不同方向的三层与两层体量、四坡屋面和挂板立面审核为 L2。部分窗距、入口和步道尺寸仍为近似。[Graduate Village 外部核对](graduate-village-exterior-review-2026-11-24.md)。

Vivian Olum 主楼与附楼按 UO 165、164 各自登记，保留原场景 ID。主楼补齐分段坡屋面和西侧步道，附楼补齐浅坡屋面和木构雨棚，两栋均审核为 L2。部分外墙开窗、雨棚及入口标高仍为近似。[Vivian Olum 外部核对](vivian-olum-exterior-review-2026-11-24.md)。

Moss Street Children’s Center 以 UO 168 登记，五个体量环绕庭院，南侧旧网格保留历史映射。屋面、木棚、玻璃立面及院内水栎经逐项核对后纳入 L2 场地模型。[Moss Street 外部核对](moss-street-exterior-review-2026-11-24.md)。

Global Scholars Hall 保留 UO 158 的原场景 ID。配准后的外部有三座坡顶塔楼、两处开放庭院、绿屋顶连廊和四处入口，经逐项核对达到 L2。部分老虎窗间距、雨棚与门槛仍为近似。[Global Scholars Hall 外部核对](global-scholars-exterior-review-2026-11-24.md)。

Many Nations Longhouse 保留原场景 ID 并登记为校方 UO 167。按配准后的墙体、向北降低的单坡绿屋顶、南侧大窗及东入口重建外部，经逐项核对达到 L2。屋面覆盖、背侧门和门槛尺寸仍为近似。[Longhouse 外部核对](longhouse-exterior-review-2026-11-24.md)。

Kalapuya Ilihi 按校方 UO 159 足迹重建住宅翼、错层屋面、开放西庭院和低位公共空间，保留原场景 ID 后审核为 L2。移除贯穿现址的旧道路及其 12 条路线边，补上连接北门、西庭院和南门的户外步道。门槛、部分背侧窗格和屋面设备仍为近似。[Kalapuya 外部核对](kalapuya-exterior-review-2026-11-24.md)。

本地默认启用 Frohnmayer UO 025 的统一外部。模型保留约 910 平方米的中央庭院，校方足迹覆盖由 74.4% 提升至 93.4%。校方一层平面图用来核对 Beall 西入口的三段台阶。主记录经过逐项审核后为 L2，两条旧网格记录保留映射。台阶、门槛及部分立面尺寸仍为近似。[音乐楼外部核对](frohnmayer-exterior-review-2026-11-23.md#default-adoption-and-exterior-review-2026-11-24)。

HEDCO Education 的本地默认外部恢复四翼、钟楼、露天庭院及西侧有顶步道，按项目样例审核后为 L2。两处入口的接近点，以及步道和支柱的碰撞已核对。柱距、开窗和实地门槛高程仍为近似。[HEDCO 外部核对](hedco-exterior-2026-11-04.md#default-adoption-and-exterior-review-2026-11-24)。

Cascade Hall 与 Volcanology 的联合模型进入本地默认场景。Cascade 细化庭院拱门和连桥护栏，Volcanology 细化窗格、石构窗楣、外墙转角及南门台阶。两栋外部逐项审核为 L2。Volcanology 的源 ID 仍保留地图近似匹配标记，门槛及台阶标高仍为近似。[庭院和临街外部核对](cascade-wall-study.md#default-adoption-and-exterior-review-2026-11-24)。

本地默认预览新增 10 个单层平屋面和 4 个双层平屋面，累计采用 31 处屋面修正。14 个新模型保留各自的场景 ID、足迹和碰撞，等级仍为 L1。已核对 1,541 个单独保留的历史高程样点。[平屋面核对](context-flat-roofs-2026-11-23.md)。

## 维护方式

1. 在 CSV 中按 `asset_type`、`area`、`status` 或 `level` 筛选。`EXT:` 和 `INT:` 后面的同一建筑 ID 可关联内外部；环境和道具使用固定的 `ENV-`、`PROP-` 等 ID。不要按名称关联，未命名身份可能之后改变。
2. 完成一项工作时，更新该行状态、证据路径、下一步和未知事项；等级依照用户已给出的标准与后续明确决定更新。新建独立内部时，将状态改为 `existing`，并按其实际阶段及用户标准赋级，不要自动继承共用教室的等级。
3. 如场景新增、合并、拆分或删除建筑 ID，核对 [manifest](../apps/web-preview/public/scene/manifest.json) 与 [扩展审计](../data/metadata/campus-expansion-audit.json)，保留旧 ID 的迁移记录，补充对应内外部行并重算统计。CSV 是可人工编辑的工作清单，不是自动生成的实时场景清单。
4. 继续维护项目开发日志。涉及照片、影像或外部模型时，参照[参考图像档案](../data/reference-images/README.md)和[许可说明](../LICENSING.md)；不得将查阅权限视为再分发或改编许可。

主要证据：[校园扩展与分类](campus-expansion.md)、[地表与区域影像](phase13-environment-comfort.md)、[场景道具](campus-life-navigation.md)、[室内运行方式](interiors-mobile.md)、[Knight 细化与局限](knight-refinement.md)。


**2026-11-03 后续：**EMU 第 216 棵程序树依据 2024 航拍复核被局部抑制；现为原始 600 棵、可见 598 棵。详见 [单树证据](emu-tree-216.md)，等级不变。


**2026-11-10 local refinement record:** Knight Library retains level 2 after source-pinned balcony and tall-window reveal additions; the generic squirrel retains level 1 after close-up color accents. The CSV links the tested standalone exports and their limitations. No interior, placement, species or measured-geometry status was promoted.


**2026-11-10 inventory reconciliation** recorded 1,082 unique rows, up from the first 1,081-row baseline after the addition of `PERSON:dan-carrere`. The reconciliation kept the 534 original exterior identities and their 534 planned interior rows.
