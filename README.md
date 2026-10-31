# Open Campus: UO

以 Blender 为核心、可跨引擎复用的 University of Oregon（Eugene）校园三维资产库与浏览器预览项目。

**状态：v0.1 首个真实数据闭环已完成。Memorial Quad 历史白模、Blender 源场景与 Three.js 探索器已生成。仓库为 private。**

## 长期定位

[Pipeline](https://github.com/williamQ96/open-geospatial-to-3d-reconstruction-pipeline) 是长期维护的 upstream source，升级方法论、自动化、验证和通用能力。本仓库是长期维护的 downstream，重点升级 UO 的具体建筑、几何、材质与校园细节。详见 [维护与升级约定](MAINTENANCE.md)。

## 立即预览

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
| 跟随 / 第一人称 / 鸟瞰 | 1 / 2 / 3，或顶部按钮 |
| 循环切换视角 | V |
| 线框 / 复位 | 右上角按钮 |
| 查看建筑候选 | 点击白模体块 |

角色沿真实地形移动，受建筑轮廓和试验区边界碰撞约束。当前漫游面向桌面键鼠；窄屏可查看场景，尚无触屏移动摇杆。

## 本次真实产物

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
