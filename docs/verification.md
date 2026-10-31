# v0.1 闭环验证

日期：2026-10-30（America/Los_Angeles）。当前检查针对 Memorial Quad 首个历史白模，不代表完整校园或独立测量精度。

## 数据证据

`data/metadata/source-audit.json` 记录实际输入、原始 LAS CRS、瓦片覆盖与校验和。选中 NOAA/DOGAMI 瓦片共 11,436,019 个点，裁剪试验区后 1,016,116 个点，含 216,517 个地面点。2021 年 USGS DEM 虽命中目录边界，但实际 AOI 129,600 个采样像元全部 NoData，已拒绝。

## 重建与导出

- 实际运行 Python → Blender **4.5.15 LTS** 后台进程，生成 `.blend` 和 GLB。
- 地形：181 × 181 顶点，2 m 间隔；原地面网格占有率 73.38%，边缘 732 个顶点用最近邻补足。
- 2,161 个地面网格留出检查：RMSE **0.107 m**，P95 绝对误差 **0.165 m**。这是内部插值一致性，不是绝对地理精度。
- 27 个建筑候选。它们是历史点云启发式占位，尚未人工逐栋确认，庭院等细节未建模。
- 导出检查 GLB 2.0 头部、长度及地形/建筑节点；场景清单按 upstream schema v1 验证。

## 自动检查

| 检查 | 结果与范围 |
| --- | --- |
| upstream Python unittest | 5 项：非对称斜坡坐标、空数据拒绝、屋顶/多回波区分、损坏缓存拒绝、非法输入路径拒绝 |
| downstream Node tests | 4 项：ENU/glTF 采样转换、非共面地形三角面一致性、边界/半径碰撞与高速防穿透、贴墙滑动及地面跟随 |
| Playwright browser | 2 项集成测试：真实 GLB 加载、GLB 射线与 heightfield 高度一致、角色移动、三种视角、鼠标转向、复位/线框/来源、窄屏控制和失焦停止移动 |
| Vite production build | 通过；引擎 JavaScript 主包约 650 kB 未 gzip，后续按需要拆分 |

浏览器集成检查使用 Chrome headless + SwiftShader 软件 WebGL，验证功能，不用它报告目标设备的 FPS。桌面预览默认使用浏览器可用 GPU。测试阻止所有外部 HTTP 请求，场景和字体均由本地应用提供。字体依赖通过 Fontsource 固定，OFL 许可副本保留在 `apps/web-preview/public/licenses/`。

CI 固定 Ubuntu 24.04，避免 `ubuntu-latest` 升至 Playwright 1.60 不支持的 Ubuntu 26；失败时保存浏览器 trace。CPU 较弱的 CI 允许较长的浏览器用例超时，不跳过功能断言。

截图保存在本地 `artifacts/overview.png`、`third-person.png`、`first-person.png` 与 `mobile.png`。源代码中保留可复跑的测试；CI 只验证，不部署站点。

## 仍未验证

独立测量控制点、当前校园变化、每栋候选的身份和语义准确性、跨引擎导入、触屏移动、完整校园流式加载与独立性能基准。
