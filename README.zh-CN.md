[English](README.md) | **简体中文**

# Open Campus: UO

以 Blender 为核心、可跨引擎复用的 UO 主 Eugene 校园三维资产与 Three.js 交互预览项目。

**[在线运行](https://opencampus-uo-williamq96.fluffy-chub-9311.chatgpt.site)**：免登录。上下游仓库现均为 public。

## 当前版本

2 × 2 km 校园及周边，534 个占位体块、63 个命名建筑、140 段基础道路／路径。主要依据 2008 年 NOAA/DOGAMI 点云，辅以 17 个明确标记的近似体块；道路使用 Census 2025 TIGER/Line® 中心线、估算路宽。该白模不等于当前精确校园测绘或产权边界。

出生点在 University Street / East 13th Avenue T 字路口，面向 EMU。Settings / About 集中说明来源、质量、项目链接和署名。

## 本地运行

```powershell
cd apps/web-preview
npm ci
npm run dev
```

打开 `http://127.0.0.1:5173/`，无需先安装 Blender 或下载原始点云。

| 操作 | 控制 |
| --- | --- |
| 移动／跑步／跳跃 | WASD 或方向键／Shift／Space |
| Follow／第一人称／Overview | 1／2／3，V 循环 |
| 看向／缩放 | 鼠标拖动；Follow 和 Overview 中滚轮缩放 |
| 搜索 | 左上角或 /，支持名称、EMU／PLC 等缩写 |
| 选择／关闭／清除 | 方向键和 Enter／Esc 或清除按钮 |
| 重置／显示选项 | Return to start／Settings / About |

Overview 搜索以约 45° 拉近展示；步行视角原地转向并高亮，切换模式保留目标。移动／拖动交还手动控制。窄屏支持查看和搜索，尚无触屏移动摇杆。

## 长期分工与模板

[上游 Pipeline](https://github.com/williamQ96/open-geospatial-to-3d-reconstruction-pipeline) 维护通用方法、自动化、验证和浏览器模板；本仓库维护 UO 来源、模型、身份、品牌和细化内容。

`pipeline.lock.json` 固定重建版本；`apps/web-preview/viewer-template.lock.json` 单独固定共享代码。品牌／说明放在 `public/viewer-profile.json`，场景放在 `public/scene/`。模板升级先核查代码 hash，保留项目数据与部署身份。见[模板说明](docs/zh-CN/viewer-template.md)。

## 重建和验证

在与 `pipeline.lock.json` 一致且干净的 upstream checkout 中准备 Python 和 Blender，然后运行 `./scripts/rebuild.ps1 -PipelineRoot <路径> -Blender <blender.exe>`。默认主校园配置，旧 Memorial Quad 场景作为首个闭环证据保留。

在浏览器应用目录运行 `npm test`、`npm run build`、`npm run test:browser`。本地 Chrome，CI Playwright Chromium；字体与场景自托管。历史来源、坐标、精度与版本检查见[验证记录](docs/zh-CN/verification.md)。

## 协议与署名

代码／模板代码 **Apache-2.0**，原创文档和原创模型／设计贡献 **CC BY 4.0**；保留署名、NOTICE 与适用第三方条款，见[协议说明](LICENSING.zh-CN.md)。不纳入 UO 内部 GIS、OSM／Microsoft 等汇编轮廓或 Google 3D 作为本版核心资产来源。

[历史 README](docs/zh-CN/README-pre-template.md)保留此前版本的完整背景。
