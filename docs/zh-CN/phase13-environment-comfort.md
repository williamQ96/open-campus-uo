# 本地迭代 13：环境、晃动与重启

> 已随 Open Campus: UO 0.12.0 发布。下文保留原本地准备／测量语境，部署确认见开发日志。


[English](../phase13-environment-comfort.md) | **简体中文**

本批接续[迭代 12](phase12-npc-beta.md)，最初在本地验证，现随 0.12.0 发布；旧验证记录保留原状态。

## 交互

- 蓝色渐变天空与 18 组原创柔边方块云；云合并为一个网格，无图片下载、无云阴影。系统减少动态效果时停止云漂移。
- Settings 的 **First-person motion** 改成 **No / Low / Mid / High**，默认 Low。垂直／侧向幅度上限分别为 0／0、3／1、6／2、10.5／3.5 毫米，无滚转。滑块只影响第一视角视觉偏移，不改变步行速度、脚步声或骨骼共用的真实位移相位；系统减少动态效果优先将晃动置零。
- 步行学生遇到碰撞先让行，约 0.5–0.74 秒后尝试侧移、绕过、回到固定路径。整段限定于内缩后的人行铺装，避开建筑和当前碰撞体。每帧最多一个角色请求规划，失败后间隔 1.1 秒重试。空间不足继续等待，不借用车道／绿地；其他种类仍沿原生境固定路线并碰撞让行。
- 僵尸接触会结束本轮：检查高度并只触发一次，暂停场景，在标签和 UI 下方盖 **30% 黑色遮罩**，中央出现 **You are dead** 与 **Restart**。Restart 重新载入页面，回到面向 EMU 的原 T 字路口、Overview、Mid 密度、Low 晃动、默认声音、Beta 关闭、开发者模式关闭。Escape 不能跳过死亡窗口。正常退出 Beta 仍恢复此前密度。
- 保留三视角、搜索、导航、小地图、密度、反馈、桌面和手机移动／转向／跑步。

## 地面与资料

归档新增 **2024-06-08 USDA NAIP 航拍正射图**，覆盖完整 2 × 2 公里场景，并非实时卫星地图。[来源记录](../../data/metadata/naip-2024-main-campus-reference.json)保存两幅源图、EPSG:3740 范围、导出参数和下载字节哈希；[原图](../../data/reference-images/aerial/naip-2024-main-campus-rgb.png)、[台账](../../data/reference-images/manifest.json)、[署名](../../data/reference-images/ATTRIBUTION.md)保留独立公共领域属性。用户提供的 Google 截图只说明关注区域，不描摹、不导入、不作为开放资产分发。

平滑航拍的大范围颜色线索，以小型原创调色板生成校园草地、背景绿地、暖色校园混凝土、冷色城市混凝土、沥青、水面色块；推断建筑周边铺装和背景硬地。它们不是精确地表、植被、产权、停车或通行调查。现有道路和精细人行铺装保持原地理布局，新层填补底部空白；原树木位置不变。GLB 不嵌照片像素或照片纹理。

新增独立可编辑源 `assets/landcover/eugene-ground.blend`，运行文件 `public/scene/landcover.glb` **9,630,380 字节**，一个网格、160,801 顶点、320,000 三角面。完全跟随原 401 × 401 高程网格，只加 0.018 米美术偏移；原地形保留用于检查和物理，不重复绘制，从而避免共面闪烁。道路／精细铺装在其上方。原创世界坐标程序颗粒用于 PBR 和 Toon，导出文件保留顶点色与粗糙度，不依赖浏览器自定义 shader 才能使用。

534 个建筑身份、源坐标、历史高程、先前校园／屋顶 Blender 源均保留。地表推断与上一批屋顶升级分离，不把 2008 地理基础改称当前实测。

在项目根目录依次执行 `scripts/prepare-landcover.py`（上游 Python 环境）、`scripts/build-landcover.py`（Blender 4.5 LTS）和 `scripts/check-landcover.py`。完整命令见英文版。生成会更新 presentation；资产字节改变后应核验并更新资产哈希台账。人行铺装改变时重生成 semantic activity，`pedestrian_regions` 是内缩、排除障碍的绕行范围，不替换导航图。

实际结果见[验证记录](../../data/metadata/phase13-verification.json)、[开发日志](../../DEVELOPMENT_LOG.zh-CN.md)及[地面](../images/phase13-ground.png)、[天空](../images/phase13-sky.png)、[死亡窗口](../images/phase13-death.png)截图。通用代码与方法在上游维护，校园资产／图源／开发日志只在下游。没有宣称真实手机 FPS。
