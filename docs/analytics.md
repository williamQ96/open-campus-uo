# Access and interaction statistics

English · [中文说明](#中文说明)

Repository traffic and website traffic are separate. The owner can inspect native GitHub traffic for the [upstream](https://github.com/williamQ96/open-geospatial-to-3d-reconstruction-pipeline/graphs/traffic) and [UO](https://github.com/williamQ96/open-campus-uo/graphs/traffic). Daily API snapshots are retained in the owner's [private analytics archive](https://github.com/williamQ96/open-campus-analytics), starting 2026-10-31. Recent values may be delayed; no earlier history is reconstructed. Daily unique visitors are not additive across dates.

A local Codex automation collects at 09:30 America/Los_Angeles each day using the existing gh login. The desktop must be available; this is not an always-on Actions cloud job. Collection failures need attention before the approximately 14-day API window expires. Authentication remains local.

Website analytics is enabled with the registered site `opencampus-uo-williamq96`, using the upstream GoatCounter adapter. Collection starts with this deployment on 2026-10-31; no earlier website history is reconstructed. The owner can inspect the [GoatCounter dashboard](https://opencampus-uo-williamq96.goatcounter.com/).

The production host is `williamq96.github.io`. Localhost, automated browsers and DNT/GPC visits are excluded. Pageviews contain pathname only, without query/referrer. Fixed events cover camera changes, a search selection, Settings, return to start and touch walking, once per event type per page load. Search text, building IDs and character coordinates are not sent. The provider defines visitor/session counts; blocked requests can undercount. See [GoatCounter privacy](https://www.goatcounter.com/help/privacy) and [upstream methodology](https://github.com/williamQ96/open-geospatial-to-3d-reconstruction-pipeline/blob/main/docs/analytics.md).

The dashboard belongs to the account owner and should remain private. Only the public site code is needed in the browser profile. Website statistics cannot be backfilled from repository traffic.

## 中文说明

上下游仓库访问由 GitHub 自动统计，首份快照已保存到独立私有统计仓库。每日美西 09:30 使用本机 Codex／gh 登录归档，须本机可用，不是全天候云任务。GitHub 仅提供近约 14 天，首次不能恢复更早历史，漏采不能算零。

网页已配置 GoatCounter 站点 `opencampus-uo-williamq96`，从 2026-10-31 本次部署起统计，不补算之前网页历史。[统计后台](https://opencampus-uo-williamq96.goatcounter.com/)由账户所有者查看。仅记录生产域名的访问与固定交互，不发送搜索词、建筑 ID 或角色坐标；同类事件每次加载最多一次。排除本地、自动测试及 DNT／GPC，统计被拦截不影响地图。
