# 架构与资产约定

## 仓库边界

本仓库是通用重建流水线的 UO 实例，负责区域、来源台账、校园内容与预览。通用算法及交换约定由 [Pipeline 仓库](https://github.com/williamQ96/open-geospatial-to-3d-reconstruction-pipeline)维护。

已通过 `pipeline.lock.json` 固定 upstream commit/version，通过 `scripts/rebuild.ps1` 调用独立 checkout，不使用 Git submodule。产物记录实际 commit、dirty 状态、配置 hash、来源校验和与处理参数。

## 当前目录与后续扩展

`configs/`、`data/metadata/`、`assets/memorial-quad/`、`exports/` 和 `apps/web-preview/` 已存在。精细化建筑库与校园分区属于后续扩展。

```text
configs/                    # AOI、地理坐标原点、Pipeline 版本
data/metadata/              # 具体数据集来源、许可依据、日期和校验和
assets/                     # 按持久资产 ID 管理的 Blender 源文件与材质
scenes/                     # 引用独立资产的校园主场景和分区
exports/                    # 本地生成的 GLB、元数据和瓦片，默认不入 Git
apps/web-preview/           # 计划使用 Three.js + Vite
```

## 地理与资产规则

- 工作单位为米，Blender 局部坐标采用 East/North/Up。
- 每个区域记录水平 CRS、垂直基准、单位与局部原点；原点应来自实际数据，不能使用假坐标占位后当作真实配准。
- 建筑使用独立且持久的 ID；没有校方 GIS ID 时由项目生成，不能依赖 Blender 对象名称作为身份。
- 原始资产与 Blockout、Detailed、Optimized 版本建立关联，后续可以逐栋替换。
- 保留来源、采集日期、处理版本、授权状态与实测误差。目标误差与实测结果分别记录。
- PBR 材质以可交换表示为目标；程序材质按需烘焙。碰撞代理独立于高精度显示 Mesh。
- GLB 的轴约定与 Blender 局部坐标不同；由导出器明确转换并以非对称控制点验证，避免下游重复转换。

跨仓库字段见 [Pipeline 交换约定](https://github.com/williamQ96/open-geospatial-to-3d-reconstruction-pipeline/blob/main/docs/architecture.md)。正式配置与场景 schema v1 已在 upstream 的 `src/geospatial3d/schemas/` 实现。

## 浏览器预览

Three.js 读取导出场景清单，根据资产 ID、版本、相对位置、瓦片和 LOD 加载 GLB。它不负责从 LiDAR 重建或修改 Blender 源资产。

第一版已支持鸟瞰、跟随、第一人称、WASD 漫游、建筑选择、来源展示与线框检查。角色从 upstream 的 ENU heightfield 采样地面，用建筑轮廓进行圆形碰撞与分步移动。区域跳转、瓦片按需加载和独立性能预算留待后续。

GitHub Pages 是原讨论提出的下游目标。目前只创建 private 仓库，未配置部署、公开站点或对象存储。未来发布时单独决定站点可见性与资源托管方式。

## 后续运行时

Godot、Unity、Unreal 都是资产消费者。第一个浏览器闭环通过后，再选择一个引擎验证坐标、比例、材质和法线。3D Gaussian Splatting 可作为后续视觉增强，不承担核心可编辑 Mesh 或碰撞的职责。
