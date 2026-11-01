发布批次 0.13.0；实际部署核验见 DEVELOPMENT_LOG.zh-CN.md。

[English](../interiors-mobile.md) | **简体中文**

# Iteration 15：拖拽调速与通用教室

本地待发布，未 push／部署，线上 0.12.0 的模型溯源不变。通用代码和方法回流到本地上游 [方法文档](https://github.com/williamQ96/open-geospatial-to-3d-reconstruction-pipeline/blob/main/docs/interiors-mobile.md)。

- 手机 Follow／First person 下半屏拖拽幅度连续控制 0–4.6 m/s，6 px 死区、48 px 满幅；轻拖行走，满拖跑步，取消独立 Run 按钮。上半屏转向、双指独立、取消／抬手停止及电脑 Shift 跑步保留。
- 534 个建筑记录均有原创绿金门框；534 个推断接近点均通过现有建筑轮廓碰撞检查。这不表示真实入口、无障碍条件或路径连通已核实。后续可在 viewer-settings.json 的 entrances 按建筑 ID 覆盖 ENU 门位与外法向角。
- 三模式可点击／触摸可见门进入；第一／第三人称靠近后可按 E 或 Enter 按钮。室内门边 E、点击门或 Return to campus 返回室外。
- 共用原创 24 × 18 m 教室，15 套桌椅、黑板、讲台、窗、天花板和出口；有家具／墙面碰撞、三视角、走跑／跳跃、现有角色／声音／舒适度。Overview 隐藏天花板。每栋当前用同一个推断模板，不是真实 UO 平面图或用途断言。
- 动态入口模块与整页切换保持单一活动世界：室内不请求校园／地面 GLB、室外导航／活动图，也不生成校园 NPC。pagehide 显式释放 GPU 资源，BFCache 恢复时重建；共享角色、字体、代码与音频允许 HTTP 缓存。未来按稳定 ID 替换更细室内，无须让所有房间常驻。
- 同标签 session 记录恢复室外位置、人物朝向、视角／俯仰／Follow 距离、Overview 构图、密度、晃动、显示与声音设置；无效／禁用存储回到普通出生点。导航、选择、NPC 轨迹、开发者与 beta 回合重新开始。
- 可编辑源代码 classroom.js 为 Apache-2.0，原创 classroom-v1.glb 为 CC BY 4.0（162,700 字节）。资产说明在 assets/interiors/README.md，哈希已登记。无新增照片或第三方模型／纹理。

实际验证与发布状态见 DEVELOPMENT_LOG.zh-CN.md 和 data/metadata/phase15-verification.json；保留旧模型与图片溯源。上游运行时未提交时，viewer lock 如实记录 dirty=true。


## Iteration 16：Overview 卡片／观察式进入／悬停（本地待发布）

Overview 点模型、标签或搜索结果，显示唯一的建筑锚定卡片：顶部名称，中间精确占位 `to be fill`，底部 Enter，另有关闭按钮。打开时只隐藏该建筑标签，关闭或切回人物视角后恢复。卡片随投影移动，手机横竖屏不越界，其余标签继续原有避让。

Overview 的 Enter 使用 interior_mode=overview，以观察者打开教室，**不创建室内 hero、不请求 hero 模型**；实际 hero 留在已保存的室外位置。可旋转／平移／缩放教室，返回后恢复室外位置和构图。该观察访问省略人物视角；Follow／First-person 的门口进入仍有 hero 和三视角。沿用 iteration15 单一活动世界。URL 显式记录模式，因此存储禁用时仍可观察进入；原位置恢复仍按既有 session 降级规则。

鼠标悬停给独立建筑轻微 emissive 提亮，不改变选择；选中效果优先。材质合批的背景建筑只增加该栋源轮廓边缘提示，保持合批，不让整批发亮。拾取按稳定 ID 解析并容忍边界误差；每 80 ms 最多处理一次待拾取鼠标位置，拖动／弹窗跳过，离开清除，触摸不产生 hover。不降低质量、不重建模型。共享代码／设计在本地母 repo，校园日志和证据仍只在下游。
