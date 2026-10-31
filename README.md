# Open Campus: UO

以 Blender 为核心、可跨引擎复用的 University of Oregon（Eugene）校园三维资产库与浏览器预览项目。

**状态：v0.4 增加建筑搜索与三种视角的定位行为，出生点改为 EMU 旁的 T 字路口。保留主校区 2 × 2 km 场景、基础道路、Follow 缩放与全英文 UI。仓库为 private。**

当前默认配置为 `configs/eugene-main-campus.json`；旧 Memorial Quad 配置与 Blender 场景作为首个闭环记录保留。当前改动、来源与限制详见 [v0.2 主校区说明](docs/v0.2-main-campus.md)。

新增功能、道路来源与验证见 [v0.3 道路与镜头说明](docs/v0.3-roads-controls.md)。

出生点与搜索行为见 [v0.4 搜索与定位说明](docs/v0.4-building-search.md)。

## 长期定位

[Pipeline](https://github.com/williamQ96/open-geospatial-to-3d-reconstruction-pipeline) 是长期维护的 upstream source，升级方法论、自动化、验证和通用能力。本仓库是长期维护的 downstream，重点升级 UO 的具体建筑、几何、材质与校园细节。详见 [维护与升级约定](MAINTENANCE.md)。

## 立即预览

在线操作：[OpenCampus: UO](https://opencampus-uo-williamq96.fluffy-chub-9311.chatgpt.site)。站点为 owner-private，使用发布者的 ChatGPT 账号登录；GitHub 两个仓库保持 private。支持完整搜索、角色移动、跳跃与三种视角，无需启动本地服务器。发布记录与维护方式见 [在线发布](docs/hosting.md)。

仓库包含浏览器所需 GLB、地形高度场及清单，无需先安装 Blender 或下载源点云。字体随应用打包，运行预览不依赖外部字体服务。

```powershell
cd apps/web-preview
npm ci
npm run dev
```

打开 `http://127.0.0.1:5173/`。这是本地预览，没有公开部署。

| 操作 | 控制 |
| --- | --- |
| 移动 / 加速 | WASD 或方向键 / Shift |
| 调整视角 | 按住鼠标拖动；鸟瞰可滚轮缩放 |
| 跟随镜头远近 | Follow 模式滚轮缩放，2.5–30 m；建筑避障优先 |
| 建筑搜索 | 左上搜索框或 /；支持名称与 EMU、PLC 等缩写；方向键、Enter 选择，Esc 关闭／清除 |
| 跟随 / 第一人称 / 鸟瞰 | 1 / 2 / 3，或顶部按钮 |
| 循环切换视角 | V |
| 跳跃 | Space；落地后可再次起跳 |
| 线框 / 名称标签 / 阴影 | Settings / About |
| 复位 | Return to start |
| 查看建筑候选 | 点击白模体块 |

角色沿真实地形移动，受建筑轮廓和试验区边界碰撞约束。当前漫游面向桌面键鼠；窄屏可查看场景，尚无触屏移动摇杆。

## 首个闭环记录（v0.1）

- 360 × 360 m 试验区，中心 `[-123.0777, 44.0444]`；比最初约 300 m 建议多留一圈边界。
- NOAA/DOGAMI **2008-08-31** 点云：裁剪 1,016,116 个点，其中 216,517 个地面点。
- 2 m 地形网格、27 个启发式建筑占位体块、白模角色与三种视角。
- [Blender 源场景](assets/memorial-quad/memorial-quad.blend)、[浏览器清单](apps/web-preview/public/scene/manifest.json)、[来源核验](data/metadata/source-audit.json)。
- 数据代表历史条件；候选轮廓可能混入树冠或遗漏建筑，尚无独立测量控制点。

## 重新生成

在 upstream 建立其 README 所述 Python 环境和 Blender，然后在本仓库运行：

```powershell
./scripts/rebuild.ps1 -PipelineRoot 'D:/github/open-geospatial-to-3d-reconstruction-pipeline' `
  -Blender 'C:/path/to/blender.exe'
```

`pipeline.lock.json` 固定已验收 upstream commit。脚本核验版本、源数据 SHA-256，调用通用工具并更新 Blender 与浏览器产物。开发可用 `-AllowUnpinned`，产物会记录实际 commit 和 dirty 状态。

在 `apps/web-preview` 执行 `npm test`、`npm run build`、`npm run test:browser` 可验证本版。本地浏览器测试使用已有 Chrome；CI 使用 Playwright Chromium。详见 [验证记录](docs/verification.md)。

## 两个仓库的分工

| 仓库 | 负责内容 |
| --- | --- |
| [Open Geospatial-to-3D Reconstruction Pipeline](https://github.com/williamQ96/open-geospatial-to-3d-reconstruction-pipeline) | 可迁移到其他地区的点云、地形、影像处理，Blender 生成与导出，元数据约定和验证工具 |
| [Open Campus: UO](https://github.com/williamQ96/open-campus-uo)（本仓库） | UO 区域配置、数据来源记录、校园 Blender 资产、场景与瓦片清单、Three.js 下游预览 |

通用算法放在 Pipeline 仓库。本仓库保存校园实例及其内容，通过固定版本的流水线生成资产；不复制一份独立的重建实现。

## 目标闭环

```text
经核验的地理数据 + 自采照片
  → 通用重建流水线
  → 可编辑 Blender 资产库
  → GLB/glTF + 地理元数据 + 场景清单
  → Three.js / Godot / Unity / Unreal
```

`.blend` 保存可编辑源资产；GLB/glTF 是优先交换格式。Three.js 只消费导出物。游戏引擎中的交互、碰撞配置和导航由各自适配层负责。

## 第一个里程碑

已用 360 × 360 米试验区完成地形、独立白模对象、Blender/GLB 导出和浏览器检查。下一阶段核对候选轮廓，建立稳定建筑身份，再逐栋细化。实际 AOI 与原点见配置和场景清单。

## 数据与发布约束

- 按后续对话决定，排除 UO 内部 GIS，不以申请校方数据作为前置条件。
- 本版已核验并使用 NOAA 托管的 DOGAMI OLC 点云。USGS 查询命中的 2021 DEM 在试验区全为 NoData，已排除；NAIP 与自采照片尚未使用。
- 第一版不纳入 OSM、Microsoft Building Footprints、Oregon 汇编建筑轮廓、Eugene City GIS 或 Google Maps/Earth 3D 作为核心资产来源。
- 仓库当前保持 private。GitHub Pages 是未来可选部署目标，目前没有启用、发布网站或上传资产。
- 代码与资产的许可证尚未选定；项目名称中的 “Open” 不代表已授权公开分发。

## 项目文档

- [架构与资产约定](docs/architecture.md)
- [首个闭环与后续路线](docs/roadmap.md)
- [原始讨论与最终决策](docs/source-discussion.md)
- [数据目录说明](data/README.md)

规划来自 [UO校园三维建模技术 — 分享对话](https://chatgpt.com/share/6ae54fb0-e6cc-83e8-8958-51a084c6b7cb?ogimg=plain)，已于 2026-10-30 读取完整的五轮讨论。
