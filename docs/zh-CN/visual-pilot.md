[English](../visual-pilot.md) | **简体中文**

# Knight Library—EMU—Johnson Hall 首个视觉闭环

v0.6 · Architectural Toon Realism · 2026-10-31

本页保留首版历史报告。当前 [v0.7 细化](visual-refinement-v0.7.md)采用开放许可图库、模块化地标和航拍引导景观；本页原截图与来源不覆盖。

本版加入 3 个照片参考地标、10 栋程序化历史建筑和 1 个未辨识背景体块，220 棵针叶／阔叶树、草坪、步道、绿篱、长椅和路灯。采用暖日光、偏冷环境光、三阶 Toon 明暗、深色窗格与浅色石饰。本版未加入全屏描边或 AO 后处理。

![试点区域](../images/visual-pilot-overview.png)

## 照片与精度

已上网搜索并查看 UO 官方照片。[参考登记表](../../data/metadata/visual-pilot-references.json)记录页面、图片 URL、采用的特征与限制。参考照片不随仓库分发，也没有用于贴图。

**素材归档更新：**[统一图片目录](../../data/reference-images/README.zh-CN.md)现保存 7 张另行取得开放许可的照片及已有项目图稿，供接下来细化。上述 UO 官方照片仍为未确认分发权的历史链接引用，明确排除并记录替代素材 ID。建图库没有重新生成本版几何；拍摄日期、修缮前后和立面朝向均登记供后续准确使用。

- Knight Library：高窗、红砖、浅色石饰／檐口、三个小阳台。[UO 图片页面](https://cas.uoregon.edu/about/cas-awards/recent-cas-awardees)
- Johnson Hall：六柱门廊、砖石对比、宽台阶与圆形种植意象。[UO 图片页面](https://news.uoregon.edu/content/uo-sets-record-academic-giving-first-public-year-campaign)
- EMU：高低砖体块、高窗、底层玻璃、雨棚、露台和 Fishbowl 弧形玻璃意象。[UO 图片页面](https://news.uoregon.edu/content/events-emus-75th-birthday-bring-uo-groups-together)、[历史资料](https://emu.uoregon.edu/index.php/about/history)

这是近似美术模型，并非测量立面或当前精确数字孪生。窗户数量、体块分段、尺寸、比例和现代 EMU 仍待进一步核验。其余建筑在历史轮廓／高度包络上添加通用窗格；`roof-39f81f68` 仍未辨识，不因换材质获得建筑身份。

树木、草坪、新增路径和设施是策划的示意布置，不是树木清单、通行测绘、修缮现状或路线建议。地形、底层 GLB、manifest、稳定 ID、2008 年资料来源和 Census 道路保持原值。新增地表贴合原地形三角面，并排除原有建筑／道路。

## 交互与局限

[在线地图](https://williamq96.github.io/open-campus-uo/)默认展示试点区域，可缩小看完整 2 × 2 km 场景。搜索三个地标可 45° 拉近。三种视角、原 T 字路口出生点、面向 EMU、WASD、Shift、Space、拖动、Follow 滚轮、搜索、选中标签、小地图均保留。出生点至 EMU 入口方向保留植被视线。

Settings → Architectural toon 可切换三阶明暗与 GLB 标准 PBR 材质，线框／阴影／标签设置正常。步行模式只显示附近一般标签，选中目标不受距离限制。行走碰撞仍用已有建筑 footprint，相机射线使用显示模型；装饰台阶、树木、长椅、露台尚未生成新的可行走碰撞体。无室内、季节天气、LOD／流式加载或移动端走路控制。

## 源资产与重建

[Blender 源文件](../../assets/visual-pilot/knight-emu-johnson.blend)、[GLB](../../apps/web-preview/public/scene/visual-pilot.glb)、[presentation 记录](../../apps/web-preview/public/scene/presentation.json)、[美术配置](../../configs/visual-pilot.json)均已提交。Blender 中按建筑／景观语义拆分，可编辑材质。GLB 保留标准 PBR、ID 和署名，三阶明暗在浏览器层实现。

从仓库根目录，先准备上游环境与 Blender：

```powershell
& '../open-geospatial-to-3d-reconstruction-pipeline/.venv/Scripts/python.exe' scripts/prepare-visual-pilot.py
& '../open-geospatial-to-3d-reconstruction-pipeline/.tools/blender-4.5.15-windows-x64/blender.exe' --background --factory-startup --python scripts/build-visual-pilot.py
```

底层地理重建与美术层分离。底图更新后须核验记录的 manifest／heightfield hash 与替换 ID，再接入美术层。脚本会重新生成其负责的源文件，后续手工细化必须先保存独立版本。

## 验证与成本

新增标准材质 GLB 约 7.9 MB，无照片贴图、CDN 或外部运行服务。场景按建筑／材质与景观族组织。1440 × 960 初次诊断在三模式测得 43–124 draw calls。`scripts/review-visual-pilot.mjs` 保存截图及每模式 60 帧样本到忽略的 artifacts 目录。

诊断使用 Chrome 155／ANGLE SwiftShader 软件渲染，帧间隔中位数约 158–175 ms，不代表硬件 GPU 表现。完整地形仍整体绘制，地形分块／LOD、植被细节层次与更多设备验证仍待进行，不承诺 60 FPS 或移动端性能。

自动测试覆盖原地形、碰撞、跳跃、三视角、出生朝向、缩放、搜索／标签、窄屏、标准材质回退、线框和 About；上游另有多 primitive 材质选择、目录安全和脚手架复制测试。代码 Apache-2.0，原创模型／截图按 [CC BY 4.0](../../LICENSING.zh-CN.md)署名，照片保持原权利。通用实现放上游，UO 地理与美术资料留在下游。
