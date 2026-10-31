[English](../hosting.md) | **简体中文**

# GitHub Pages 在线预览

**[打开 OpenCampus: UO](https://williamq96.github.io/open-campus-uo/)**：公开、免登录，由 GitHub Pages 托管。

`.github/workflows/pages.yml` 在 main 分支的应用或部署配置更新时，通过 GitHub Actions 安装锁定依赖、检查格式、运行移动／跳跃测试、构建 Vite 静态产物并发布。也可从 Actions 手动运行 Deploy GitHub Pages。

发布目录为 `apps/web-preview/dist`，含 GLB、地形、路网、品牌、字体和署名。`base: "./"` 保证 `/open-campus-uo/` 子路径下正确加载资源，不改变共享模板源码。

GitHub 仓库负责源码保存；GitHub Pages 负责网页托管。此前的 `chatgpt.site` 来自 ChatGPT Sites，是另一家托管服务，见[历史记录](hosting-sites-history.md)。仓库内旧 Sites identity 仅保留作历史证据；当前主站部署不依赖它。

部署后验证 Pages 状态，并在没有登录状态的浏览器中检查场景、搜索、移动、跳跃、视角和署名。
