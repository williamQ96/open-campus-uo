# 项目开发日志

[English](DEVELOPMENT_LOG.md) | **简体中文**

本日志仅属于 **Open Campus: UO 下游项目**。每次项目改动同步记录目的、结果、验证和发布状态，按新到旧排列。历史条目保留，纠正另记；不补写未经核实的历史。英文为主，中文同步维护。

上游仅记录可复用的方法、算法、接口和验证实践，见[方法论日志](https://github.com/williamQ96/open-geospatial-to-3d-reconstruction-pipeline/blob/main/METHODOLOGY_LOG.zh-CN.md)，本地文件位于相邻上游仓库。下游开发日志、校园专属更新记录不复制进上游。发布与部署状态见下方最新记录。

## 2026-11-03 - 资产精细化清单（本地）

- 新增可维护清单：534 条建筑外部、534 条待创建的独立内部，以及 13 条现有环境、道具、共用室内和角色动物条目。按用户基线，Knight 外部为 2 级，其余现有资产为 1 级；未创建的内部不评级。3–5 级等待用户标准。
- 已核对唯一 ID、内外部建筑 ID 与 manifest 的对应关系、状态等级和证据路径。清单仅在本地，未提交、发布或修改模型。见[清单](docs/asset-refinement-inventory.md)。

## 2026-11-03 - Knight Library 北立面细化（本地）

- 保留建筑 ID、校园位置、主要体量与现有 Architectural Toon 配色，细化双入口、窗上题板、层间装饰和檐口。参考资料与推测尺寸见[细化说明](docs/knight-refinement.md)。
- 使用 Blender 4.5.15 重建试点及校园扩展层。扩展审计通过：534 个唯一建筑 ID，未嵌入照片。已检查单体渲染，42 项预览单元测试通过；本地浏览器中检查了校园位置、朝北立面和卡通材质，控制台无警告或错误；未测试硬件性能。现有示意树木遮挡了部分建筑。本地更改，未提交或发布。

## 2026-11-01 — 发布确认：0.13.0 已部署并通过匿名线上核验

- 实现 [ba2aeb8](https://github.com/williamQ96/open-campus-uo/commit/ba2aeb8a8649023973990274e3e5b51f835ba4a5) 已推送，[GitHub Pages 部署](https://github.com/williamQ96/open-campus-uo/actions/runs/41349051268) 成功。[线上地图](https://williamq96.github.io/open-campus-uo/) 匿名 HTTP200，iteration16，534 入口。
- 线上卡片／精确占位文字／标签隐藏、本体悬停与点击、无 hero 的 Overview 教室且无角色／室外GLB请求、返回位置／构图精确恢复、普通 E 进入有 hero 的第一／第三人称教室、390px 手机拖拽走／满拖跑／取消、无 Run 按钮／页面溢出均通过，零页面异常。校园／地面／教室三个线上 GLB 哈希与本地一致。[生产证据](data/metadata/release-v013-verification.json)，诊断截图仅留本地。
- 发布锁固定干净上游 16e754a（pipeline0.12.0／模板0.4.0），[上游CI](https://github.com/williamQ96/open-geospatial-to-3d-reconstruction-pipeline/actions/runs/41348974431) 全部通过。下游来源／图片／资产／地理／地面审计成功。本记录时[完整下游浏览器工作流](https://github.com/williamQ96/open-campus-uo/actions/runs/41349051286) 仍在运行，其格式／JS／构建步骤已通过，完整浏览器回归尚未结束，不声称远端完整套件已通过；本地历史专项证据单独保留。
- 本次仅文档／证据确认，[skip ci] 不改变运行时／资产／部署；旧待发布／本地条目保留原采集上下文。开发日志仅下游，方法日志仅上游，附件与本地诊断排除上传。

## 2026-11-01 — 发布批次：Open Campus: UO 0.13.0

用户授权上下游累计两批推送并部署 Pages。本版合并 iteration15 手机拖拽走跑、534 推断入口、可导出通用教室与独立世界／GPU 生命周期，以及 iteration16 Overview 卡片、无 hero 观察教室和轻微悬停。共享运行时固定到干净上游 16e754a918e87d77cebc8e511e5932191f8d4924（pipeline0.12.0／模板0.4.0），dirty=false；旧模型生成、phase15/16 本地记录与重建 pin 均保留原溯源。本地 34 上游 Python、双方各42 JS、上游完整17例浏览器及下游搜索／室内／卡片／手机／导航／地标专项通过。源模型／地理几何保留，新原创教室 GLB 已登记。本记录准备发布，部署后补录 Actions 与匿名线上核验。开发日志／美术／证据仅在下游，通用方法在上游，附件与本地截图／trace 不上传。

## 2026-11-01 — 本地待发布 iteration 16：Overview 建筑卡片、观察教室与悬停

- Overview 点击标签／建筑本体或搜索选择，打开单张建筑锚定卡片：顶部名称，中间精确占位 to be fill，底部 Enter，附关闭按钮。只隐藏该栋普通标签，关闭或切人物视角后恢复；其余标签／避让、世界锚点、搜索构图、手机横竖屏和人物模式原选择面板保留。
- Overview 的 Enter 用显式 URL 模式打开纯观察教室：打开天花板、Overview 旋转／平移／缩放，不创建室内 hero／请求 hero 模型。室外 hero 保留原校园位置，返回恢复原位置与构图。Follow／First-person 门口进入仍有可玩的三视角教室。沿用独立世界／GPU 释放边界，不添加隐藏常驻校园。
- 鼠标悬停给独立建筑轻微 emissive 提亮，选中更强且持续，清除悬停不清选择。合批背景按稳定轮廓 ID 和边界容差解析，仅画该栋源轮廓提示以保持合批。每 80 ms 最多处理一次待拾取鼠标位置，拖动／弹窗跳过，移出清除，触摸不产生 hover。不降低画质、不重建地理或美术资产。
- 验证：34 上游 Python、双方各 42 JS、上游完整浏览器 17 例，双方格式／构建通过。下游专项首轮 7/9 通过，两处仅为测试使用动态 :visible 定位器及假设背向镜头的标签可见；改用稳定 ID／搜索面向后，卡片／悬停／手机／观察进入 3/3 通过，搜索／普通室内 6/6、导航／地标／材质 4/4 通过。原生 UO 检查确认 Chapman Hall 卡片文字、标签隐藏、heroPresent=false／player=null／原 outsidePlayer 保留、无角色模型请求、室外位置／构图精确恢复、零页面异常。[证据](data/metadata/phase16-verification.json)、[设计](docs/zh-CN/interiors-mobile.md)。截图保留本地 artifacts；既有 Vite 共享代码体积提示不变，不声称手机 FPS。
- 归属／状态：通用实现与卡片／观察／悬停方法在本地上游独立记录，iteration16 与本项目日志仅留在下游。43 个托管文件哈希与上游一致，dirty=true 如实表示未提交。本批及上一批本地改动未提交／未 push／未部署；线上 0.12.0 及历史模型／参考证据保留。本地 http://127.0.0.1:5173/。

## 2026-11-01 — 本地待发布 iteration 15：手机拖拽调速与建筑室内

- Follow／First person 下半屏拖拽连续控制停止、行走至 4.6 m/s 跑步（6 px 死区／48 px 满幅），上半屏独立转向；取消独立 Run 按钮。实际位移决定步态，步声继续按距离匹配；键盘／Shift／跳跃和触摸取消保留。
- 534 个建筑记录均有原创绿金推断门，534 接近点均通过现有建筑轮廓碰撞检查。三视角鼠标点门或触摸进入，人物模式靠近可 E／Enter。全部先共用原创推断的 24 × 18 m 教室：15 套桌椅、讲台、黑板、窗、天花板、家具碰撞与出口；保留三视角、移动与音频，Overview 隐藏天花板。这不是实测入口、无障碍条件或真实 UO 平面图。
- 动态校园／室内入口、整页导航、pagehide 显式释放渲染／GPU 资源和 BFCache 重建，保持单一活动世界。生产预览室内不请求室外 GLB 或校园代码 chunk。session 记录恢复室外位置、人物朝向、镜头构图／模式、密度／晃动／显示／声音；存储无效／禁用安全回到默认出生点。导航、选择、NPC 轨迹、beta／开发者状态重新开始。稳定 ID 门位覆盖可用于后续逐栋校正与独立室内精细化。
- 原创教室 GLB 162,700 字节、10 mesh、无内嵌图片，SHA-256 397a9825a4efe1c2d9136f80c2b9ef056254148b9c023ccbcbb4485ed450489e，已登记为 CC BY 4.0；参数化代码／导出脚本 Apache-2.0。无新增照片或第三方资产；既有校园／地面模型与溯源不变。通用实现与设计已回流本地上游并独立记录方法日志，具体资产／证据及本开发日志仅在下游。
- 实测：上游 34 Python、双方各 40 JS、格式／构建通过。上游完整浏览器在新增禁用存储例前 13 例通过，再通过最终室内专项 4 例。下游完整首轮 27/28 通过，唯一失败为写死旧 iteration14 的反馈测试，已改读当前配置；手机／音频／反馈／室内专项 10/10 通过，最终含禁用存储的室内 4/4 通过。当前全部 29 例分批覆盖，不声称新跑过一次完整 29 例。23 资产、534 建筑身份、70 路径／20 固定点、地面高度审计通过。生产预览证实位置／模式精确恢复，Low 密度／No 晃动／静音保留，室内无室外 GLB／校园代码请求、无页面异常。[设计说明](docs/zh-CN/interiors-mobile.md)、[验证记录](data/metadata/phase15-verification.json)。既有 Vite 共享代码体积提示保留。
- 最后调整：进入时人物朝向黑板，Follow 镜头高度保持在天花板内；调整后下游 E 进入／返回专项通过，格式／构建仍通过。
- 状态：仅本地未提交，未 push／部署，线上仍为 0.12.0。41 个托管文件与上游逐字节一致，viewer lock 以真实基线记录 dirty=true；保留历史重建证据及用户附件。本地 http://127.0.0.1:5173/ 可体验。

## 2026-10-31 — 发布确认：0.12.0 已部署并匿名核验

- 实现 [f26e5a5](https://github.com/williamQ96/open-campus-uo/commit/f26e5a511b471ad9095baeebb62be863a1011ca3) 已推送，[Pages](https://github.com/williamQ96/open-campus-uo/actions/runs/41277741074) 成功。[线上](https://williamq96.github.io/open-campus-uo/) 匿名 HTTP200，iteration14、Overview near32米、有骨骼角色、18组云、Mid29实例、雾缓存关闭。
- 搜索、三视角、No密度、Beta启退、390px无溢出通过，JavaScript零错误。34,638,580字节校园模型和9,630,380字节地面均与本地SHA一致。[线上证据](data/metadata/release-v012-verification.json)。
- 固定干净上游64ed0a2，[上游检查](https://github.com/williamQ96/open-geospatial-to-3d-reconstruction-pipeline/actions/runs/41277680207)通过，下游素材／地理／地面核验通过。本记录时[完整下游浏览器工作流](https://github.com/williamQ96/open-campus-uo/actions/runs/41277741143)为 in_progress／等待最终结果；本地完整24项已通过，不把未完成的远程检查称作成功。
- 本证据跟进仅文档，使用[skip ci]，不改运行代码／资产／部署。旧本地条目保留原状态，发布状态以本确认更新。开发日志只下游，方法上游；附件和trace不上传。

## 2026-10-31 — 发布批次：Open Campus: UO 0.12.0

用户授权累计改动一起 push 并更新 Pages。本版合并 12–14 批：屋顶、seed 语义活动、开发工具、Zombie School／重启、天空／云／地面、晃动滑块、行人绕行与深度／不降质 CPU 修复；静态雾缓存关闭。运行代码同步到干净上游 `64ed0a21898d8f156bc8657595a5407629491bb1`（pipeline0.11.0／模板0.3.0），dirty=false；历史几何与本地测量保留原真实来源。上游34 Python、两边各35 JS、上游9／下游24完整浏览器、格式／构建及素材／地理核验已通过。本提交准备发布，部署成功和匿名访问结果完成后另记。开发日志／资产只在下游，方法在上游；排除用户附件、trace、原始大数据与 Blender 备份。

## 2026-10-31 — 本地待发布迭代 14：远景闪烁与不降质渲染评估

- **诊断／修复：**同一镜头在 near=0.08 米复现浅色屋顶条纹，只改为 16 米即可消除。查看器依据静态地图包围盒、8 米余量、盒外距离十分之一及向下二次幂量化自适应 Overview near，上限 64 米，初始校园视图为 32 米；Follow／First person 及盒内仍为 0.08 米。保留屋顶／铺装材质、几何、FOV 与 far。
- **默认优化：**63 个世界坐标标签使用独立小 CSS 场景，缓存 184 静态节点变换，小地图输入不变则不重画，坐标文字不变则不替换。活动角色、标签投影／固定／更新频率、路径失效、三视角、抗锯齿、像素比例、光照与人口均保留；不重建资产、不减面。
- **评估：**RTX5090 原生无头 Chrome 旋转标签 CPU 0.334→0.191 ms，约减少 43%；渲染提交 1.405→1.249 ms。统计网格顶点 1,585,723、稳定帧 947,049 三角面／229 绘制保持一致，像素比例不变。CPU 限速／DPR2 压力测试也降低标签开销。原生已近 120Hz 上限，不能称整体 FPS 提升 40%，也不等于内置浏览器或手机保证；独立原生环境未复现所报内置浏览器明显掉帧。
- **默认未采用：**静态雾缓存的 Toon／PBR 对照均仅一个像素一条通道差 1，但多次 GPU 收益小且不稳定，增加 5,166,728 字节属性、CPU／GPU 副本及载入计算。UO 明确 cache_static_haze=false，默认额外缓存顶点／属性为零；保留实验与精确记录，不称通用提速。
- **验证：**上游 34 Python／35 JS、下游 35 JS 通过；完整浏览器上游 9／下游 24 项通过。两边格式／生产构建通过；22 资产文件、17 图源、534 建筑身份核验通过。GLB／Blender／图源及旧证据不改，运行哈希与上游一致且 dirty=true。见[报告](docs/zh-CN/overview-performance.md)与[验证](data/metadata/phase14-verification.json)。保留 Vite 原大包提示。
- **归属／状态：**通用深度、缓存和按证据选择实验的方法进入上游本地方法日志；校园测量、截图、iteration14 与开发日志只在下游。仍未提交／push／部署，两边基准与线上不变。没有公开 profiling API 或新增统计，检查引用只注入独立测试页。

## 2026-10-31 — 本地待发布迭代 13：天空、晃动、绕行、重启与地表

- **行为：**蓝色渐变天幕、18 组合并柔边方块云，尊重系统减少动态效果。第一视角改成 No／Low／Mid／High，默认 Low；垂直幅度上限 0／3／6／10.5 毫米，侧向同比、无滚转，不改脚步和骨骼相位；系统减少动态效果优先置零。
- **碰撞恢复：**步行学生先等待，再于内缩的人行铺装中尝试绕行，按正常速度回归原固定路线。扣除孔洞、建筑和车行面，缓存高度、统一接触余量，每帧最多一个规划请求；空间不足继续让行，不跨生境脱困。
- **僵尸恢复：**考虑高度的接触只触发一次并暂停。UI 下方盖 30% 黑色场景遮罩，上方居中 You are dead；Escape 不能跳过。Restart 重载原面向 EMU 的 T 字路口与新开页面默认值，包括 Overview、Mid 密度、Low 晃动、Beta／开发者关闭。
- **地表开发：**归档第二张公共领域 USDA NAIP 参考，覆盖完整 2 × 2 公里，两幅源图均为 2024-06-08。平滑大范围颜色后推断草地、建筑周边、城市混凝土／沥青并加原创磨砂颗粒；日期、范围、许可和哈希留在图片库，Google 截图仅说明区域。新增独立可编辑地面 Blender 源及无照片纹理 GLB，增加 9,630,380 字节／320,000 三角面。保留原地形用于物理／检查，只绘制一层完整底面，解决重复底面深度闪烁。本批不改原道路或 534 建筑身份。
- **验证：**上游 34 Python／31 JS、下游 31 JS 通过；上游 8 浏览器、下游完整 21 浏览器项通过，再通过 2 个新增地面／材质／手机死亡窗用例。两边格式和生产构建通过。资产 22 文件、图源 17 张、语义路线 70／点位 20、建筑 534 通过；新底面相对原高程的最大浮点导出差 0.00000376 米，无嵌入照片纹理。见[本批说明](docs/zh-CN/phase13-environment-comfort.md)与[证据](data/metadata/phase13-verification.json)。保留 Vite 原大包提示，未宣称真实手机 FPS。 最后将遮罩与标签置于同一场景层，随后 4 个消费者浏览器项通过，并重新生成两边构建。
- **归属／状态：**通用环境、舒适度、绕行与终止恢复约定在上游本地维护，独立写方法日志。图片、分类、Blender／GLB、截图和开发日志只在下游。第 12＋13 批仍本地未提交、未 push、未部署，基准提交与线上页面不变，运行模板锁如实为 dirty。

## 2026-10-31 — 本地第 12 阶段：步态 bugfix、屋顶、语义模板与 Zombie Beta

- **Bugfix：**声音与模型改为真实位移驱动的同一步态相位。步行／跑步 1.7／4.6 m/s，落脚间距 0.95／1.5 米，普通步行约每秒 1.8 次，避免原来每秒超过 4 次的节奏。采样实际 GLB 的 65 个姿态，配置 0.15625 循环的落脚偏移，来源哈希及标记见 `data/metadata/gait-calibration.json`。第一视角最大垂直 3 毫米、侧向 1 毫米、零滚转，仍可关闭并尊重减少动态效果。手机增加按住 Run，松手／重置取消，便于跑离僵尸。
- **屋顶 dev：**534 个身份均有明确推测语法：坡顶／金属／瓦／石板，或平顶／女儿墙／分缝／采光与设备；外围预算更低。地标保留已有几何并处理屋顶颜色／浅构件，不宣称新照片证据。新源 `assets/roof-refinement/eugene-campus.blend` 保留 534 个独立建筑，旧源不变；重新打开确认没有使用旧灰色 roof 材质。GLB 仍 93 个语义网格，由 25,382,236 增至 34,638,580 字节，明确承担几何与下载成本；成功导出临时文件后原子替换。
- **路径 dev：**70 条预编译固定路径（14 人行、8 行车、40 草地、8 树上）及 20 个停车点位，对实际铺装／植被掩膜审核，不回退其他类别。归档旧活动 v1，新活动 v2 缓存高度和原始转角，导航保持 v1。树锚点存配置，无需忽略目录中的中间文件即可重建完全相同的活动数据。
- **模板 dev：**共享基础素材，仅生成当前实例；Mid 29、High 目标 74、No 零，实际销毁资源而非隐藏高档池。按版本化 seed 重放学生 m/f 形象、截断正态身高、连续肤色、六发型／五背包／颜色／速度及走跑状态；车辆、骑行者、松鼠也有变化。头发和背包按附着点合批；普通 NPC 每帧不再分类建筑和地形，不承诺未测的硬件 FPS。
- **开发入口：**About → Developer mode 默认关，点击无遮挡 NPC 查看／复制模板、seed、属性、路径／点位和当前状态；关闭入口或移除对象清空面板，Beta 怪物也可检查，保留未来扩展入口。
- **Beta dev：**Beta functions 与 Settings／About 一级并列。ZOMBIE SCHOOL!!! 主动开启，保存／恢复原密度，开启时销毁普通 NPC 和道具，在 160 米范围空地尝试生成 28 个统一原创 Q 版怪人。12 米圈内以 0.45 m/s 游荡，≤30 米吸引、2.2 m/s 追逐、>60 米脱离并重设中心。共享几何／材质，保留碰撞、限频绕障、对话框暂停和退出销毁；未加入攻击／伤害。
- **验证：**上游 34 个 Python、26 个 JS，下游 23 个 JS 通过；完整浏览器回归上游 6、下游 19 个通过，实际骨骼偏移校准后又通过声音专项。两侧格式及构建、20 个资产、16 张原参考图、语义路径／点位和地理不变量审核通过。检查屋顶、六种人物发型／背包、怪物和开发面板。首次触屏测试错用了 CDP 释放触点，纠正测试后原生松手检查通过。Vite 原有大分包提示仍在，未做实体设备 FPS 结论。
- **回流／状态：**通用编译器、seed 模板、步态偏移、开发入口、Beta 生命周期与 Zombie 模板已在相邻上游本地实现并写中英文方法；校园配置、资产和开发日志仅在下游。未提交、未 push、未部署，下游基于 `30b20091909811ffd003960bb5ddf4260b0b3c42`、上游基于 `c02f6cd3098dcff2635f4d9a347f9308639bc1f3`；模板锁 `dirty: true`，正式版本／网站保持不变。见[阶段说明](docs/zh-CN/phase12-npc-beta.md)。

## 2026-10-31 — 发布确认：上下游已 push，Pages 已更新

- **在线网页：**[Open Campus: UO](https://williamq96.github.io/open-campus-uo/) 已更新，无需登录。已部署实现为 [`b6a9cc54d8beac7a19574601faf4f94381d3afcb`](https://github.com/williamQ96/open-campus-uo/commit/b6a9cc54d8beac7a19574601faf4f94381d3afcb)，应用版本 0.11.0。
- **上游：**通用实现 [`6b15ce8`](https://github.com/williamQ96/open-geospatial-to-3d-reconstruction-pipeline/commit/6b15ce8878051dbbd0928d4332f507e6a5df4780) 与方法论发布记录 [`c02f6cd`](https://github.com/williamQ96/open-geospatial-to-3d-reconstruction-pipeline/commit/c02f6cd3098dcff2635f4d9a347f9308639bc1f3) 均已 push。干净的运行时锁有意指向实现提交，后续方法记录仅改文档。
- **GitHub 检查：**[上游实现](https://github.com/williamQ96/open-geospatial-to-3d-reconstruction-pipeline/actions/runs/41264186786)、[上游记录](https://github.com/williamQ96/open-geospatial-to-3d-reconstruction-pipeline/actions/runs/41264324084)、[下游检查](https://github.com/williamQ96/open-campus-uo/actions/runs/41264257199)、[Pages 部署](https://github.com/williamQ96/open-campus-uo/actions/runs/41264257127) 全部成功。已提交实现通过全部 16 个下游浏览器用例，以及资产／媒体／地理不变量审核。
- **线上实测：**匿名 HTTP 200、3D 场景就绪；25,382,236 字节校园 GLB 的 SHA-256 与本地一致。Mid 有 29 个活动／道具碰撞体，含 8 只松鼠；No 清空。三视角、建筑搜索与反馈窗口可用。音乐、脚步和松鼠文件与本地完全一致。390px 窄屏无横向溢出，无页面 JavaScript 报错。没有创建真实反馈 Issue。见[结构化发布证据](data/metadata/release-v011-verification.json)。
- **归属与来源：**项目开发及部署记录仅在本下游；上游只存方法论记录。历史重建／艺术来源哈希与真实生成状态保留；聊天附件和 Blender 备份未上传。
- **补记提交：**本次最后补记与当前状态文案仅改文档，不改变已测试上线代码；提交以 `[skip ci]` 避免对发布证据重复整套测试，上述实现和部署结果均对应明确的已测试提交。

## 2026-10-31 — 发布批次：Open Campus: UO 0.11.0

- **范围：**合并发布此前本地批次：固定步行导航起点；照片规律驱动的地标／校园细化、534 个风格化建筑及外围雾化；四档密度、开放松鼠与碰撞；音乐、实际地面位移脚步、支持减少动态效果的第一视角轻微晃动；下游 GitHub 反馈草稿。保留三视角、搜索、小地图、导航与手机操作。
- **归属：**开发日志与校园资产仅在下游；通用方法、模板与方法论记录进入上游。聊天附件、测试产物和 Blender 备份文件不上传。
- **上游锁：**通过哈希校验同步至干净的上游提交 `6b15ce8878051dbbd0928d4332f507e6a5df4780`（pipeline 0.10.0，模板 0.2.0），运行时锁如实为 `dirty: false`。历史生成锁、模型哈希及艺术层生成时的 dirty 记录保持原样，不假装重新生成。
- **验证：**发布前上游 32 个 Python、上游 19／下游 16 个 JS、格式与构建及资产／媒体／地理不变量检查通过；实现批次完整浏览器回归为上游 4、下游 16 个用例。GitHub Actions 将检查已提交文件并构建部署静态站点；完成后另记线上验证。
- **状态：**用户已授权这几批一起 push 并更新网页；上游实现已 push，本下游提交准备 Pages 发布。此前仅本地条目作为历史保留，确认上线状态见后续部署记录。

## 2026-10-31 — 本地第 11 次待发布迭代：密度、松鼠、声音与反馈

- **行为：**两组开关合为 No / Low / Mid / High，默认 Mid。No 清除移动 NPC、固定道具及碰撞体，保留角色与地图。增加开放松鼠模型、估计的固定路线和停顿；按类别设置胶囊体，角色分步检查，NPC 停止让行。目标数量受可用空间影响。
- **资产：**保留 Innerscene CC0 松鼠原始 GLB、IntelligentGene / Another Page Studio 的 CC0 Overworld (BGM) MP3、来源许可与哈希。改编松鼠为 900 三角面、单材质、无图片依赖的 93,480 字节 GLB，保留 Blender 源并清理未使用的导入材质和图片。脚步为原创确定性合成 WAV，CC0。About 和 NOTICE 同步署名，原始 CC0 不改协议。
- **声音／行走：**Directions 旁主声音按钮默认开；受浏览器自动播放限制时首次交互重试，后台暂停。第一和第三视角脚步依据真实地面位移；静止、受阻、空中、总览和对话框时停止。第一视角轻微晃动不改变角色和导航坐标，支持设置关闭与系统减少动态效果。
- **反馈：**按用户确认使用 GitHub 登录后确认创建。内容必填，标题与坐标可选；缺省标题含 UTC 草稿标识及迭代号，坐标默认空。预填本项目 Issue，反馈者在 GitHub 登录确认；保留草稿、弹窗备用链接、长内容复制，不宣称网页已创建，不发送内容或坐标到统计。未创建测试 Issue。
- **回流：**通用密度、碰撞、资产／音频配置、行走反馈与 Issue 草稿在上游模板实现并同步；上游中英文记录尽早白膜交互、中等精度、来源与推测结合、用户反馈和主动细化的循环。校园素材、路线和开发日志仅在下游。
- **验证：**下游 16 个 JS 单测、全部 16 个浏览器用例、格式及生产构建通过。上游 32 个 Python unittest、19 个 JS、4 个合成场景浏览器用例、格式与构建通过。19 个资产文件、16 张参考图、534 个建筑的地理不变量审核通过。重新打开 Blender 核验单个 900 面网格且无图片材质依赖；音乐原件与运行副本一致。验证四档 0/7/29/74 个碰撞体、No 清空、音频开关、实际位移脚步、减少动态效果、可选坐标反馈及 320px 窄屏。原三视角、双指手机操作、搜索和固定起点导航保留。测试使用 Chrome/SwiftShader，不代表实体手机性能；Vite 原有大分包提示仍存在。
- **证据：**[交互说明](docs/zh-CN/ambience-feedback.md)、[资产档案](data/asset-sources/campus-life/README.zh-CN.md)、新增单测和浏览器用例；本次未重建校园建筑与地理源二进制。
- **状态：**仅本地、未提交、未 push、未部署。下游基于 `7c6558d9272b315afad94d234db4778bc0f55d95`，上游基于 `0361592966089072333ce3bf6eea22772c5d3079`；模板锁保持 `dirty: true`。第 11 次迭代为本地反馈标识，并非已发布的软件版本。

## 2026-10-31 — 本地待发布批次：校园与外围背景分层细化

- **需求：**继续既有卡通建筑画风，从照片提炼规律而非照片级复刻；低成本升级外围白模，保持建筑坐标和道路／街区规划。
- **模型：**保留旧试验区源文件，用新归档的两张 CC BY 4.0 原照细化 Gerlinger Hall／Annex，并补充 Knight Library、EMU、Johnson Hall 的浅构件。534 个记录全部加入风格化外观，艺术重点区 135 个、背景 399 个；类型／配色／屋顶按稳定 ID 固定随机，原坐标、轮廓和高度记录不变。
- **景观：**保留原 300 棵航片线索引导的树，新增 300 棵明确标注为推测的树及校园草地，不声称使用了新航片提取。
- **维护与导出：**新 Blender 源保留 534 个独立建筑对象，共 542 个源网格；仅导出时把 470 个匿名 ID 合并为 21 个网格，运行 GLB 共 93 个网格，约 25.4 MB，无嵌入照片。旧精细源文件与旧模型保留。
- **浏览器：**默认开启固定区域的外围雾化、降饱和与淡色滤镜，重点区清晰；可用 Background haze 开关对比。顶点计算与高度场偏移元数据降低重复计算。保留全部交互、NPC／道具开关及上一条的固定导航起点。
- **证据：**[照片与许可](data/metadata/campus-expansion-photo-evidence.json)、[逐建筑审计](data/metadata/campus-expansion-audit.json)、[说明](docs/zh-CN/campus-expansion.md)。素材登记现有 16 项批准记录；二进制逐字节校验，文本原始 hash 外补 LF 标准化 hash，处理跨平台换行。
- **目前验证：**上游 32 项 Python、15 项 JS、4 项浏览器测试通过；下游 12 项 JS、全部 13 项浏览器测试及格式／构建通过。地理身份、旧源文件、素材许可／校验及零嵌入照片审计通过。最后再次检查按建筑独立保存的 Blender 源。
- **最终导出检查：**重新打开保存的 Blender，确认 542 个源网格及 534 个独立且唯一的建筑对象。最终 GLB／源文件校验值与全部运行时身份审计通过；针对最终导出再次运行的 13 项下游浏览器测试全部通过。共享运行时代码与本地上游文件、如实标记 dirty 的版本锁一致；HEAD 和跟踪版本未变。
- **范围与状态：**具体项目记录只在本日志；通用分层方法、算法、显示与验证实践记入上游方法论日志。下游基线仍为 `7c6558d9272b315afad94d234db4778bc0f55d95`，上游基线仍为 `0361592966089072333ce3bf6eea22772c5d3079`。全部本地未提交，未 push、未部署；运行时及新艺术层如实标记本地方法版本未提交。

## 2026-10-31 — 本地待发布批次：固定步行导航起点

- **原因：**蓝色起点跟随角色移动，视觉不舒适。
- **行为：**第一人称／Follow 在点击 Start route 时保存 A；之后行走不重算、裁短路线，也不移动蓝色圆点。角色与小地图定位点、白色箭头动画及到达检测继续更新。
- **视角：**第一／第三人称之间切换保留同一起点。Overview 的手动 A 独立保留，返回步行模式恢复原起点。再次 Start route 从当前位置开始新路线；Clear 或重选端点重置起点。
- **界面：**活动路线的英文 A 文案改为 “You · fixed starting point”；同步修正文档。
- **验证：**导航／活动专项浏览器测试 **3 项通过**，覆盖两种步行视角各移动超过 6 米后整条路线不变、视角切换、重新开始与 Clear。后续检查结果完成后补记。
- **完整检查：**下游 **10 项 JS 测试、全部 13 项浏览器测试**通过，覆盖手机触控、搜索与跳跃回归，格式检查及生产构建通过。上游共享模板 **12 项 JS 测试、4 项浏览器测试**及格式／构建通过。本地运行时代码与版本锁、上游文件校验一致。两个仓库 HEAD 和跟踪版本仍为上述基线，没有 commit、push 或部署。
- **日志：**从本条开始持续记录。先前工作保留在[校园活动／导航说明](docs/campus-life-navigation.md)、[视觉细化记录](docs/visual-refinement-v0.7.md)等现有文档。
- **状态：**下游基线 `7c6558d9272b315afad94d234db4778bc0f55d95`，上游基线 `0361592966089072333ce3bf6eea22772c5d3079`。本次为本地未提交修改，**没有 push 或部署**，等待与下一批一起发布。
- **版本锁：**本地 viewer lock 如实标记 `dirty: true`。下次获准发布时，先提交上游，再同步到干净版本并验证；历史地理重建与艺术模型生成的版本锁保持原有来源。

## 2026-11-03 — 自行车道具细化（本地，未发布）

细化通用自行车的镂空轮圈、辐条、座管、曲柄和踏板，保留原有布置与路线；重新导出运行时 GLB 和额外的可编辑 Blender 候选文件，保留原 Blender 文件。PROP-03 仍为 1 级；滑板车、骑姿比例和校园场景内审查仍待完成。生产构建、顶点有限值检查及独立浏览器近景检查通过，见[详情和证据](docs/bicycle-refinement.md)。共享 viewer 锁文件仍记录原 props 源文件，后续升级时需协调。

## 2026-11-03 — 环境资产批次（本地，未发布）

恢复现有推断地表图层的场景引用；为通用车辆增加轮毂、皮卡货斗，并细化滑板车。自行车已在校园场景中检查。保留共享 viewer 上游基线，并单独记录可校验的下游覆盖。生产构建、42 项单元测试、有限顶点检查、本地浏览器检查与覆盖哈希检查通过。重建脚本可能再次覆盖地表元数据；逐项实地核对及其他清单工作仍待完成。[证据](docs/environment-batch-2026-11-03.md)。

## 2026-11-03 — 植被净空筛查（本地，未发布）

新增可复现的保守二维树木与建筑轮廓筛查：树干中心均不在候选轮廓内；试点区域 7 棵树冠需进一步检查，扩展区域无候选。这不是三维相交检查或现状树木调查，没有修改几何或等级。已保存两处探索视角，见[方法和候选记录](docs/vegetation-clearance-audit.md)。恢复后的现有地表也通过完整检查（160801 顶点、320000 三角形，地形坐标保留）。

## 2026-11-03 — 云层形态细化（本地，未发布）

调整现有程序云团的尺度、方向和分块，保留合并网格及减少动态效果设置。ENV-07 仍为 1 级，季节和校园场景视角检查仍待完成。生产构建、42 项单元测试以及云层漂移／减少动态检查通过；见[前后对比](docs/sky-refinement.md)。下游天空文件哈希与上游 viewer 基线分开记录。

## 2026-11-03 — 环境资产排查与来源（本地，未发布）

记录了植物、台阶、铺装、家具和共用教室的场景视角，并检查推断入口与校园活动数量。Knight 示意台阶受到植被遮挡；完整重建试点资产可能覆盖地标细化，因此需隔离网格后修正。仅更新本次道具的来源清单大小、哈希和许可。完整资源检查现停在既有 campus-expanded GLB 与 roof Blender 哈希不一致，属于其他地标工作，未覆盖其记录。见 [13 条排查](docs/environment-triage-2026-11-03.md)。等级未变。

## 2026-11-03 — Knight 树木隔离修正（本地，未发布）

通过固定来源的运行时顶点修正与独立植被 Blender 候选文件，将一棵推断针叶树移出示意台阶。未重写建筑组合 GLB 或屋顶 Blender；修正前原子核对 68 个来源位置及 204 个拆分顶点，对照未发现其他植被顶点位置变化。校园场景检查、生产构建及 43 项单元测试通过。灌木仍有遮挡，入口并非现场测量；见[证据及重建限制](docs/knight-vegetation-correction.md)。

## 2026-11-03 — 配套灌木修正（本地，未发布）

通过第二个固定来源修正，将与先前 Knight 树木配套的推断灌木同步移开。隔离 Blender 对比显示仅 68 个树木顶点和 63 个灌木顶点平移，网格拓扑数量不变。浏览器检查、生产构建及 43 项单元测试通过；其余植物与真实通行仍未核实。[证据](docs/knight-vegetation-correction.md)。

两处 Knight 修正后的最终验证：完整校园加载与移动浏览器回归通过；灌木后续修正前校园／室内 9 项浏览器测试通过。完整 32 项浏览器运行因后续工作中断，未声称通过。覆盖记录与地表检查通过；全局资源检查仍报告先前地标资产哈希不一致。

## 2026-11-03 — 地标来源与环境重建保护（本地，未发布）

依据先前 Knight 构建记录、配置与审计中的哈希和大小、通过的扩展审计以及 Knight Blender/GLB 顶点零距离对比，更新两条过期来源记录并保留旧哈希；27 项开放资源检查通过。校园美术构建器现暂存 Blender 与 GLB 输出、核对现有环境资产，在 GLB 完全一致时保留地表和固定来源的植被补丁引用；补丁不匹配时在替换前停止。5 项保留逻辑测试通过；隔离 Blender 实际重建保留地表和两个补丁，模拟来源不符及现有资产不符时在替换前停止。其他重建路径和多文件事务不在该保护范围。见[来源记录](docs/landmark-provenance-2026-11-03.md)及[重建说明](docs/zh-CN/campus-expansion.md)。

## 2026-11-03 — 清单状态代码对齐（本地，未发布）

将 UO CSV 的状态代码统一为母仓库模板的 `existing`（现有）和 `planned`（待创建），中文说明保留共用教室回退的解释。逐行比较 1081 条记录，ID、等级及其他字段均未变；母仓库结构校验通过。该检查不验证资料真实性或质量等级。

环境修正后的最终回归：工作区副本使用本地 Chrome/SwiftShader 运行的 32 项浏览器测试全部通过，补完此前中断的测试。43 项 JavaScript 单元测试、5 项重建保留测试、27 项开放资源检查、地表与校园扩展审计、覆盖哈希及母仓库清单结构校验也均通过；不代表硬件性能测试。

## 2026-11-03 — 植被三维相交排查（本地，未发布）

新增可复现的只读 Blender BVH 检查，将此前 7 个二维候选逐一与对应手工建筑网格比较：3 棵出现表面相交（Knight 两棵、EMU 一棵），4 棵在此有限测试中未发现相交。原台阶树与 Knight 相交，修正候选未相交。未再移动其余树木：粗略净空候选约在 26–30 米外，需更好的资料和位置复核。[证据及限制](docs/vegetation-clearance-audit.md#read-only-3d-follow-up)。等级不变。

## 2026-11-03 — 航拍复核与骑手连接（本地，未发布）

对照已归档的 2024 年 NAIP 航拍及获许可的 Knight／EMU 照片检查三棵相交程序树；将位于当时开阔草坪／铺装边缘的一棵 EMU 示意树隐藏，未作 26–30 米的臆测迁移。两棵 Knight 树因树冠密集和遮挡仍待核实。原始组合 GLB 仍含 600 棵程序树，运行时显示 599 棵；新增固定来源的可撤销修正、独立可编辑候选及重建保护。调整通用自行车／滑板车骑手，使采样身高下手脚保持接触。集成前生产构建、45 项 JS 单元测试、6 项相关浏览器测试、6 项重建保留测试、隔离 Blender 构建和网格对比通过。证据与局限见[环境细化记录](docs/environment-refinement-2026-11-03.md)。等级未变。

环境恢复连接后的集成验证：先核对全部候选及目标哈希，仅执行一次写入。生产构建、45 项 JS 单元测试、6 项相关浏览器测试、6 项保留测试、28 项开放资产检查、参考媒体审计、扩展／地表审计、覆盖哈希及通用清单检查均通过；项目 Blender 网格复核与既有证据一致。仍仅为本地改动，未发布。


## 2026-11-03 — 建筑卡片资料与室外分批计划

为 32 个既有建筑 ID 接入 UO 官方来源的用途或已知使用单位，卡片显示来源和核查日期；未核实或数据不可用时明确显示未知。这是资料覆盖，不代表外观升级。新增室外资产分批计划及尚未获用户确认的对照检查项；Knight 仍为唯一 2 级建筑示例，其余等级不变。未修改各建筑内部或校园几何。隔离副本完成生产构建、45 项单元测试及 5 项浏览器测试（含手机尺寸与数据缺失）；已记录 viewer override 哈希。其余校园仍需按区域核实和逐批优化。


## 2026-11-03 — Johnson 后立面和种植细化

新增基于源资产哈希的可复用几何细节层，为 Johnson Hall 增加简化的后入口、石质门框、雨棚与台阶，以及参考照片启发的两侧灌木。2012 年 CC BY 4.0 归档参考、推断范围和前后对比记录于 docs/johnson-rear-refinement.md。未重建基础校园 GLB 或内部；建筑和 ENV-03 保持 1 级。隔离验证包括生产构建、46 项 JS 测试、7 项重建保护测试、6 项地标及卡片浏览器测试，以及固定视角场景检查。已记录细节层与 viewer override 哈希；仅本地，未发布。


## 2026-11-03 — Gerlinger Hall 和新增建筑卡片

依据归档照片新增 Gerlinger Hall 入口、栏杆和示意性的两侧灌木，作为第二个独立源哈希细节层；校园 GLB 与建筑内部未改动。来源、限制和对比图见 docs/gerlinger-refinement.md。重建保护已支持逐层验证，包括保留既有 Johnson 细节层。新增 6 条 UO 官方建筑资料，覆盖 38 个建筑。记录 Annex 照片/模型与 UO 2025 建筑调查之间待核实的不一致，未改其几何。未提升等级。隔离验证包括构建、46 项单元测试、8 项重建测试、6 项地标及卡片浏览器测试、视觉对照和哈希检查；仅本地，未发布。


## 2026-11-03 — 建筑资料补充

补充 10 条 UO 官方来源的建筑信息（总计 48 条），新增已知 ID、日期和官方 HTTPS 域名自动检查；浏览器核实 Straub 卡片。已知使用单位并非完整名单；未改变资产等级或内部。仅本地，未发布。


## 2026-11-03 — Gerlinger 身份与立面修正

对照 UO 调查与近似坐标后，Annex 的位置关系基本吻合，原拱窗老虎窗外观不符。新增可回退、绑定源哈希的现代平顶示意模型和局部花池，原 GLB 未改变。前次 Hall 细节使用东立面照片却放在北侧，现已停用并保留候选，等待准确重建。Annex 卡片补充舞蹈系官方来源。限制与视觉证据见 docs/gerlinger-annex-correction.md。未提升等级；仅本地未发布。隔离验证包括构建、48 项 JS 测试、8 项重建测试、6 项地标及卡片浏览器测试、Annex 选择测试和场景对照。


## 2026-11-03 — Gerlinger Hall 东立面

根据 UO 图纸与源网格采样确认东墙，新增绑定源哈希的山墙、窗、檐篷、入口、栏杆和示意灌木；此前错误置于北侧的候选保持停用。卡片补充 UO 人体生理学办公室资料。细节按语义类型与顶点颜色合批，解决浏览器绘制调用数超限并保留材质模式。来源、未知项与对照图见 docs/gerlinger-east-refinement.md。未提升等级，未修改基础 GLB 或内部。隔离构建、49 项 JS 测试、8 项重建测试、地标及 Annex 浏览器检查和视觉复核通过；仅本地，未发布。


## 2026-11-03 — EMU 第 216 棵程序树

依据归档 2024 NAIP 图像中该中心未见明确树冠，局部抑制一棵推断树；第 297 棵位于边界、证据不足，保持原样。源哈希补丁验证精确导出顶点并从固定 Blender 源逐字节复现，基础 GLB 未改动。源树 600 棵，可见 598 棵，包含此前第 273 棵的抑制。重建保护新增多补丁哈希和计数检查。未知项及对照见 docs/emu-tree-216.md。未提升等级，未修改建筑或内部。隔离构建、49 项 JS 测试、9 项保护测试、相关地标及 Annex 浏览器检查和视觉复核通过；仅本地，未发布。


## 2026-11-03 — 四条建筑卡片资料

新增 Computing Center、Jaqua Academic Center、Matthew Knight Arena 和 McArthur Court 的 UO 官方来源资料；现覆盖 53 个建筑 ID。数据验证及 Jaqua 浏览器检查通过；未修改几何或等级，仅本地未发布。


## 2026-11-03 — Johnson 北侧檐部铭文

依据历史调查及归档照片，使用可回退且绑定源哈希的运行时文字层，将北侧檐部修正为历史铭文 Administration Building。浏览器画布生成文字，不含照片像素；字体、比例和现状仍为近似。原 GLB、后立面层和内部未改动。来源及对照见 docs/johnson-frieze-refinement.md，建筑保持 1 级。隔离构建、50 项 JS 测试、9 项重建测试、视觉对照和地标/材质/调用数浏览器检查通过；仅本地，未发布。


## 2026-11-03 — 三条建筑资料

新增 Cascade Hall、Ford Alumni Center 及 Outdoor Program Barn 的 UO 官方信息；现覆盖 56 个建筑 ID，已知使用单位并非完整名单。资料验证和 Cascade 浏览器检查通过；未修改几何或等级，仅本地未发布。

### 2026-11-03：Friendly Hall 西立面

新增保留建筑身份的来源锁定外立面模型，归档 CC0 照片并记录学校历史资料；保留原 GLB 和 1 级状态。限制及验证见 docs/friendly-west-refinement.md。

### 2026-11-03：建筑资料卡

为 Bean、中央能源站、Collier House 和 Living Learning Center 南北两项添加五条学校官方来源资料。建筑身份及完整使用单位仍需核实。参见 docs/building-information-east-campus.md。

### 2026-11-03：Friendly 西立面及种植

依据已归档照片增加窗中梃、入口柱、水平饰带和六个示意灌木；场景选择、渲染模式及试点回归通过，等级不变。详见 docs/friendly-west-refinement.md。

### 2026-11-03：Villard Hall 东立面

以 CC0 照片及学校立面图为依据，增加保留建筑身份的简化东立面和示意种植；其他立面及尺寸待核实，维持 1 级。见 docs/villard-east-refinement.md。

### 2026-11-03：University Hall 外立面

新增来源锁定的简化双塔外观、示意种植和可复用收坡屋顶；历史资料和待核实事项见 docs/university-hall-refinement.md，等级维持 1。

### 2026-11-03：University 与 Villard 拱窗

新增可复用双朝向拱形几何，细化 University Hall 窗列和塔楼屋顶窗，以及 Villard 东立面底层窗；沿用已有历史资料与待核实说明，等级维持 1。

### 2026-11-03：University 入口与 Villard 屋顶

补充 University Hall 东西入口的示意拱门和台阶，以及 Villard 简化收坡屋顶；树木净空、通行与尺寸待核实，均维持 1 级。详见各自记录。

### 2026-11-03：Anstett 南立面

增加来源锁定的南立面及示意花坛、灌木、长椅；按学校资料补充资料卡，通用细节层支持道具语义。等级仍为 1，详见 docs/anstett-south-refinement.md。

### 2026-11-03：Peterson 南立面

复用成对建筑的通用立面语言，增加来源锁定的示意南立面及三丛灌木，并依据学校资料补充 Oregon MBA。主体接缝和尺寸尚待核实，维持 1 级。见 docs/peterson-south-refinement.md。

### 2026-11-03：长椅细节及 Knight Campus 资料卡

细化两把 Anstett 示意长椅靠背和扶手，按学校来源添加两张 Knight Campus 资料卡；Peterson 两种接缝候选因几何重叠被拒绝。等级不变，详见各自记录。

### 2026-11-03：Anstett 花坛

为两处示意花坛补充石边、土壤与分层低矮植被，并扩展可复用色板；物种和现状仍待核实，等级不变。见 docs/anstett-south-refinement.md。

### 2026-11-04：Tykeson 北侧外立面

为已有近似体量增加来源锁定的简化玻璃立面、雨棚和示意植物；来源、推断朝向、树冠遮挡及尺寸待核实事项见 docs/tykeson-north-refinement.md，等级维持 1。

### 2026-11-04：Susan Campbell Hall

增加可回退的来源锁定 L 形简化外观和折坡屋顶，以及可复用折坡屋顶组件；来源和待核实事项见 docs/susan-campbell-refinement.md，等级维持 1。

### 2026-11-04：Hendricks 外观资料核查

对照校方调查、航拍背景及候选屋顶；由于建筑边界未核实且候选遮挡现有细节，不合入候选，等级仍为 1。详见 docs/hendricks-exterior-audit.md。

### 2026-11-04：通用交通道具细节

增加车辆保险杠、后视镜、侧窗分隔及滑板车轮毂、握把、尾部反光细节；重新导出 GLB，等级仍为 1。详见 docs/prop-detail-2026-11-04.md。

### 2026-11-04：道具 Blender 版本快照

从当前 GLB 创建不覆盖旧文件的可编辑 Blender 快照，记录来源哈希，并与重新导入的五个网格比较坐标及变换。程序化源码仍是权威来源。

### 2026-11-04：Straub 西侧立面

依据校方调查增加可逆的西侧立面叠加；轮廓、窗列及入口仍为近似，屋顶与其他立面待核实，等级仍为 1。详见 docs/straub-west-refinement.md。

### 2026-11-04：Condon 东侧入口

增加依据校方资料的可逆入口、参考现有地形调整的示意台阶和灌木；建筑及环境条目仍为 1 级。详见 docs/condon-east-refinement.md。

### 2026-11-04：Fenton 南侧入口

增加依据校方资料的可逆入口叠加、示意台阶与灌木；原模型高度与轮廓仍为近似，建筑和环境条目保持 1 级。详见 docs/fenton-south-refinement.md。

### 2026-11-04：Chapman 西侧入口及建筑卡片

增加依据校方资料的可逆西入口和示意种植；建筑与环境条目保持 1 级。依据 UO 信息更新 Villard、Chiles 两张卡片的已知单位。详见 docs/chapman-west-refinement.md 和 docs/building-info-2026-11-04.md。

### 2026-11-04：Oregon Hall 立面与办公室卡片

增加依据校方资料的可逆西翼立面；最近屋顶身份与位置仍为近似，保持 1 级。依据 UO 资料更新 Lillis 和 Columbia 办公室卡片。详见 docs/oregon-south-refinement.md 和 docs/building-info-offices-2026-11-04.md。

### 2026-11-04：Oregon Hall 抬高草坪

增加依据校方调查的可逆示意草坪与边缘，尺寸、现状和通行仍未核实；ENV-05 与 ENV-06 保持 1 级。详见 docs/oregon-south-refinement.md。

### 2026-11-04：Collier House 外观及建筑卡片

增加依据校方调查的可逆外观替换，屋顶、门廊与附翼为近似；原 GLB 和室内保留，等级仍为 1。依据 UO 来源更新 Collier 与 Clinical Services 卡片。详见 docs/collier-house-refinement.md 和 docs/building-info-collier-clinical-2026-11-04.md。

### 2026-11-04：Collier 碰撞对齐

为重建外观增加经过验证的保守碰撞范围及路线检查，保留原有轮廓；示意门廊和台阶暂不可行走。图和浏览器检查通过，详见 docs/collier-house-refinement.md。

### 2026-11-04：场馆卡片及外观边界核查

依据 UO 资料更新 McArthur 与 Hayward 的场馆用途；记录 McArthur 与 Esslinger 的轮廓重叠，并拒绝未能可靠接合的 Clinical Services 屋顶候选。本轮核查未增加几何。

### 2026-11-04：Outdoor Barn 示意太阳能阵列与场馆卡片

增加依据 UO 资料的可逆示意太阳能板和可验证的几何旋转支持；屋顶身份及阵列现状未核实，保持 1 级。为 Matthew Knight Arena 卡片增加有来源的篮球主场信息。详见 docs/outdoor-barn-solar-refinement.md 和 docs/building-info-arena-2026-11-04.md。

## 2026-11-04 — Volcanology 待核身份

为 roof-399a0551 增加带源模型和轮廓校验的可选近似身份及有校方来源的教师办公室卡片；原始清单不变，仍为 1 级。立面候选因地形遮挡和屋顶穿透未合入。详见 docs/volcanology-identity-audit.md。62 项单元测试、6 项浏览器测试和生产构建通过。

## 2026-11-04 — Volcanology 示意南立面

根据校方历史照片，为待核地图匹配增加源模型校验的示意南立面，并采样地表和屋顶高度、检查正面及侧视。身份和尺度仍待核实，保持 1 级，入口与碰撞数据未改变。详见 docs/volcanology-identity-audit.md。

## 2026-11-04 — Anstett 前场景观家具

根据已归档的 2019 年参考照片，新增独立且校验源模型的两盏示意球形灯及季节性花篮。位置、物种和现状未核实，等级保持 1。详见 docs/anstett-south-refinement.md。

## 2026-11-04 — 四种通用道路车辆

统一细化四种程序化车型并修正皮卡挡风玻璃；导出增加 SUV 和对应的六模型 Blender 快照。场景位置和碰撞未改动，PROP-02 保持 1 级。详见 docs/vehicle-family-refinement-2026-11-04.md。

## 2026-11-04 — 试点长椅组

以源模型校验的顶点选择和可复用环境图层细化九张原有长椅靠背与扶手；保留座面、灯具、原位置及 GLB，并合批保持绘制预算。原步道和地面位置仍需核实；PROP-01 保持 1 级。详见 docs/pilot-bench-batch-2026-11-04.md。

## 2026-11-04 — 区域性蕨形植物

用可复用蕨形叶片及源模型校验细化三处原有示意种植，合入原林下植物批次；另八处因铺装或建筑局部冲突维持原状，位置和物种待核实，ENV-03 保持 1 级。详见 docs/pilot-ferns-2026-11-04.md。

## 2026-11-04 — 广场种植冲突

对照既有铺装和 2024 年 USDA NAIP 航拍，抑制三组广场上的推断植物，不另行猜测位置。新增可复用的源模型校验环境补丁列表及重建检查；另五处仍待核实，ENV-03 与 ENV-05 保持 1 级。详见 docs/plaza-plant-clearance-2026-11-04.md。

## 2026-11-04 — 试点球形灯组

以可复用底座和灯罩支座细化八盏原有示意灯，并合入现有金属批次；另三处位置待核，样式和位置未调查，PROP-01 保持 1 级。详见 docs/pilot-lamps-2026-11-04.md。

## 2026-11-04 — Anstett 南立面

依据历史照片连贯调整两侧窗列、砖柱、入口石框、中央竖向构件和双侧台阶侧墙。保留现有景观与原 GLB；比例及其他立面待核实，保持 1 级。详见 docs/anstett-south-refinement.md。

## 2026-11-04 — Collier 多立面外部

参考 UO 2018 年标注历史照片，补充两个示意东门廊、西侧烟囱和屋檐、门廊细节，并为新增可见实体增加保守碰撞范围；保留原足迹、GLB、植被和室内。尺度及现状未核实，保持 1 级。详见 docs/collier-house-refinement.md。

## 2026-11-04 - Villard 多立面外观

参考 UO 2017 年历史评估，补充示意性南北立面、四角屋顶、北侧台阶及保守碰撞范围。保留既有东立面、原建筑范围、GLB 和室内；尺寸及无障碍通行尚未核实，维持 1 级。详见 docs/villard-east-refinement.md。

## 2026-11-04 - Susan Campbell 多立面外观

参考 UO 历史调查，细化多格窗、六处翼楼屋顶窗及保守碰撞，并清理翼楼交界内被遮蔽的窗洞。保留原布局、GLB 和室内；入口、精确细节及无障碍通行尚未核实，维持 1 级。详见 docs/susan-campbell-refinement.md。

## 2026-11-04 - Condon 原入口与扩建立面

参考 UO 历史调查，补充示意性入口檐口、扩建外墙框架和平屋顶边缘。保留原模型、景观、导航和室内；尺寸、未见立面及无障碍通行尚未核实，维持 1 级。详见 docs/condon-east-refinement.md。

## 2026-11-04 - Friendly Hall 多立面外观

参考 UO 历史立面与屋顶图，补充示意性的南北东立面、折坡屋顶和保守碰撞范围。保留既有西立面、植被、源 GLB 与室内；翼楼体量、地形衔接及无障碍通行尚未核实，维持 1 级。详见 docs/friendly-west-refinement.md。

## 2026-11-04 - Chapman 多立面外观

参考 UO 历史评估及现有玻璃网格，细化示意性的南北檐口和多格窗。保留原平屋顶、西入口、GLB、植被、导航及室内；入口、地形和无障碍通行尚未核实，维持 1 级。详见 docs/chapman-west-refinement.md。

## 2026-11-04 - Fenton 入口方向纠正与书库

州历史档案确认此前按南侧处理的主入口照片实际为东立面，现将示意入口移至东侧，因地形待核实而移除台阶，并补充示意性南西书库窗列及屋顶栏杆。保留原 GLB、景观与室内；真实标高、细节和无障碍通行尚未核实，维持 1 级。详见 docs/fenton-south-refinement.md。

## 2026-11-04 - Gerlinger 多立面外观

参考 UO 历史照片补充示意性南侧窗户、百叶和屋顶窗及北侧翼部窗户。保留既有东立面、GLB、植被、导航与室内；原网格北侧山墙来源、标高、通行与现状细节待核实，维持 1 级。详见 docs/gerlinger-east-refinement.md。

## 2026-11-04 - Oregon Hall 东翼外观

参考 UO 调查补充示意性东翼四层横窗及屋顶边缘；未见照片的东立面为推断。保留西立面、花池、GLB、植被、导航和室内；建筑匹配、边界及通行尚未核实，维持 1 级。详见 docs/oregon-south-refinement.md。

- 2026-11-04: Added source-pinned schematic McKenzie Hall west/east exterior overlays; see docs/mckenzie-exterior-refinement.md for sources, visual checks, collision caveats and remaining level-1 gaps.

- 2026-11-04: Added source-pinned schematic Allen Hall west exterior overlay and consolidated adjacent Anstett vegetation and prop draws; see docs/allen-west-exterior-refinement.md for sources, visual checks, collision caveats and remaining level-1 gaps.

- 2026-11-04: Added source-pinned Carson Hall schematic exterior, source-checked wall recolor and rebuild preservation; see docs/carson-exterior-refinement.md for evidence and level-1 limitations.

- 2026-11-04: Added source-pinned PLC tower facade and nearby planting batching; corrected Carson navigation test axes. See docs/plc-tower-refinement.md and docs/carson-exterior-refinement.md.

- 2026-11-04: Added source-pinned schematic museum west exterior and pointed-arch geometry, with nearby planting batching; see docs/museum-west-refinement.md for evidence and level-1 limitations.

- 2026-11-04: Added source-pinned Bean exterior study and wall recolor with nearby planting batching. See docs/bean-exterior-refinement.md for sources and level-1 limitations.

- 2026-11-04: Added source-pinned LLC North exterior study, wall recolor and guarded source-building mesh consolidation. See docs/llc-north-refinement.md for references and level-1 limits.

- 2026-11-04: Added source-pinned LLC South facade, wall color and guarded local roof reconstruction. See docs/llc-south-refinement.md for references and level-1 limits.

- 2026-11-04: Added source-pinned natural and cultural history museum exterior study and wall recolor. See docs/natural-museum-refinement.md for evidence and level-1 limits.

- 2026-11-04: Added source-pinned central power station exterior study and wall recolor. See docs/power-station-refinement.md for evidence and level-1 limits.

- 2026-11-04: Refined the reusable generic scooter and regenerated its prop export; see docs/scooter-detail-2026-11-04.md for evidence and level-1 limitations.

- 2026-11-04: Refined the generic bicycle and saved verified six-prop Blender snapshot; see docs/bicycle-drivetrain-2026-11-04.md.

- 2026-11-04: Refined nine illustrative pilot bench seats with source-pinned slats; see docs/pilot-bench-seats-2026-11-04.md.

- 2026-11-04: Refined reusable fern fronds at three existing sites; see docs/fern-arched-2026-11-04.md for evidence and limitations.

- 2026-11-04: Added reversible source-pinned color variation to the pilot canopy batches; see docs/pilot-canopy-tone-2026-11-04.md for scope and limitations.

- 2026-11-04: Added subtle cloud underside shading without changing cloud geometry; see docs/cloud-shading-2026-11-04.md.

- 2026-11-04: Added source-pinned Knight Law Center western exterior study and wall recolor. See docs/knight-law-refinement.md for evidence and level-1 limits.

- 2026-11-04: Added source-pinned Clinical Services roof slope study with rebuild protection; see docs/clinical-roof-refinement.md.

- 2026-11-04: Added source-pinned Cascade Hall wall color study. See docs/cascade-wall-study.md for evidence and level-1 limits.

- 2026-11-04: Added source-pinned Miller Theatre Complex western study and wall recolor. See docs/miller-west-study.md for evidence and level-1 limits.

- 2026-11-04: Added source-pinned thin overlay collision for the Miller west facade, with footprint-adjacency and route safeguards. See docs/miller-west-study.md.

- 2026-11-04: Added editable Blender snapshot and verified single-mesh GLB for the nine pilot bench detail overlays; see docs/pilot-bench-editable-overlay.md for source and exclusions.

- 2026-11-04: Added an illustrative source-pinned Ford Alumni Center north/east exterior study and route-screened collision; see docs/ford-alumni-study.md. Local only.

### 2026-11-04 — 科学建筑群足迹筛查（仅本地）

新增可复现的清单二维足迹筛查及 Huestis、Global Scholars 来源记录。Huestis 与现有 Willamette 候选足迹相交 746.09 平方米；63 个已命名候选中 13 个存在筛查重叠。此结果不是已证实的网格碰撞。Global Scholars 当前是矩形占位，而校方资料描述两个封闭庭院。本批未改变建筑、室内、碰撞、等级或线上版本；筛查对固定哈希的清单复现，详见 `docs/science-and-global-footprint-audit-2026-11-04.md`。

### 2026-11-04 — 低帧率导航有限补偿候选（仅本地）

线上浏览器失败轨迹与本地约每秒一帧的复现显示逐帧时间上限丢失了移动时间。本地候选将可见状态水平移动时间限制在每帧最多 0.25 秒，保留碰撞子步，并以移动时间判断步行与跑步。原有 6 米 / 15 秒测试不变。修正首次候选造成的移动端状态回归后，导航、低帧率及移动端浏览器测试 8 项通过；117 项单元测试、构建、格式及 viewer 哈希校验通过。渲染帧率低的根因仍未解决，GitHub 未运行该候选。详情与限制见 `docs/github-browser-regression-2026-11-04.md`。未推送或部署。

### 2026-11-04 — 通用道路车辆轮廓（仅本地）

对共用的轿车、SUV 和皮卡车身增加倾斜的车头和车尾轮廓，保持原有尺寸包络、位置和碰撞形状；面包车、自行车和滑板车几何未变。已重新导出 GLB 并更新哈希，六类模型的位置数组与程序源码一致。117 项原有单元测试及一项新增轮廓测试通过；5 项浏览器测试（含原绘制调用限制）、生产构建、格式和 106 项开放资产检查通过。保留旧 GLB；当前环境未找到 Blender，新版可编辑快照尚未生成，旧快照不含本次修改。详见 `docs/vehicle-profile-2026-11-04.md`。PROP-02 保持 1 级，未部署。

### 2026-11-04 — Jaqua 建筑外部（仅本地）

在 Jaqua 近似包络上增加可选择的四面玻璃和金属分格示意层，102 个构件合并为一个网格，并增加八段周边碰撞薄盒。保留地形、建筑源和室内；检查了建筑师参考及两个场景视角，119 项单元测试、14 项重建保留测试、构建、107 项开放资产和 viewer 哈希通过。浏览器批次覆盖选择、渲染模式、导航和原绘制调用预算。真实边界、屋顶、水景与尺寸未核实，等级保持 1；未找到 Blender，尚无新的可编辑 Blender 快照。详见 `docs/jaqua-exterior-2026-11-04.md`。未发布。

### 2026-11-04 — Knight Campus 2 东立面（仅本地）

在现有近似包络东侧添加受来源哈希保护的玻璃和竖向遮阳分格，合并为一个网格并附四段窄碰撞盒；保留选择和地形。现有包络长 85 米，短于校方公布的约 107.6 米；实际错位体量、其他立面、屋顶、连桥和周围环境仍待核实，等级保持 1。来源哈希、路线筛查、120 项单元测试、14 项重建保留测试、构建、108 项开放资产及浏览器选择、导航和原绘制预算检查通过。保留可编辑运行时 JSON，未生成新版 Blender 快照。见 `docs/knight-campus2-east-2026-11-04.md`。未部署。

### 2026-11-04 — Lillis 南侧入口（仅本地）

在近似最近屋顶匹配的 Lillis 候选南墙增加受来源哈希保护、可选择的示意玻璃入口与浅色门框，以及示意光伏板和一段周边碰撞盒；参考照片仅用于观察，未嵌入校徽或第三方几何。校园源、周边和室内不变。检查了七处模型墙面射线采样及同角度前后画面；121 项单元测试、14 项重建保留测试、构建、格式、109 项开放资产、源码哈希和 5 项浏览器选择、导航及预算测试通过。真实边界、几何和其他立面仍未核实，等级保持 1；可编辑运行时 JSON 尚无新版 Blender 快照。见 `docs/lillis-south-2026-11-04.md`。未发布。

### 2026-11-04 — 学生运动中心东立面（仅本地）

在运动中心近似候选的一段经采样倾斜东墙增加受来源哈希保护、可选择的示意玻璃立面，保留原几何、地形、植被和室内。初始独立网格候选达到 180 次绘制，未通过原有小于 180 的限制；最终使用现有受检查的源建筑网格合并。6 项浏览器测试覆盖源位置、颜色与法线、选择、导航和原绘制预算；122 项单元测试、14 项重建保留测试、构建、格式、110 项开放资产及 viewer 哈希通过；40 个当前细节层另做了元数据保留模拟。真实边界、入口和其他立面未核实，等级保持 1。旋转盒运行时 JSON 尚无独立 Blender/GLB 快照，现有仅支持无旋转盒的导出器不能直接忠实生成。详见 `docs/rec-east-2026-11-04.md`。未部署。

### 2026-11-04 — 支持旋转的外立面导出（仅本地）

新增可复用的运行时盒体立面 GLB 导出器，烘焙 XYZ 旋转并检查来源哈希、输入稳定性和禁止覆盖。为运动中心、Jaqua、Knight Campus 2 与 Lillis 生成新的独立叠加层 GLB，保留旧资产；四个落盘文件的位置、法线、颜色和单位变换均与运行时一致，三轴旋转合成测试及运动中心左右画面对比通过。原建筑与碰撞数据独立，新版逐对象 Blender 快照尚未生成；运行时及资产等级不变。见 `docs/rotated-exterior-export-2026-11-04.md`。未发布。

### 2026-11-04 — Knight Campus 1 南立面局部（仅本地）

在现有南侧包络约 61 米增加来源哈希保护的示意折叠玻璃图案，并在模型坐标中距未解决的无名相邻足迹至少约 4 米处停止。通过既有受检查的合并机制保留源网格，未移动建筑、地形、树木或室内。独立旋转叠加层 GLB 的 2,808 个顶点、法线、颜色与变换已独立比对；9 项浏览器、123 项单元、14 项保留测试、构建、格式、116 项开放资产及 viewer 哈希通过，41 个层通过元数据保留模拟。真实双体量、连桥、边界和剩余立面未解决，等级保持 1；尚无逐对象 Blender 快照。见 `docs/knight-campus1-south-2026-11-04.md`。未部署。

### 2026-11-04 - HEDCO 建筑外部（仅本地）

根据校方和建筑师资料，为现有近似建筑体量的两个外立面增加示意红砖与竖窗，并合并网格、增加六段经路径筛查的薄碰撞条。现有矩形和平屋顶并未还原实际庭院建筑群，窗列位置也未经测绘，等级保持 1。独立 GLB 仅包含新增外墙构件，其 6,984 个顶点的位置、法线和颜色与运行时一致；未生成新 Blender 快照。建筑主体、布局和室内保留。详见 `docs/hedco-exterior-2026-11-04.md`。未部署。

### 2026-11-04 - 蕨类有限形态变化（仅本地）

为三个现有示意蕨类簇使用的可复用叶片加入确定性的长度、高度及方向变化；位置、拓扑、原始 GLB 和合批方式不变。新独立单株 GLB 的 2,040 个顶点位置和法线与运行时一致并记录源码哈希。物种和位置尚未实测，等级保持 1，未生成新的 Blender 快照。计算中心近似轮廓与 Chiles 候选重叠，暂缓其立面细化。详见 `docs/fern-variation-2026-11-04.md`。未部署。

### 2026-11-04 - 共用估计入口组件（仅本地）

为原有两组实例化入口标记增加中缝和双侧把手，覆盖 534 个估计入口，不改变位置、推断、交互、碰撞或室内。每实例增加 60 个三角面，保持原有外接范围；局部第一人称视角测得 190 次绘制调用，既有固定视角预算测试另行验证。新双网格独立 GLB 记录源码哈希，不含放置数据，未生成 Blender 快照。入口不是测绘结果，PROP-04 保持 1 级；Pacific Hall 暂缓立面处理，等待候选模型可靠配准。详见 `docs/shared-entrance-portal-2026-11-04.md`。未部署。

### 2026-11-04 - 入口性能对照与云层导出（仅本地）

同视角比较显示入口改动前后均为 190 次绘制调用；通过平面细节将初版新增 32,040 个三角面降至 6,408 个，保留外观和两组实例化网格。既有固定视角预算测试保持不变。重新导出优化入口 GLB，保留旧版。另新增独立云层网格 GLB，与现有运行时几何及受控画面一致；它不包含天空穹顶、漂移和相机跟随，雾效与色调映射默认值需由使用方配置。未新增 Blender 快照或提升等级。详见 `docs/entrance-performance-2026-11-04.md` 和 `docs/cloud-standalone-2026-11-04.md`。未部署。

### 2026-11-04 - 外部轮廓筛查与灯具细节导出（仅本地）

将 63 个具名项目候选与 664 个俄勒冈州公开参考轮廓做二维筛查，仅保留重叠指标和编号。Pacific Hall 校方平面与州轮廓提示 Lawrence/Pacific 可能存在模型合并或误绑定；州数据部分编号重复且来源日期缺失，未直接改名或改几何。新增限定于盒体和柱体的可复用环境导出器，并为八处既有示意灯具的 40 个配件生成独立校验 GLB；原灯具主体未包含，场景画面不变。未生成 Blender 快照或提升等级。详见 `docs/oregon-footprint-screen-2026-11-04.md` 和 `docs/pilot-lamp-overlay-export-2026-11-04.md`。未部署。

### 2026-11-04 - 试点区铺装材质（仅本地）

为既有试点区铺装添加基于世界坐标的细微示意接缝，卡通和 PBR 模式均可见；不改变网格、路径、地形、建筑或室内。NAIP 仅提供有日期的硬铺区域背景，网格并非实测，ENV-05 保持 1 级。独立 GLB 与旧 Blender 文件不包含运行时着色器。同机位卡通画面前后均为 71 次绘制调用；逐像素开销未做设备性能基准。127 项 Node 测试、17 项 Python 测试、五项浏览器检查、构建、格式和哈希检查通过；仅元数据模拟保留了 42 个细节层及此补丁。详见 `docs/pilot-paving-joints-2026-11-04.md`。未部署。

### 2026-11-04 - 未放置的自行车架候选（仅本地）

参考 UO 公开尺寸制作原创参数化低多边形圆环车架，并生成源码哈希固定的三环独立 GLB。UO 地图 A27 表示 Tykeson 附近有遮蔽停车设施，但附近测试范围落在现有模型草坪上，且灌木与建筑配准尚不确定；未修改场景或放置车架。来源、范围与坐标检查见 `docs/bike-rack-candidate-2026-11-04.md`。128 项 Node 测试、17 项 Python 测试、四项浏览器检查、构建、格式和哈希检查通过。PROP-01 保持 1 级，未生成新 Blender 快照，未部署。


## 2026-11-04 — pilot lawn and bike rack screening

本地：为试点区现有草坪增加来源锁定的示意色调，支持 Toon 与 PBR，不改变几何和导航；ENV-05 保持 1 级。核对 UO F50、F20、A12 停车点与场景，因现有草地或建筑冲突暂不放置车架。证据、限制及独立导出缺口见 docs/pilot-lawn-tone-2026-11-04.md。


## 2026-11-04 — campus lawn extension

本地：将来源锁定的草坪色调扩展到现有顶点着色校园草坪，保留几何及原顶点色；ENV-04 和 ENV-05 仍为 1 级。相同视角前后均为 39 次绘制；来源、验证及仅运行时生效的导出限制见 docs/campus-lawn-extension-2026-11-04.md。未发布。


## 2026-11-04 — context tree trunks

本地：将 300 棵推断外围树木的方形树干替换为来源锁定的八边形几何，保留位置、树冠及导航；ENV-02 仍为 1 级。同视角绘制次数保持 39，三角形增加 1,200。来源、测试和仅运行时生效的导出限制见 docs/context-tree-trunks-2026-11-04.md；Esslinger 和 Chiles 因边界不确定未修改。未发布。


## 2026-11-04 — Unthank west facade

本地：为 Unthank 近似建筑西侧增加来源锁定的示意立面及独立叠加导出，保留现有轮廓与室内；等级仍为 1。三段西墙碰撞已检查导航边；近似轮廓、与 Bean 的重叠、其他立面和导出限制仍待核实。来源与验证见 docs/unthank-west-2026-11-04.md。未发布。


## 2026-11-04 — arena north facade

本地：为 Matthew Knight Arena 近似模型增加来源锁定的示意北侧幕墙及独立叠加导出；既有示意入口和模型导航保持不变，等级仍为 1。真实曲面和其他立面尚未核实；Yasui 南立面因模型几何与碰撞重叠暂缓。来源与导出限制见 docs/arena-north-2026-11-04.md。未发布。

验证：修正首版约 2 厘米入口偏移后，严格对比通过；132 项 JavaScript、19 项 Python、13 项浏览器测试以及构建、格式和 136 项资产哈希检查通过。仅元数据模拟保留 44 个外立面图层，未做完整 Blender 重建；仅本地。

最终 v3：视觉检查后分离入口附近重合面；严格入口对比及 13 项浏览器测试通过。重新验证 132 项 JavaScript 测试、构建、格式、viewer 哈希及 137 项资产；元数据模拟保留 44 个图层。仅本地。


## 2026-11-04 — context tree export and Hayward screening

本地：将现有 300 棵细化外围示意树导出为来源锁定的单网格 GLB，并核验几何及独立渲染；ENV-02 保持 1 级，逐树 Blender 源仍缺。Hayward 屋顶候选因原实心看台产生类似仓库的误导性外观而隔离，未改场景。详见 docs/context-trees-standalone-2026-11-04.md 和 docs/hayward-west-screen-2026-11-04.md。未发布。

验证：132 项 JavaScript、19 项 Python、5 项浏览器检查，以及构建、格式、viewer 哈希和 139 项资产检查通过；仅元数据模拟保留 44 个图层并确认 Hayward 候选未合入。未做完整 Blender 重建，仅本地。


## 2026-11-04 — shared planting material

本地：修复 40 丛试点示意灌木因树冠调色误改共享材质而显示全黑的问题；启用树冠顶点色前复制材质，灌木几何和树冠数值不变。ENV-03 保持 1 级。证据及导出影响见 docs/planting-shared-material-fix-2026-11-04.md。未发布。

验证：133 项 JavaScript 测试（含共享材质隔离）、19 项 Python 测试、6 项浏览器测试，以及构建、格式、viewer 哈希和 139 项资产检查通过；元数据模拟保留 44 个图层，未进行完整 Blender 重建。仅本地。


## 2026-11-04 — bounded pilot shrubs

本地：为两组共 40 丛既有示意灌木增加来源锁定的边界内形态变化，不扩大原有范围、不移动位置或改变树冠；导出并核对单网格 PBR GLB，ENV-03 仍为 1 级。来源、两处画面对照及 Blender/导出限制见 docs/pilot-shrub-variation-2026-11-04.md。未发布。

验证：133 项 JavaScript、20 项 Python、7 项浏览器测试及构建、格式、viewer 哈希和 141 项资产检查通过；元数据模拟保留灌木层及 44 个外立面图层，未进行完整 Blender 重建或设备性能测试。仅本地。

## 2026-11-04 - 隔离的林下灌木候选

核查 71 组既有低灌木，发现此前名称含 fern 的补丁还隐藏了其中三组。试制 64 组原范围内变化，但前景缩小后暴露尖锐底层叶片，整体效果不足，因此隔离候选、不接入场景。证据见 local-only research notes 和前后截图。资产维持 1 级，未生成独立导出；仅保留本地。
隔离后验证：构建、两项现有浏览器测试、20 项 Python 测试、viewer 哈希和 141 个归档资产检查通过。Vite 仍提示已有的大体积 chunk 警告。

## 2026-11-04 - 完整试点长椅导出

本地：将九张示意试点长椅的原始金属支架与细化木制座背合并为独立 GLB；运行场景与位置未变，PROP-01 保持 1 级。导出为校园坐标下的两个网格，并非九个可独立编辑对象。Cedar/Yasui 占位重叠仍未解决，未修改立面。来源、对照、溯源与限制见 docs/pilot-benches-complete-2026-11-04.md；未发布。

验证：133 项 JavaScript、20 项 Python、5 项浏览器测试、构建、格式、viewer 哈希、142 条资产记录及 1081 行清单检查通过。未做完整重建、Blender 快照或硬件性能测试；构建仍有既有大 chunk 提示。

## 2026-11-04 - Alder 暂定北立面

本地：为 Alder Building 地址附近的未命名 roof-ee63827c 候选增加 42 个示意立面及门廊构件；身份仍待核实，维持 1 级。未合批版本超出既有固定视角绘制预算；经校验的静态合批保留 179 次调用，测试点的原几何和选择行为保持一致。不修改室内、不发布。来源、画面对照、碰撞/入口测试和独立覆盖层限制见 docs/alder-north-provisional-2026-11-04.md。

验证：134 项 JavaScript、20 项 Python、3 项浏览器测试、构建及 45 个立面层的仅元数据保留通过；未做完整 Blender 重建或硬件基准。
补充验证：格式、viewer 哈希、144 条归档资产及 1081 行清单检查通过。

## 2026-11-04 - University–Villard 灌木合批

本地：合并两组兼容、来源固定且不可选择的灌木，建筑网格、布局和材质不变。1440 × 1000 初始全景由 179 降至 178 次绘制，三角形数不变；七组对照图逐像素一致。两个近景因剔除粒度变粗分别多绘制 640/320 个三角形，画面不变。全部 534 条入口记录及两栋建筑搜索选择保持一致；等级不变。证据和限制见 docs/shrub-batching-performance-2026-11-04.md。未发布。

验证：135 项 JavaScript、20 项 Python、3 项浏览器测试及构建通过；未做硬件帧时测试或完整重建。

## 2026-11-04 - 隔离的 Agate 立面研究

灌木合批验证通过后，依据校方调查、历史照片和归档航拍筛查可能的 Agate Hall 西立面；未命名 roof-b068940e 的身份仍属暂定。候选虽保持数值入口记录，却在相同场景视角遮住绿色入口标记，因此保持隔离、不加载；等级、碰撞和校园几何未变。首版超出原有合批范围保护，未修改该限制。详见 docs/agate-west-candidate-2026-11-04.md。仅本地。
Agate 隔离后补充检查：格式、viewer 哈希、145 条归档资产、1081 行清单和七组对照图哈希通过。
补充：能清楚看到 University 的标准材质对照也完全一致（共八组）；合批前后均可通过实际点击选择 University 与 Villard。

## 2026-11-04 - Agate 暂定西立面

更正：此前称 Agate v1 候选遮住入口标记，是视觉复核错误；原始截图的入口局部一致，射线也显示标记在前。v1 继续隔离。采用第二版 77 构件来源固定的西立面，填补入口周围棕色接缝，保留原估计入口与未确认身份，维持 1 级。立面合并至现有三建筑静态批次，并核验原几何与独立导出。来源、图像/射线证据、导航及限制见 docs/agate-west-provisional-2026-11-04.md。仅本地，不修改室内或发布。

验证：136 项 JavaScript、20 项 Python、4 项浏览器测试、构建及 46 个立面层的仅元数据保留通过；固定全景维持 178 次调用，阈值不变。未做硬件基准或完整 Blender 重建。
补充验证：格式、viewer 哈希、147 条归档资产、1081 行清单、六张图片哈希和五条入口射线记录通过。

## 2026-11-04 — Longhouse 区域暂定外部细化

- 对 Many Nations Longhouse 附近的未确认对象 `roof-f736712f` 添加 23 个南立面构件及受范围约束的配色。UO 参考资料、近似定位、前后画面及身份、屋顶和入口的证据缺口见 `docs/longhouse-south-provisional-2026-11-04.md`。对象仍为未确认、1 级；未改室内和位置。
- 配色先核对原模型和顶点颜色，仅更改 20,148 个批次顶点中的 92 个，保留原始 GLB 与 22 个对象身份。独立 828 顶点立面 GLB 的位置、法线及颜色往返误差为零，但不包含原建筑和运行时配色；未生成 Blender 快照。
- 138 个 JavaScript 测试、21 个 Python 测试、构建、格式、150 个归档资产与查看器哈希、1,081 条清单检查，以及真实 GLB 合并、入口点击/导航、Agate 和植被选择回归通过。三视角绘制调用前后均为 44/167/17；原总览预算检查为 178（<180）；534 条入口记录不变。先前临时测试重复注入已整合候选导致初始化失败，已修正为检查真实场景，阈值未变。没有执行设备帧耗时测试或完整 Blender 重建。修改仅在本地，未发布。

## 2026-11-04 — Lokey 教育楼候选墙面配色

- 使用现有源文件固定的配色流程，仅为近似候选 `roof-74ecc113` 的 120 个竖直墙顶点添加示意红砖色。校方资料、2013 年参考照片、多视角对比，以及身份、屋顶、入口和独立导出的限制见 `docs/lokey-wall-color-2026-11-04.md`。候选仍为 1 级；原 GLB、校园布局和室内未变，没有生成 Blender 快照或烘焙后的独立导出。
- 真实 GLB 浏览器检查确认其余位置、法线、索引、材质和对象身份不变，错误的预期数量会被拒绝。修改前后建筑选择、估计入口和 534 条入口记录一致；四视角绘制调用均为 28/89/23/67，既有总览预算测试为 178（<180）。138 项 JS、21 项 Python、3 项浏览器测试、构建、格式、查看器哈希及 151 个源/模型哈希检查通过。未进行硬件性能测试或完整 Blender 重建。仅本地保存，未发布。

## 2026-11-04 — 厢式车外形与 Onyx Bridge 候选核查

- 为现有通用厢式车增加下倾引擎盖，保持位置、碰撞、行驶路径和可见边界不变。重新导出六种道具 GLB 并保留前一版本；中性场景对比、校方车辆背景和新版 Blender 快照缺口见 `docs/van-profile-2026-11-04.md`。PROP-02 仍为 1 级。
- 校方历史调查将 Onyx Bridge 描述为带外露桁架的四层建筑，而现有近似屋顶候选仅 166 平方米、高 4.14 米。已在 `docs/onyx-candidate-screen-2026-11-04.md` 记录身份、尺度和附近候选距离的不确定性；未修改桁架、几何、身份或碰撞。
- 139 项 JS、21 项 Python、7 项针对性浏览器测试、构建、格式、查看器哈希及 152 个归档资产哈希检查通过。六种导出道具的位置与程序源一致，其他五种道具的位置、法线、颜色和变换与旧版一致；厢式车由 2,184 增至 2,196 个顶点。固定总览仍为 178 次绘制（<180）；未进行硬件帧耗时或校园场景内厢式车视觉验证。没有新 Blender 快照或部署；工作仅本地保存。

## 2026-11-04 — 外延树木树干变化

- 对 300 棵现有推断树木的树干增加源文件固定的第二层处理：顶端半径为既有底部的 78%，树皮颜色稳定变化不超过 ±6%。树冠各属性和索引、树木中心及高度、地形、布局和室内均未变。参考、限制及前后/PBR 画面见 `docs/context-trunk-variation-2026-11-04.md`；ENV-02 仍为 1 级。
- 新增不覆盖旧版的 300 棵树独立 GLB；位置、法线、颜色往返误差为零，索引一致。原独立 GLB 保留，其原浏览器测试仍通过。两个导出均为单一网格而非逐树 Blender 场景；没有新建 Blender 快照。仅元数据的重建保留检查验证了新层及其对原树干层的依赖。
- 139 项 JS、22 项 Python、6 项针对性浏览器测试通过，包括未更改的树冠保护、旧/新导出、选择和原 <180 总览预算（178）。对应近景前后均为 39 次绘制、749,989 个三角形；已检查 PBR。构建、格式、154 个资产哈希、查看器哈希及 1,081 条清单检查通过。未进行完整重建或硬件性能/峰值内存测试。修改仅在本地，未发布。

## 2026-11-04 — EMU 前场圆形铺装

- 在现有试点铺装着色器中添加有限范围的圆形错缝铺装。已归档的 2017 年 CC0 照片和 2024 年公有领域 NAIP 航片支持其大体外观与近似位置；具体砖块、尺寸、台阶及现状仍未核实。来源和 Toon/PBR 对照见 `docs/emu-radial-paving-2026-11-04.md`。ENV-05 仍为 1 级；未修改几何、校园布局或室内。
- 141 项 JS、22 项 Python 和 6 项浏览器测试通过，包括 534 条入口记录、模型碰撞、无关画面区域及导航检查。对应近景维持 71 次绘制、819,257 个三角形；固定总览为 178（<180）。构建、格式、155 项归档资产哈希、查看器哈希、1,081 条清单及仅元数据保留检查通过。独立 GLB 和 Blender 不含运行时着色器；没有新的烘焙导出、Blender 快照、完整重建或设备性能测试。仅本地保存，未发布。
- 另依据归档航片筛查远北背景地表：792 顶点的隔离修正候选在既有空间雾下几乎不可见，因此未合入或导出。

## 2026-11-04 — 圆润云层体积

- 将运行时现有 90 个云瓣改为低多边形圆润轮廓，保留各云瓣水平中心和底部高度，以及 18 组云的位置、运动、配色和材质。NWS 参考、校园与 PBR 对照、限制及可复现导出见 `docs/rounded-cloud-volumes-2026-11-04.md`；ENV-07 仍为 1 级。原天空生成器与旧独立云层导出保留。
- 新增 27,000 顶点独立云层 GLB，重导入的位置、法线及颜色误差为零；不含天空穹顶和动态行为，也未生成新 Blender 快照。两个对应校园视角分别维持 71 和 70 次绘制，各减少 18,000 个三角形。固定总览仍为 178（<180）；未做设备帧耗时或峰值内存测试。
- 143 项 JS、22 项 Python 和 7 项浏览器测试通过，覆盖新旧导出、减弱动态效果、导航和原预算；构建、格式、查看器哈希、156 项归档资产检查及 1,081 条清单检查通过。既有构建大块警告仍在。仅本地保存，未发布。
- 根据校方资料与 2024 航片筛查 Frohnmayer：现有命名的 505 平方米屋顶候选似乎只覆盖多翼建筑的一部分，限制见 `docs/frohnmayer-candidate-screen-2026-11-04.md`；未修改建筑几何、身份、碰撞或室内。

## 2026-11-04 - 可独立编辑的试点长椅导出

- 新增 `assets/exterior-refinement/pilot-benches-individual-2026-11-04.glb`，将九张长椅分别设为独立组，保留原金属支架与木件；导出过程校验源码及 18 个网格的世界坐标，旧合并导出保留。来源、对照及复现步骤见 `docs/pilot-benches-individual-2026-11-04.md`。PROP-01 保持 1 级；运行场景及校园布局未改变。没有新增 Blender 快照，单块木件仍合并。
- 筛查 UO 地图 A20 自行车停车区域：近似场景范围内 25 个采样点均落在模型草坪上，因此未放置通用车架；坐标误差和未核实事项已记录，不将其当作现场清点。
- 143 项 JavaScript 测试、生产构建及两项定向浏览器测试通过；几何对比完全一致，截图允许少量栅格差异（最大通道差 44）。构建原有大包警告仍在。仅本地保存，未发布。

## 2026-11-04 - 景观参考资料筛查

- 在 `docs/landscape-reference-screen-2026-11-04.md` 记录 Gerlinger Field Green 和 Science Walk 的 UO 原始资料。历史描述可支持后续调查，但不足以确定模型内单株树木的位置，或制作具有可靠坐标和许可的艺术铺装。科学区建筑重叠问题仍待解决。本轮未改变资产、运行场景、清单等级或发布状态；仅文档筛查，未新增运行时测试。

## 2026-11-04 - 草地细节候选筛查与清单核对

- 在两批既有草坪上试验近景程序化草纹，两项定向浏览器检查通过，包括原固定视角绘制预算及 Toon/PBR 材质加载；但视觉上仍像重复地面条纹，未达到采用标准。已恢复原 `src/lawn-tone.js`，候选代码和截图保存在项目外的任务工作区。本次筛查未改变运行时画面、几何或性能阈值。
- 更新 `docs/asset-refinement-inventory.csv` 的 PROP-01，补记此前完成的九张可独立分组长椅及单块木件、Blender 快照限制，等级维持 1。恢复运行时代码后，CSV 核对为 1,081 行，143 项 JavaScript 测试通过。仅本地保存，未发布。

## 2026-11-04 - 松鼠眼部细节

- 给既有通用松鼠增加两侧眼部细节并合并到共享网格，保留原身体几何、活动数量、路径、碰撞、建筑和室内；不宣称物种，LIFE-01 保持 1 级。俄勒冈州参考、CC0 来源、三视角对照、生成器和限制见 `docs/squirrel-eyes-2026-11-04.md`。
- 新增源码校验的独立 GLB，重导入的位置、法线和颜色一致；原 GLB 与 Blender 快照保留，没有新 Blender 快照。每只可见松鼠增加 160 个三角形，仍为单网格；未测量真实硬件帧时间。
- 143 项 JS 测试、构建、格式检查及两项定向浏览器检查通过，包括原固定视角绘制预算和默认 8 只松鼠；最终保护条件修改后复跑了松鼠测试和构建。清单核对为 1,081 行。原有构建大包警告仍在。仅本地保存，未发布。

## 2026-11-04 - University Hall 老虎窗与檐口

- 依据已存照片细化 University Hall 的老虎窗山花和侧框，并在四面及双塔檐口增加连续线脚和简化托架。保留原 210 个构件、先前规格、布局、室内和既有植被；来源、四张校园对照、隔离视图及未核实事项见 `docs/university-hall-refinement.md`。整体证据尚不足以认定与 Knight 相当，University Hall 保持 1 级，不自定等级标准。
- 新增含原四丛示意灌木的独立完整外部 GLB，位置、法线和颜色导出往返一致；原校园 GLB 和 Blender 快照未改，没有新的 Blender 快照或逐构件可编辑层级。隔离视角绘制次数维持 2 次，三角形由 10,004 增至 12,420；两组校园视角前后绘制次数一致，未测量真实硬件帧时间。
- 143 项 JS、22 项 Python 和三项相关浏览器测试通过；调整摄影机后复跑校园对照。原固定视角 <180 绘制预算、建筑选择、渲染模式、534 个入口记录和两点碰撞检查通过；生产构建及格式检查通过。首次 Python 测试路径和格式检查失败，修正后通过；原有大包警告仍在。清单保持 1,081 行，仅本地保存，未发布。

## 2026-11-04 - Villard 外立面檐口与塔顶栏饰

- 依据归档 CC0 照片和 UO 调查，细化 Villard 东立面圆窗拱饰、东及两端檐口托架、入口阳台侧栏与四角塔顶栏饰。原 206 个构件、校园布局、灌木、碰撞及室内不变。中央屋顶栏杆候选因画面衔接不可靠而未采用；西面与剧场连接及其他历史细节仍需核验。来源、匹配视图和限制见 `docs/villard-east-refinement.md`，Villard 保持 1 级。
- 新增含原八丛示意灌木的源码校验独立外部 GLB；位置、法线和颜色往返误差为零。原校园 GLB 和 Blender 源未改，没有新 Blender 快照、碰撞或逐构件编辑层级。隔离视角绘制次数保持 2 次，三角形从 6,948 增至 9,780；两组校园视角绘制次数不变，未测真实硬件帧时间。
- 143 项 JS、22 项 Python 和三项浏览器测试通过，包含选择、双渲染模式、原固定视角 <180 绘制预算、534 个入口记录及两处采样碰撞。构建及格式检查通过，原有大包警告仍在。清单保持 1,081 行，仅本地保存，未发布。

## 2026-11-04 - Johnson Hall 浅坡屋顶与檐口

- 在 Johnson 既有平屋面上增加有来源支撑的浅坡四坡屋顶，并为后侧与两端添加连续檐口和托架。原有三个屋顶标记被新屋面遮住，在相同水平坐标的较高处用简化构件表示；其真实身份尚未核实。保留旧后立面层、正面柱廊和铭文、建筑 ID、植被、室内及布局。UO 调查、2024 年公共领域航拍、2012 年 CC BY 4.0 照片、匹配画面和山墙加四坡屋顶仍不准确等限制见 `docs/johnson-rear-refinement.md`；Johnson 保持 1 级。
- 导出含既有示意灌木的源码校验屋顶/后立面叠加 GLB，不含原建筑、正面铭文、导航或碰撞；位置、法线和颜色往返误差为零，没有新 Blender 快照。隔离场景绘制次数保持 13 次，三角形从 8,480 增至 9,660；两组校园视角前后绘制次数一致，未测真实硬件帧时间。
- 143 项 JS、22 项 Python 和两项浏览器测试通过；原固定视角 <180 绘制预算、建筑选择、534 个入口记录和两处采样碰撞通过。构建及格式检查通过，原有大包警告仍在，清单保持 1,081 行。Friendly 山墙屋顶候选与既有老虎窗明显冲突，已留在项目外，未改变其运行时。仅本地保存，未发布。

## 2026-11-04 - Johnson Hall 山墙与四坡屋顶修正

- 依据 UO 历史调查所述屋顶类型及 2024 年航拍，替换上一轮截顶四坡屋顶为有中央屋脊和两端斜面的浅坡形式。两侧示意屋顶标记降低并旋转以贴合新坡面；水平中心、其余外立面、植被、碰撞和室内保持不变。来源、匹配画面及未核实细节见 `docs/johnson-rear-refinement.md`；Johnson 仍为 1 级。
- 新增带尺寸保护的可复用 `gable-hip` 几何及屋脊、坡面、标记接触射线测试。保留旧规格和生成器；新的源码校验叠加 GLB 位置、法线、颜色往返一致。原底模、旧叠加层和 Blender 快照保留；没有新 Blender 快照，叠加 GLB 不含完整建筑或碰撞。隔离视角绘制保持 13 次，三角形从 9,660 变为 9,652；两组校园视角绘制次数一致，未测硬件帧时间。
- 144 项 JS、22 项 Python 和两项浏览器测试通过；建筑选择、入口记录、采样碰撞和原固定视角 <180 预算通过，构建及格式检查通过。标记测试首次误设 0.10 米间距，修正为既有 0.12 米支撑厚度后通过。原有大包警告仍在，清单 1,081 行。仅本地保存，未发布。

### 2026-11-04 — Collier 北立面上层凸窗研究（本地）

参考链接中的 UO 照片，为 Collier House 增加两处上层梯形凸窗及示意阳台栏杆；保留建筑锚点、碰撞配置和室内。旧规格和生成器已保留，独立 GLB 的位置、法线与颜色往返一致；下层凸窗、门廊屋顶关系及现状尺寸仍需核实，建筑继续标为 1 级。同视角校园北/东画面绘制次数维持 60/93；选择、入口、碰撞采样、既有 toon/PBR 预算浏览器测试、145 项 JS 测试和生产构建通过。来源、画面及局限见 `docs/collier-house-refinement.md`。Friendly 屋顶与老虎窗候选经视觉检查后仍隔离。仅保存本地，未发布。

### 2026-11-04 — Collier 下层凸窗与中央门廊（本地）

依据参考照片增加与上层对齐的两处示意下层凸窗，将原整宽门廊收至中间并移除与凸窗冲突的外侧构件；保留建筑锚点、室内和保守碰撞矩形。比例、门廊结构与现状尚未实测，等级仍为 1。三个对应视角的绘制次数维持 60/60/93；建筑选择、入口、碰撞采样、既有 toon/PBR 预算、146 项 JS 测试及生产构建通过。独立 GLB 的位置、法线、颜色往返一致；尚无新版 Blender 快照。来源、对照图和限制见 `docs/collier-house-refinement.md`。仅保存本地，未发布。

### 2026-11-04 — University Hall 双塔细化研究（本地）

参考 UO 资料及许可明确的历史照片，将两端塔楼原示意单拱窗改成三联窄拱窗，并增加简化塔顶栏饰。保留建筑锚点、入口、周围场景、碰撞与室内，以及旧版规格。曼萨德屋面、烟囱、比例、入口通行及现状仍需更多证据，建筑继续标为 1 级。三个校园视角的绘制次数维持 80/36/26；建筑选择、入口记录、碰撞采样、原 toon/PBR 预算、147 项 JS 测试和生产构建通过。独立 GLB 的位置、法线、颜色往返一致，但不是新版 Blender 快照。详见 `docs/university-hall-refinement.md`。仅本地保存，未发布。

### 2026-11-04 — University Hall 曼萨德屋顶研究（本地）

将三处单坡屋顶近似替换为可复用的双坡曼萨德形态，并调整四组塔窗使其与坡面相交且保持可见。早期候选误改了入口构件，现已恢复，并通过逐对象回归验证最终范围。建筑锚点、入口、周围场景、室内和碰撞均保留。坡度、塔窗、烟囱及现状尚未测量，建筑继续标为 1 级。四个对应视角绘制次数维持 80/36/26/121；屋面与塔窗几何、选择、入口记录、碰撞采样、既有 toon/PBR 预算、149 项 JS 测试和生产构建通过。GLB 的位置、法线、颜色往返一致，尚无新版 Blender 快照。详见 `docs/university-hall-refinement.md`。仅本地保存，未发布。

### 2026-11-04 — Friendly 外挑檐口屋顶研究暂缓（本地）

将外挑檐口山墙与 17 个延长顶盖的候选和现有 Friendly 模型对照。UO 2025 调查与初步历史评估对屋顶类型的术语不同；候选远侧顶盖在高角度形成明显块状轮廓。候选、生成器和图片已保留以供审阅，运行时生成器已恢复，Friendly 锁定图层及 1 级状态不变。早期候选西、南视角绘制次数均为前后 77、34；东侧遮挡、北侧相机回退，因此不构成完整场景验证。来源和局限见 `docs/friendly-west-refinement.md`。未导出或发布。

### 2026-11-04 — Villard 屋顶轮廓研究（本地）

依据引用的 UO 调查和立面资料，将主体及四角塔顶共五处单坡屋面改为既有可复用的示意双坡轮廓；保留屋顶包围范围、其余构件、碰撞、入口、植被和室内，并保留旧版规格。西侧与剧院衔接、屋面曲线、精确尺寸和现状尚未核实，建筑继续标为 1 级。东、北、南对应视角绘制次数维持 27/133/21；尝试的西侧相机回退，不能算有效视觉检查。五处屋面几何、选择、入口、碰撞采样、原 toon/PBR 预算、150 项 JS 测试和生产构建通过。独立 GLB 的位置、法线、颜色往返一致，但不是新版 Blender 快照。详见 `docs/villard-east-refinement.md`；仅本地保存，未发布。

### 2026-11-04 — Villard 西侧相机与连接处排查（本地）

确认原西侧视点位于剧院碰撞范围内，触发现有返回逻辑回退；从无碰撞位置建立四个可复现的第一人称视角，并增加原坐标受阻及视点位置的浏览器回归。模型显示一条空隙，但 UO 2025 调查称剧院与建筑相连；2017 年提议连接图不足以证明翻修后的实际构造。等待现状影像或实测图前，保留几何、碰撞和 1 级状态。详见 `docs/villard-east-refinement.md`；仅本地保存，未发布。

另依据 2016 年评估和本地无碰撞视点排查 Chapman 北入口；前景几何遮挡视野，入口与模型的精确对应关系仍未确定，本轮未修改 Chapman 几何。详见 `docs/chapman-west-refinement.md`。

### 2026-11-04 — Susan Campbell 砖砌屋顶山墙研究（本地）

依据 UO 调查和许可明确的 2011 年照片，为长立面增加两处示意砖砌屋顶山墙，并调整相应既有窗框。已验证屋面相交和玻璃可见，其余构件、锚点、碰撞和室内保持不变，旧规格已保留。位置、比例、朝向、庭院入口与现状仍需核实，等级仍为 1。三个软件渲染视角绘制次数维持 87/58/45，部分受遮挡；选择、入口记录、碰撞采样、原 toon/PBR 预算、151 项 JS 测试和生产构建通过。仅含建筑的独立 GLB 位置、法线与颜色往返一致，尚无新版 Blender 快照。详见 `docs/susan-campbell-refinement.md`；仅本地保存，未发布。

### 2026-11-04 — 外部资产来源哈希对账（本地）

核对五座已细化建筑规格及共用外立面生成器的过期下游哈希：逐一确认旧建筑哈希与保留的旧快照一致，再核验当前场景与基础 GLB 锁定并更新记录；保留原来源记录，登记已校验的快照及新版 GLB，未修改场景几何。101 个追踪输出及 169 个归档资产的哈希均与记录一致，22 项 Python 测试通过；以源树数量 600 调用保留逻辑，47 个外部图层通过验证。首次直接探测遗漏重建统计，按预期被输入验证拒绝；补齐后通过。详见 `docs/exterior-source-pin-reconciliation-2026-11-04.md`。仅本地保存，未发布。

### 2026-11-04 — Susan 庭院入口研究（本地）

参考 UO 调查的庭院照片及近似场景映射，在内侧立面增加示意门廊、门和两个较小的保守柱体碰撞盒，并移除冲突的示意窗。精确位置、朝向及无障碍通行尚未核实；原位于南侧的估算互动入口标记未移动，新门不是已接通的互动入口，等级仍为 1。新增碰撞盒与现有导航边在 0.5 米缓冲下无交叉。三个软件渲染视角绘制次数保持 47/47/88；几何、柱体碰撞、选择、入口记录、既有 toon/PBR 预算、152 项 JS 测试与构建通过。仅建筑 GLB 的位置、法线和颜色往返一致；没有新版 Blender 快照。详见 `docs/susan-campbell-refinement.md`。仅本地保存，未发布。

### 2026-11-04 — Fenton 入口与栏杆连接（本地）

依据 UO 调查和州档案，修正东入口装饰拱与矩形门的层次，并连接原先悬空的屋顶栏杆和入口檐口。原建筑轮廓、植被、碰撞和室内不变。参考照片中的台阶因当前地形与门槛高程关系未核实而未建模；体量、尺寸、通行与现状仍有不确定性，等级保持 1。东、斜、南三个软件渲染视角绘制次数维持 54/77/36；几何、选择、入口记录、碰撞采样、原 toon/PBR 预算、153 项 JS 测试与生产构建通过。仅叠加层 GLB 的位置、法线和颜色往返一致，并非新版 Blender 快照。来源及输出哈希和旧记录已更新，详见 `docs/fenton-south-refinement.md`。仅本地保存，未发布。

## 2026-11-04 — Straub 西翼屋顶与顶层研究

参考所链接的 UO 调查，在已有来源锁定的西立面覆盖层添加近似西翼山墙屋顶与浅色顶层带；保留原建筑、既有覆盖几何及碰撞数据。检查三个地面视角与一个俯视视角；西侧与西北侧浏览器对比保留选择、入口数据、采样碰撞与绘制次数，既有草坪性能预算测试通过。导出独立追加式 GLB，重导入的位置、法线与颜色属性一致；来源和导出哈希已登记，保留修改前规格。屋顶确切形态与后翼衔接尚未核实，等级仍为 1，详见 `docs/straub-west-refinement.md`。未发布。

## 2026-11-04 — Fenton 东立面候选暂缓

对照 UO 调查记载的东侧两层原建筑与现有三排通用窗列，试验了隔离立面候选。候选仍露出原窗并产生檐口断裂，故未合入；两个浏览器视角分别保持 54 和 77 次绘制，这只是视觉筛查而非完整导航或性能验证。详见 `docs/fenton-south-refinement.md`；运行时资产和等级不变，仅本地保存，未发布。

## 2026-11-04 — Fenton 源网格过滤与 Anstett 朝向复核

在隔离浏览器实验中从 Fenton 网格移除 144 个索引三角形，两处视角维持 54/77 次绘制；端部立面仍不完整，候选缺少安全校验与交互回归，未合入运行时。另记录 UO 调查的 Anstett 西向入口描述与当前南向覆盖层之间的差异，没有移动入口。详见对应细化记录；未生成新 GLB 或 Blender 快照，仅本地保存，未发布。

## 2026-11-04 — Fenton 东立面受保护窗列修正

逐项验证 144 个待移除旧窗三角形及其 288 个源顶点签名后，合入来源锁定的东立面修正。运行时只克隆并过滤网格，保留其余索引、原 GLB 和建筑身份；来源哈希、几何或目标不匹配时在修改前拒绝。原檐口、入口和碰撞保持不变；转角旧窗及真实比例仍待核实，Fenton 仍为 1 级。浏览器前后对比保留选择、入口数据、采样碰撞和绘制次数，既有绘制预算与步行导航回归通过；构建、156 项 JS、23 项 Python 测试及格式检查通过。独立追加覆盖层导出属性往返一致，但不含基础网格或源三角形过滤；未生成新版 Blender 快照。详见 `docs/fenton-south-refinement.md`，仅本地保存，未发布。

## 2026-11-04 — Fenton 转角低窗及加载测量

依据历史照片，在两处现有斜向转角将最下层过大的通用窗替换为较小低窗；来源校验过滤范围由 144 扩至 168 个三角形。保留修改前规格、上层窗、屋顶、建筑身份、原 GLB 与碰撞。三个核对摄像机位置的前后视角、源文件篡改拒绝、绘制预算和步行导航回归通过，157 项 JS、23 项 Python 测试以及构建、格式检查通过。现有屋顶的替换边界证据不足，本轮未动。当前浏览器对 34.8 MB GLB 进行六次 SHA-256 的耗时为 22.0–23.4 毫秒；少量整体加载对照不能单独量化总开销。导出的追加覆盖层不含基础网格或源过滤，未生成 Blender 快照。Fenton 保持 1 级，详见 `docs/fenton-south-refinement.md`；仅本地保存，未发布。

## 2026-11-04 — University Hall 东西入口台阶

参考所链接的 UO 历史评估，为已有东西入口台阶增加示意实体混凝土翼墙与中央扶手。首版翼墙在斜视中悬空，修正为可复用楔形几何后合入；既有模型构件、屋顶、建筑位置、碰撞、导航和室内保持不变。三个核对摄像机位置的前后视角保留选中、入口记录、采样碰撞和绘制次数；原性能预算及步行导航回归通过。158 项 JS、23 项 Python 测试、构建与格式检查通过。独立替换模型往返校验通过，但不含地形、导航或碰撞，未生成新版 Blender 快照。尺寸与通行性仍待核实，等级仍为 1；详见 `docs/university-hall-refinement.md`。仅本地保存，未发布。

## 2026-11-04 — University Hall 入口台阶碰撞

为两端模型翼墙和中央扶手添加六个受限的全高二维碰撞框，保留修改前规格。按 0.42 米玩家半径模拟，两侧通道仍可通行；以 0.5 米余量筛查，现有导航边均未与碰撞框相交。浏览器前后对比保留全部入口记录及 Johnson 至 University 的 38 点路线，既有步行回归通过。真实台阶通行、垂直运动和无障碍仍未核实；独立 GLB 不含碰撞。等级保持 1，详见 `docs/university-hall-refinement.md`。仅本地保存，未发布。

## 2026-11-04 — Tykeson 上部立面

参考已归档照片与设计方项目资料，将既有来源锁定正面覆盖层调整为两排上部窗列，并调整玻璃立面比例；保留原入口雨棚、植被、基础占位模型、屋顶、碰撞、校园位置和室内。三个核对摄像机位置的视角维持 68/69/98 次绘制，俯视候选维持 82 次；选中、入口、采样碰撞、Toon/PBR 和原性能预算检查通过。追加式覆盖层往返校验通过，不含基础建筑、地形、导航或碰撞，未生成新版 Blender 快照。真实三部分体量及其他立面仍缺失或未核实，等级保持 1；160 项 JS、23 项 Python 测试及构建通过。详见 `docs/tykeson-north-refinement.md`，仅本地保存，未发布。

## 2026-11-04 — Gerlinger 东入口门廊

依据 UO 历史评估和已归档照片，在已定位的 Gerlinger 东立面增加示意柱式入口门廊，保留原覆盖层、门、上层窗、植被、屋顶、基础 GLB 和室内；弧形门廊顶部与真实标高仍待处理。三个核对摄像机位置的视角保留选中、入口数据、采样碰撞及 62/43/101 次绘制，南侧视角受遮挡；几何测试确认门玻璃可见且檐部低于上窗。原 Toon/PBR 绘制预算通过。追加式 GLB 往返校验通过，但不含基础建筑、地形或碰撞，未生成 Blender 快照；新柱仅为视觉几何，不保证通行。等级保持 1，详见 `docs/gerlinger-east-refinement.md`。本地待发布审查。

## 2026-11-04 - 路灯叠加资产生成器哈希更新

共享生成器变更后重新导出既有路灯叠加层，保留旧文件，并验证 3,840 个顶点的位置、法线、颜色及场景合并和材质一致性。运行时几何未变，PROP-01 仍为 1 级。详见 `docs/pilot-lamp-overlay-export-2026-11-04.md`。

## 2026-11-04 - Johnson 后立面上层窗与横带

依据既有历史照片，为后立面增加示意性中央上层窗、遮阳篷及横带。两个视角保持 56/71 次绘制、选择、入口和采样碰撞；独立叠加 GLB 的位置、法线和颜色重导一致。保留旧源码，未修改室内或碰撞；尺寸及现状未实测，仍为 1 级。详见 `docs/johnson-rear-refinement.md`，仅本地保存。

## 2026-11-04 - 固定人物原型（本地）

在 Deschutes 附近加入有来源标注的风格化人物原型，包括经过碰撞采样的短路径与端点停顿、地图标记、轻量交互标签、接近台词和含资料链接的人物卡。复用骨骼角色并程序化制作格纹与配饰；用户给出的台词为游戏脚本，外貌尺寸未经测量。详见 `docs/fixed-person-dan-carrere.md` 与预览图。仅本地保存，等待用户审核，暂停上线。

## 2026-11-04 - 固定人物建筑遮挡（本地）

为人物标签和气泡增加限频的两点建筑遮挡判断，未改变已审核人物外观。真实场景中的桌面和触控遮挡／无遮挡视角、人物卡、路径、178 次绘制预算及低帧率回归通过；局部遮挡为近似处理，尚未检查树木。详见 `docs/fixed-person-dan-carrere.md`。仅本地保存，等待气泡参考图核对。

## 2026-11-04 - 固定人物对话气泡参考

按用户提供且由母线程目视核对的参考调整为白色圆角气泡、柔和阴影和左下尾巴；放在人物右上方并避开姓名。参考图未再分发，已审核的人物外观不变。详见 `docs/fixed-person-dan-carrere.md`，上线验证待完成。

## 2026-11-04 - 六视角测试夹具效率

CI 模式完整浏览器回归中 168 项通过，Gerlinger、Tykeson 和 University Hall 的六视角比较各触发原 90 秒超时；原始用例独立复测有两项复现。每项比较复用一个浏览器上下文、两版各用新页面并清理本地存储及 Cookie，全部镜头、截图、断言和 90 秒限制保持不变。三项隔离 CI 复测通过；失败轨迹保留在本地任务工作区，上线前重跑完整回归。

## 2026-11-05 - 固定人物悬浮卡（本地）

人物资料卡改为人物旁的非模态悬浮卡，依据可用空间左右或下方避让并限制在视口内。卡片打开时人物路径仍暂停；玩家或相机移动时卡片跟随，人物离开视野或被遮挡时关闭。保留 Escape、关闭、焦点恢复、模型和标签点击及触控，台词与资料不变。本地验证：164 项单元测试、生产构建、格式检查、4 项人物桌面／触控与遮挡浏览器测试和 5 项现有建筑卡浏览器测试通过。未重跑完整浏览器套件；此前 Linux CI 超时仍未解决。已获用户授权准备发布。

## 2026-11-05 - 总览缩放和角色移动速度（本地）

将建筑与固定人物标签上的总览滚轮事件转发给现有轨道控制，避免平移后标签移到鼠标下方吞掉缩放。键盘默认速度改为原奔跑速度 4.6 米/秒，Shift 奔跑为 9.2 米/秒；触控摇杆仍为连续速度，上限 9.2 米/秒，步行动画阈值同步更新。室内共用移动逻辑。验证通过：165 项单元测试、生产构建、格式检查、平移前后桌面滚轮边界及标签滚轮、平移后触屏捏合、4 项移动端控制、5 项建筑卡，以及每秒一帧奔跑测试。两项人物卡测试两次失败；使用 HEAD 版本的本次改动运行时模块对照时，在相同断言处失败，人物卡问题仍待解决；没有重跑完整浏览器测试及 Linux CI。HEAD 原有 wildlife.js 模板锁哈希不一致，本次未修改。仅隔离分支本地修改，未发布。


## 2026-11-05 - 触屏缩放边界与人物卡排查（本地）

扩展浏览器回归，使用真实双指手势分别在平移前后到达原有的轨道距离 12 和 6000；桌面和触屏两项测试通过。两项已有固定人物测试使用 HEAD 版本的本次修改运行时模块仍可复现：人物行走使标签移动，Playwright 在悬停可暂停人物之前等待目标稳定；手机卡片打开时先处于 (0, 0)，下一次画面更新才定位到人物旁（50 毫秒时观察到）。这些问题尚未解决；没有修改人物行为或测试断言。43 个模板锁文件中，本次三个修改文件的覆盖哈希和上游锁均匹配；仅 wildlife.js 不匹配，其实际哈希与 HEAD 一致且未登记覆盖项。未推送或部署。

## 2026-11-10 - 松鼠近景细节及人物卡首帧定位（本地）

为既有 CC0 衍生通用松鼠增加原创炭色鼻尖和克制的胸部／毛色顶点色。源几何、轮廓、布置、路线和原 GLB 均不变；细化后仍为一个绘制对象、1,060 个三角形，并释放合并用临时几何。新增独立 GLB 经重新导入核验，3,180 个位置、法线和颜色值误差均为零；旧导出保留。限制与前后图见 `docs/squirrel-eyes-2026-11-04.md`，LIFE-01 保持一级。

人物卡打开后立即同步计算人物旁的锚点，消除先出现在左上角再下一帧定位的闪现；后续更新复用同一计算。新增桌面／手机同一任务内即时断言，原实现 0/2，修复后 2/2；相关人物卡与遮挡浏览器回归共 6/6 通过。既有移动目标测试先聚焦标签暂停行走，再真实点击，未删减交互断言。

目前验证：169 项 JS 单元测试、23 项 Python 单元测试、生产构建、语义活动、校园扩展和地表校验通过；松鼠校园批处理浏览器回归通过。恢复既有天空归档的 LF 工作副本字节后，189 个源／模型文件校验通过（无 Git 内容变更）。明确登记此前漏记的 wildlife 下游覆盖，未改变上游模板锁。全目录格式检查使用自动行尾通过；默认检查仍报告既有 Windows CRLF 工作副本差异，未批量改动无关文件。保留既有声音大包警告。未运行完整浏览器套件或 Linux CI，未推送／部署；剩余额度不可见。

## 2026-11-10 - Knight 图书馆实心阳台轮廓（本地）

依据已归档 CC-BY-4.0 照片，为北立面三个阳台增加实心石栏板、侧回墙、压顶和渐收底部。源哈希固定附加层含 21 件并合为一个网格。原建筑 GLB、轮廓、窗户、入口与碰撞不变。前后浏览器测试通过：绘制调用 42→43，采样碰撞与入口不变，无页面错误。图像和限制见 `docs/knight-refinement.md`：尺寸、雕刻和当前状况未核实，此为单视角验收。Knight 保持二级。未推送／部署。

## 2026-11-10 - 集成复验与归档字节保护（本地）

14 项选择性浏览器集成测试全部通过：建筑卡 5 项、Overview 平移缩放 2 项、低渲染频率奔跑 1 项、人物打开／交互／遮挡 6 项。使用 direct-node Vite 和唯一严格端口，避免误测其他工作副本；没有放宽浏览器或运行时断言。缺失信息警告由通过的容错测试主动模拟。本结果替代此前网络中断的局部导航测试，不代表完整浏览器套件或 Linux CI。为已有校验值的天空历史 JS 归档增加精确的 `-text` Git 属性，防止 Windows 检出转换其字节；归档内容和哈希未改变。未推送／部署。

## 2026-11-10 - Knight 高窗深度与可复用分层导出（本地）

增加七扇高窗的来源支持砖石窗侧／顶壁，独立源哈希固定图层，42 件合为一个网格；保留玻璃开口、空白学科牌和完成的阳台。这是围绕现有窗面向外增加厚度的解释性造型，并非实测窗洞；Knight 保持二级。正／斜角前后浏览器检查增加实际人物坐标与朝向断言，防止被拒视点回落到默认出生点后产生伪验收。纠正后的两视角均通过，采样碰撞／入口不变，无页面错误，绘制调用分别 44→45、41→42。保留既有树木遮挡。见 `docs/knight-refinement.md`。

阳台和窗洞层各导出为独立可复用 GLB，记录来源／生成器哈希与真实生成时间。重新导入位置、法线、颜色误差均为零，本地与浏览器构造一致，材质和身份亦通过。导出器只接受两个固定 Knight 图层、显式 localhost 端口及新文件；不包含原建筑、碰撞或 Blender 场景。保留原证据，可分享核验记录移除工作站路径。见 `docs/knight-standalone-export-2026-11-10.md`。

本轮最终检查：173/173 项 JS 单元测试、生产构建、自动行尾格式检查及 191 个归档源／模型校验通过。另有上文 14/14 集成浏览器回归及 Knight 专项视图通过；未运行完整浏览器套件或 Linux CI。既有几何与证据保留。未提交、推送或部署。

## 2026-11-10 - Gerlinger 砖饰、Johnson 柱头及证据纠正（本地）

Gerlinger 东立面新增 36 块中央交错浅砖饰和 15 件克制窗冠，保留窗洞和遮阳棚。目视发现悬空的外角候选后已剔除，保留部分按实际源网格定位。正／斜检查入口与采样碰撞不变，绘制调用 64→65、44→45。Johnson 北面六柱增加十二个原创简化涡卷，保留牌文与原柱体；2,832 三角形图层正／斜验证为 81→82、86→87。两者保持一级，独立 GLB 和属性零误差重导入证据已保存，见各自日期文档。整体场景预算另行检查：全量诊断随后测得 182 次绘制，超过既有 <180 阈值，正在实现严格验证的图层合批，不抬高阈值。

Johnson 扶手审查纠正此前候选前提：实际生成器和 GLB 已有两道扶手，不能再无依据增成四道，因此没有改扶手。库存补充证据但未改变状态／等级，总数核对为 1,082 行，包含后来新增的固定人物。另将本地登记的 Knight 阳台 output digest 改为原始 JSON 精确字节哈希，而非 LF 归一化值；源 JSON、presentation pin 与导出本来一致，均未改变。

Windows autocrlf 改变了未修改的自行车架、天空和随机模板生成器工作字节，导致精确导出来源检查失败。GLB 内嵌哈希与 Git HEAD／LF 源字节一致。只恢复这些规范 LF 字节并增加精确文件属性保护，没有改变几何、导出校验值或断言。稳定浏览器复验待完成。未推送／部署。

## 2026-11-10 - Tykeson 雨棚、键盘访问及绘制预算恢复（本地）

将 Tykeson 两块既有雨棚板细化为框肋／玻璃色分格，并增加避开窗洞的上部竖向板缝。原 52 对象 JSON 完整保存，其余 50 件完全不变。两个实际视点均保持 71 次绘制、入口和碰撞不变，新独立 GLB 重导入零误差。玻璃色材质仍不透明、间距为推断、隐藏体量未解决，均如实记录；保持一级。

建筑卡打开／切换时同步定位；桌面／手机同任务即时回归在旧实现失败、修复后通过。键盘 Enter／Space 可原生激活标签与按钮，不再被全局移动快捷键吞掉；键盘打开卡片接收焦点，关闭安全恢复，pointer 打开不抢焦点，Tab 不被非模态卡片困住。10 项相关浏览器测试通过，并通过加强后的键盘进入测试。

不删几何、不抬阈值，恢复整体绘制预算：三对固定来源同建筑图层仅在 JSON 精确哈希、生成几何、静态变换、材质和唯一资源所有权全部验证后合批。位置／法线／颜色与射线命中身份保留，植被和独立导出保留。实测优化前 182、后 179，既有 toon／PBR <180 测试通过。合法历史配置 pin 不参与新合批，仍独立显示；当前支持 pin 下的损坏则事务性拒绝。历史前后测试保留所有非绘制字段的精确断言，只允许绘制减少或相等，而非强迫冗余工作。

Git 属性固定规范源行尾，Windows 下严格 viewer 哈希和默认格式检查通过；三个原本以 CRLF 保存的历史导出器作为精确字节例外保留。旧生成 receipt 原始字节哈希未改，见 `docs/source-byte-normalization-2026-11-10.md`。全量套件仍为诊断，须在稳定版本复验变化／HMR 导致的失败后才能结论。未提交、推送或部署。

## 2026-11-10 - 冻结版本当前浏览器套件验收完成（本地）

当前 144 文件中的 186 项浏览器测试全部通过：稳定主批 182/182，另补四项固定人物测试，零跳过、零 flaky。两个稳定批次之间源码／场景／测试的原始 SHA-256 全树均无变化。这是同一冻结状态的两批完整覆盖，不冒称单次 186 项调用。此前非冻结诊断的 163 通过／14 失败报告原样保留，14 项均在上述修复与稳定复验后通过。真实时间与报告哈希见 `docs/browser-validation-2026-11-10.json`。

配套检查通过：183 项 JS 单测、23 项 Python 测试、生产构建、默认格式检查、全部 43 项 viewer 基线／覆盖原始哈希、登记输出与 195 个源／模型文件校验。保留既有声音大包警告。Windows Chrome／SwiftShader 验收不等同 Linux CI、真实移动 GPU 性能或线上部署验证；隔离导出测试人为移除 DOM 后的 console 警告保留在原日志。未提交、推送或部署。后续 Susan Campbell 来源支持候选仍是计划，不是已完成几何。

## 2026-11-10：后续本地细化批次（进行中）

在上一批冻结代码通过 186 项浏览器测试后，继续获授权的 UO 细化。Susan Campbell 两个有历史照片支持的小拱形细节正在加入现有合并层，并保留完整修改前规格。已更新本地来源哈希，视觉、导出和回归验收仍待完成。此前验收仅适用于上一检查点，不自动覆盖新几何。未提交、推送或部署。

### Susan／人物控件本地结果（集成复测前）

- Susan：原有 463 个构件全部保留，按归档 2011 年照片增加两个浅拱饰的 8 个部件，保留原始规格快照，仍为 1 级。真实相机正面／斜角对照通过，draw calls 为 81→81 / 79→79，入口与碰撞不变。独立 GLB 642704 字节，SHA-256 `40b507d808bab0d438e7481b572a0f03631a409fa68bb7e882c08b27efaffb25`；17808 个位置／法线／颜色属性回读误差为零。初始被树干遮挡的正面证据已替换为无遮挡的局部立面近景，不声称完整建筑视图。不确定的凸窗暂缓。
- 人物控件：标签／关闭按钮按空格原先错误触发角色跳跃。两项新增测试在修复前失败；小范围保留按钮原生空格激活并阻止传播至移动后，8 项相关浏览器测试通过，Enter／Escape 仍受验证。
- 本地生产构建及标准格式检查通过，冻结定向集成回归正在运行；此前完整测试记录独立保留。未提交、推送、部署。

### Susan／人物批次验收

冻结后的定向浏览器回归 **27/27 通过**，无失败／跳过／不稳定用例，耗时约 4.7 分钟；源码、浏览器测试与场景前后哈希一致。全局 draw calls 维持 **179（小于 180）**，错误来源哈希的负向测试仍有效。当前全部 JS 单测 **186/186**、Python **23/23** 通过，构建、格式、viewer 哈希及 **197** 项归档资源记录验证通过。见 `docs/browser-validation-2026-11-10-round2.json`。此次定向复测补充而非替代上一批 186 项完整浏览器记录。仅本地未提交。

## 2026-11-10：Friendly Hall 圆柱批次（进行中）

在 Susan／人物控件验收检查点之后，四根照片明确支持的独立门廊柱仅从方柱改为现有八边形圆柱。所有位置、尺寸、材质及另外 486 个对象保留，原规格与嵌套来源记录已保存。已更新本地来源哈希，最终视觉、导出及回归验证尚待完成。未提交、推送、部署。

### Friendly 批次验收及有依据的收口

语义上仅修改四根柱的 shape；另外 486 个对象、尺寸、材质、位置、碰撞和导航完全不变。新规格序列化为 LF，同时完整保留原始字节快照，因此 Git 文本差异比语义改动大。建筑仅增加 80 个三角形，不增加 draw calls。三处真实相机对照通过；独立 building-only GLB（796100 字节；`cc96fee2b2bf1564a3deb81335557cb1a3e9e9d87bc955fc5f862e1ea2f4311a`）的 22068 组位置／法线／颜色属性回读精确一致。导出 stdout 凭证后补记录真实记录时间，不虚构未知导出时间。

最终冻结定向浏览器回归 **7/7 通过**，零失败／跳过／不稳定用例，源码、测试和场景哈希未变；固定场景预算仍为 **179**。见 `docs/browser-validation-2026-11-10-round3.json`。全部 **187 项 JS 单测**、构建、标准格式检查通过；**43** 项模板／覆盖原始哈希及 **199** 项归档资源记录均验证通过。未改动的 Python 范围已在上一批通过 23/23。

限定复核 University Hall、Villard Hall、Gerlinger Annex 后，没有可靠的新小改动：可见饰件多已实现，剩余屋顶映射需要更好证据，Annex 照片已有建筑身份警告。见 `docs/refinement-candidate-audit-2026-11-10-c-stop.md`。本批据此收口，不编造几何或无意义消耗额度。无法读取剩余额度。全部改动仍为本地未提交，未推送、部署或宣称新 upstream pin。

## 2026-11-10：继续资料与交互质量复核（进行中）

几何检查点后，按持续工作要求检索新的公开来源，不重复耗尽的旧照片候选，并复现实际交互缺陷。照片归档 README 数量陈旧：已按原始字节核验全部 23 条 manifest 记录，双语数量修正为 15 个照片文件、2 个航片子集、5 个设计图和 1 个纹理。保留文件不全是当前有效建筑参考，Gerlinger Annex 既有身份警告继续明确保留。未新增或改许可图片。新复现的人物标签鼠标／键盘焦点冲突正在限定范围修复与验证。未发布。

### 新来源 Annex 与人物焦点结果（集成待完成）

- 重新查证 UO 官方调查，并独立查看照片楼牌与方位图，确认现代 Annex 北面，与误标的既有 Commons 图区分。官方图片未核实开放图片许可，仅保留链接，不新增源图片或纹理。5 条深 0.03 米的浅槽是基于现有模块的风格化解释，不宣称实测缝数／间距。仅重分上部面板，另外 83 个对象、立面包络、碰撞和入口记录不变，实际射线验证 0.03 米槽深。环境／斜视／近景 draw calls 39/38/36 均不增加，未移动或隐藏树木。
- Annex 导出 179300 字节，SHA `9572877db1ce9a010e09f87eddb953926bd38faaf4bcb782ba7bd30776ed7bf8`；建筑 2700、植被 2208 个顶点的位置／法线／颜色回读精确一致。保留原 stdout，未知导出时间保持 null。
- 复现人物标签鼠标离开误清键盘焦点状态（修复前 0/1）。分离模型悬停、标签悬停及焦点后，10/10 相关浏览器检查通过，包括反向 blur、隐藏／销毁清理及不抢其他输入焦点。
- 全部 189 项 JS 单测、构建及标准格式检查通过。冻结 16 项集成回归正在运行，未发布。

### Annex／人物批次验收

冻结集成 **16/16 通过**，144.9 秒，无失败／跳过／不稳定用例，runtime／scene／browser 测试哈希无漂移。全局 draw calls 仍 **179**；Annex 环境／斜视／近景维持 **39/38/36**。当前 189 项 JS 单测、构建／格式、43 项 viewer／模板原始记录、201 项资源注册记录及 23 项参考图片归档记录均验证通过。见 `docs/browser-validation-2026-11-10-round4.json`。仅本地未提交；此检查点后继续独立来源研究。

## 2026-11-10：Chapman 西面浅浮雕批次（进行中）

独立复核确认西入口凸出部缺少照片可见的浅拱节奏，其他立面既有饰件不在此次范围内，限定 10 米范围，用原有生成器并完整保留 144 个对象。使用 UO 官方资料仅链接参考；新低清照片为 attribution-only，不在固定归档白名单内，聚焦检索的 CC／公有领域替代均为其他大学同名楼。未伪标许可、放宽 CI 或公开入库照片。本地来源哈希已更新，视觉／导出／回归待验。固定参考资料检查器的现有 23 项记录通过，语义活动、校园身份和地表检查亦通过。

### Chapman 与原生按钮结果（集成待完成）

Chapman 原有 144 个对象完整保留，新增 121 个部件，形成连续浅石带和 12 个深 4 厘米的拱形浮雕。首版独立拱看似悬挂马蹄，已拒绝，未因测试通过就接受。等价旋转规约至现有校验范围，未放宽校验；近景／斜视相机也已修正，真正显示檐带。最终三视角局部 draw calls 109/44/41 均不变。原 144 对象测试改为精确保留前缀与明确新增数，并非宽松不等式。

独立 overlay GLB 为 419904 字节，SHA `90ebcc700a8809c30242066f3f8877344f53c6e7cf8d56e726e7c5c704d5573d`，建筑 10872、灌木 720 个顶点，位置／法线／颜色回读误差零。原 stdout 保留，未知生成时间保持 null。

再复现一个真实键盘缺陷：Follow 和 Settings 按钮把空格当成世界跳跃（修复前 0/2）。全局键处理仅对原生按钮目标的 Space 返回，保留原生激活；viewport 空格仍跳，鼠标点 Follow 后 W 仍走。8 项本地相关测试通过。upstream 基线未变，本地覆盖已明确记录哈希。冻结 15 项集成回归正在运行。未提交／推送／部署。

### Chapman／原生按钮批次验收

冻结集成 **15/15 通过**，132.5 秒，无失败／跳过／不稳定用例，源码／场景／浏览器测试哈希未变。Chapman 视角预算 **109/44/41** 不变，全局 **179**。原生按钮激活、viewport 跳跃、W 移动、人物／建筑键盘操作以及 overview 滚轮／捏合／慢帧回归通过。当前 **191 项 JS 单测**、构建／格式、43 项 viewer 原始哈希、203 项开放资源记录及全部 23 项参考图片记录通过。见 `docs/browser-validation-2026-11-10-round5.json`。此次补充既有完整／定向记录，不宣称再次全量浏览器测试。未提交、推送或部署。

## 发布收口，2026-11-10T22:09:23.045485+00:00

用户要求结束当前批次、记录、推送部署后停止。未再启动实现。最新 Carson 候选明确保持未实现；搜索／触屏只读复核 6/6 通过，无代码改动。额外合批候选因语义桶不兼容或已有合批而否决，没有安全新增收益。

从现有 main 基线 `8cbb19b71268090c086a8ec2eb25ed8476137fb3` 发布已本地验证的 11 月 10 日完整批次。刚 fetch 确认与 origin/main 无 ahead/behind 分歧。使用已有 GitHub Pages 流程，不改变凭证、权限或托管设置。发布 commit 及实际 workflow／部署结果由此记录之后的 GitHub 记录，不在这里预先宣称成功。此前 local/pending 描述为历史。发布验证后不再继续细化。
