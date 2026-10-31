> 历史 Sites 部署记录；当前主站使用 [GitHub Pages](../hosting.md)。

> 当前更新：在线站点现为 public、免登录；下方保留初次 private 部署记录。两边仓库均已公开。

[English](../hosting.md) | **简体中文**

> 此中文记录保留相应版本的历史背景；最新公开访问、模板和维护状态请参阅默认英文文档。

# OpenCampus: UO 在线预览

地址：<https://opencampus-uo-williamq96.fluffy-chub-9311.chatgpt.site>

通过 Sites 发布为 owner-private 站点，使用站点所有者的 ChatGPT 账号访问。GitHub 仓库继续保持 private；站点访问授权与 GitHub 仓库授权各自独立。在线应用使用与本地 v0.4 相同的静态产物，包含 GLB、地形高度场、路网／名称清单、标志和字体。

## 发布记录

- GitHub 应用代码：`881c7464e7b9984e79bfb7e8b4a8c3e14f84dac5`，此前 13 项测试及 CI 已通过。
- Sites project ID：`appgprj_6ae5957c229c8191a784fdc457532774`。
- Sites source commit：`489b305d46542b10b1c904e4e40a413f143bdea0`。
- Saved version ID：`appgprj_6ae5957c229c8191a784fdc457532774~appgver_e35094db3fd88191b7b6e15a9cc14373`。
- Deployment ID：`appgdep_6ae59631577081918806c915134c2129`；原生部署状态已确认 `succeeded`。
- 构建：对镜像应用执行 `npm ci` 与 `npm run build` 成功，使用受支持的 Sites source helper 推送源码并打包，发布对应的同一份 archive。

## 后续维护

`apps/web-preview/.openai/hosting.json` 保存已有 Site 身份及静态目录 `dist`。后续更新复用此 project ID 和 private audience，不重新创建站点。

`hosting/open-campus-uo/` 是忽略的独立发布工作区，保留前端源码、依赖锁文件、public 资源与自己的 Sites Git 历史。`.openai/hosting.json` 同步自应用的规范配置，`source-provenance.json` 记录镜像对应的 GitHub commit。原始点云和 Blender 源资产仍由主 GitHub 仓库／本地数据工作区维护。

更新时先完成并推送 GitHub 的应用代码，再同步发布工作区；通过 Sites 获取同一 project 的临时 source repository credential，使用 Sites skill 的 `site-workflow.mjs` 推送、构建和打包，然后发布该精确 commit 与 archive，并确认部署终态。临时 credential 只在会话内通过 stdin 传给 helper，不写入仓库或文档。
