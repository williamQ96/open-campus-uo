# 五栋校外住宅的外部模型核对

2026-11-24。按 Knight Library 外部样例逐栋核对比例、主要立面、材质、可编辑几何与默认场景行为。评级为 L2，场景仅在本地更新。

| 场景 ID | 地址和名称 | 模型及证据 |
| --- | --- | --- |
| `roof-5f1a5ce2` | 1414 E 18th Ave，The Lewis | 以 Emerald Street 转角照片定位西立面。恢复水平窗带、窗间深色板和北端双层门廊。下层窗数和门槛仍为近似。[市政房屋清单](https://www.eugene-or.gov/AgendaCenter/ViewFile/Item/3?fileID=10) · [物业图集](https://www.thelewisandclarkapts.com/gallery) |
| `roof-4cb05afd` | 1424 E 18th Ave，The Clark | 地址与独立屋面对应，保留西侧建筑间隙。共用物业图集支持临街门廊的外观，挑台位置及相邻侧墙窗列使用近似值。[市政房屋清单](https://www.eugene-or.gov/AgendaCenter/ViewFile/Item/3?fileID=10) · [物业图集](https://www.thelewisandclarkapts.com/gallery) |
| `roof-175d8088` | 1442 E 18th Ave，Student Manor Apartments | 物业照片支持街侧角石、窄阳台、层间材质带和长立面三行可见窗。模型近似窗距、标牌位置和入口细部。[物业照片](https://www.greystoneproperties.com/student-manor-apartments/) |
| `roof-57cd5529` | 625 E 16th Ave，Royal Terrace | 保留不等长两翼、北侧檐下通道和开敞庭院。复建照片所示的外梯、透空格栅、挑台、铺装和低矮喷泉。植物位置和外梯尺寸为近似。[物业照片](https://www.rent.com/apartment/royal-terrace-eugene-or-lc6686672) |
| `roof-4855fc7e` | 622 E 13th Alley，Coho Townhouses (North) | 北排独立配准。复建木板、凸出的金属肋板窗舱和南侧巷道入口。保留拟合的双坡屋面。窗舱和门位尺寸为近似。[市政项目卷宗](https://www.eugene-or.gov/AgendaCenter/ViewFile/Item/66?fileID=77) · [物业照片](https://www.new.paradigmpropertiesnw.com/properties-coho-townhouses.html) |

[可编辑配准及来源](../data/metadata/residential-exterior-review.json)锁定场景底图、地形、既有屋面来源、州轮廓编号、2024 航片和实景图哈希。几何源由[生成脚本](../scripts/build-residential-exterior-review.py)和此配准文件共同组成。分层外墙、窗、雨棚、栏杆和铺装采用原创几何。场景包包含原有屋面几何和新的可编辑外观，照片用于参考。

## 验证

- 9 组前后视图覆盖 18th Avenue 三栋、Royal Terrace 庭院及 Coho 北排。10,102 个屋面采样点与原拟合的射线交点在浮点精度内一致。
- 检查 7,710 条有效路线边，未新增净宽冲突，最近模型与路线边距离 2.482 米。Royal Terrace 两翼和喷泉有碰撞，檐下及喷泉旁的通道可走。
- 从两个源批次移除属于这五栋的 1,256 个三角面。逐项比对保留的索引、属性和候选 ID。五个旧屋面处理在独立外部包加载时省略，场景中其余 24 个处理继续启用。
- 在桌面和移动端核对七处可达入口和五个搜索名称。损坏网格、错误地形哈希与最后一段源锚点异常均恢复先前场景。默认场景有 515 个可选建筑、418 个源批次成员、139 段道路及 550 株树。
- 阶段包、重复导出及生产包的模型和描述文件哈希一致。台账共 99 项 L2、429 项独立 L1、21 项历史映射。[室外台账](asset-refinement-inventory.md)。

实景图中的门号、窗户开扇、五金和现场门槛高程需进一步核对。Coho 南排是另一个候选，仍待独立核对。
