# Overview 深度稳定与渲染评估

[English](../overview-performance.md) | **简体中文**

本地迭代 14 修复可复现的深度冲突，移除重复 CPU 工作。资产、透视、像素比例、抗锯齿、光照、NPC 密度和三视角保持不变。本批未 push／部署。

## 屋顶与铺装闪烁

此前所有视角都让 24 位深度缓冲覆盖 0.08–9000 米。Overview 远景中，相隔很近的屋顶／饰边争抢深度值。同一镜头、模型、材质和光照，只把 near 改为 16 米，就能去掉浅色条纹。[原深度精度](../images/phase14-depth-before.png)、[提高精度](../images/phase14-depth-after.png)。问题属于深度冲突，不需要改掉原棕色风化屋顶材质。

实际修复采用自适应 near：一次计算静态地图包围盒，加 8 米角色／跳跃余量；只在包围盒外的空空间中，使用距离的至多十分之一，向下量化到二次幂，上限 64 米。UO 初始 Overview 为 32 米；进入包围盒内或切 Follow／First person，仍用 0.08 米。FOV、far、透视和地理／模型数据不变。

## 默认优化

- 63 个建筑标签放在独立小型 CSS 场景，保持投影、固定标签和去重逻辑；不再重复遍历所有校园物体及动画骨骼。
- 184 个静态地图节点一次计算后缓存矩阵；角色、学生、车、动物和 Beta 怪物仍正常动态更新。
- 小地图只有真实显示的位置、朝向、目标或路径改变才重画；Overview 拖动相机时内容不变。行走、新路线及清空仍会刷新。
- 坐标显示文字改变时才替换文本节点。

没有减面、降分辨率、降低标签更新频率、移除 NPC 或改变阴影质量。被测默认视图稳定帧仍为 **947,049 三角面／229 次绘制**，像素比例相同。

## 测量与适用范围

工具使用 RTX 5090、原生 ANGLE／D3D11 的无头 Chrome，1440 × 1000 CSS 像素、像素比例 1；初次编译／上传／阴影结束后记录静止、真实鼠标旋转和右键平移。带 CPU profiler 和 GPU query 的测量不等于 Codex 内置浏览器或手机实测。

| 旋转期间平均 CPU 工作 | 原先 | 当前默认 |
| --- | ---: | ---: |
| 标签更新 | 0.334 ms | 0.191 ms |
| WebGL 渲染提交 | 1.405 ms | 1.249 ms |

平移时标签从 0.319 降到 0.189 ms。另一次 4 倍 CPU 限速、像素比例 2 的压力测量中，旋转标签从 2.534 降到 1.490 ms。压力设置属于人工条件，帧间隔和 GPU 排队耗时不能当成手机基准。原生 Chrome 已接近 120 Hz 上限，因此**不声称整体 FPS 提升 40%，也尚未确认内置浏览器的具体瓶颈**；确定收益是减少 CPU 重复工作及远景表面稳定。

保留[原生前](../../data/metadata/performance/phase14-baseline-gpu.json)、[原生后](../../data/metadata/performance/phase14-final-gpu.json)、[压力前](../../data/metadata/performance/phase14-baseline-4x-dpr2.json)、[压力后](../../data/metadata/performance/phase14-final-4x-dpr2.json)的源哈希、采样量、GPU 和环境。大型本地 CPU trace 留在忽略的 artifacts，不上传。

## 已评估、默认关闭：静态雾效缓存

`scene/viewer-settings.json` 可选 `cache_static_haze`，在静态资产最终摆放后缓存原有逐顶点空间雾权重，保留插值及 Toon／PBR 效果。受控图像对照中，两种材质各只有一个像素的一条 8 位通道相差 1，无大于 1/255 的差异。

但 dynamic／cached／cached／dynamic 四轮 GPU 测量及复测收益很小且不稳定，约百分之几毫秒量级；会新增 **5,166,728 字节顶点属性**，CPU／GPU 各有副本，还增加载入计算。因此 UO 明确设置为 **false**，默认缓存顶点与额外属性字节均为零。保留给目标设备实验，不视作已证实的默认优化。[复测结果](../../data/metadata/performance/phase14-haze-ab.json)。

本地 Vite 运行时，在 apps/web-preview 执行 `node scripts/profile-overview.mjs my-overview-probe` 或 `node scripts/compare-render-cache.mjs`。它们只向独立 Playwright 页面注入检查引用／缓存选项，不给公开应用增加调试 API，不发送统计。测量时避免其他浏览器或测试干扰；GPU 微测试需要 timer query 扩展。

若其他浏览器仍卡，应先确认实际 GPU／后端、像素比例与 CPU／GPU／合成器耗时。后续不减几何质量的候选包括保留拾取身份的同材质批处理、交互空间索引、保留所有顶点／法线／颜色的地面分块与视锥剔除；均有 CPU／内存／绘制次数权衡，本批没有宣称实施。动态分辨率、减少 NPC 或模型细节不属于本次评估依据。

见[验证](../../data/metadata/phase14-verification.json)、仅在下游的[开发日志](../../DEVELOPMENT_LOG.zh-CN.md)及[上游通用方法](https://github.com/williamQ96/open-geospatial-to-3d-reconstruction-pipeline/blob/main/docs/zh-CN/render-performance.md)。原 GLB／Blender／图源字节及历史记录均保留。
