# 校园活动与室外导航

[English](../campus-life-navigation.md) | **简体中文**

v0.10 加入绿色／黄色服装的通用骨骼角色，不带校徽或 mascot。基础网格、动画和皮肤来自 Kenney Animated Characters 3（CC0）；原创服装材质、背包、车辆与骑行人物为 CC BY 4.0。保留原始 ZIP、实际使用的 FBX／PNG、来源和校验值，角色与道具均提供 Blender 和 GLB 文件。

右上角 **Directions**：Overview 中用 Search A/B 搜索建筑，或 Pin A/B 在地图的建筑外空地选点。选点时面板折叠，避免挡住手机地图。First person 和 Follow 以点击 Start route 时的角色位置为固定 A，只需搜索 B。行走以及切换这两种视角时，蓝色起点圆点与整条路线不移动；人物定位点、白色箭头和到达检测继续更新。再次 Start route 从当前位置开始新路线，Clear 或重新选端点重置起点。Overview 的手动 A 独立保留。关闭面板保留导航。

Settings → Campus life 现为 No / Low / Mid / High 统一密度滑块，默认 Mid；包含松鼠、停放道具和碰撞体。No 清空活动及碰撞，保留角色。当前数量、声音、脚步、晃动及 GitHub 反馈见[第 11 次迭代](ambience-feedback.md)。

导航使用历史道路、原创步道和建筑占位轮廓生成的近似室外图。建筑目的地停在附近路径的接近点，**不是核实过的入口**；无连通路线会提示失败。台阶、围栏、无障碍、施工、通行时间、室内道路均未验证。模型与布局按第一版合理推测、长期纠正的原则维护。

具体重建命令、来源、约束和测试见英文文档。现有三种视角、跳跃、搜索、小地图和上下半屏触控保持可用。
