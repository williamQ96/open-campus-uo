[English](../viewer-template.md) | **简体中文**

# 共享浏览器模板

UO 是通用浏览器模板的第一个下游。共享部分包含三种模式、搜索、小地图、标签、移动／跳跃、缩放与设置；具体 UO 模型、名称、品牌、来源与部署身份仍留在本仓库。

`viewer-template.lock.json` 固定共享代码的上游 revision 和文件 SHA-256；`pipeline.lock.json` 独立固定重建版本。使用 `python -m geospatial3d sync-viewer --output <apps/web-preview路径>` 升级模板，会先检查本地共享代码修改并保留项目数据；首次接入才使用 `--adopt`。

升级后运行 UO 浏览器回归并重新构建、发布。上游另有完全合成的独立示例。代码 Apache-2.0，原创内容 CC BY 4.0；保留署名与第三方条款。
