**English** | [简体中文](zh-CN/hosting.md)

# GitHub Pages explorer

**[Open OpenCampus: UO](https://williamq96.github.io/open-campus-uo/)** — public and no sign-in required. GitHub stores the source repository and hosts the static explorer through GitHub Pages.

## Automatic deployment

`.github/workflows/pages.yml` runs on main-branch changes to the application or Pages workflow, and can also be started manually with **Deploy GitHub Pages**. The build installs locked Node dependencies, checks formatting, runs movement/jump tests and builds Vite. Separate build/deploy jobs upload and publish `apps/web-preview/dist` to the `github-pages` environment using GitHub's Pages/OIDC permissions.

The same output contains GLB, heightfield, source/name/road metadata, branding, self-hosted fonts and license/attribution files. Vite's existing relative `base: "./"` supports the `/open-campus-uo/` project path without changing the shared runtime. Pages is configured with `build_type: workflow`.

Verify the deployment result and test in an anonymous browser context, including asset loading, search, walking, jumping, camera views and About attribution. The normal browser regression workflow remains independent of the hosting workflow.

## Previous Sites deployment

The earlier `https://opencampus-uo-williamq96.fluffy-chub-9311.chatgpt.site` was hosted by ChatGPT Sites, not GitHub Pages. Its initial audience was private and was subsequently changed to public. It is retained as a separate earlier deployment; the GitHub Pages URL above is the primary entry point.

The historical Sites project is `appgprj_6ae5957c229c8191a784fdc457532774`, with identity in `apps/web-preview/.openai/hosting.json`. Its first source commit was `489b305d46542b10b1c904e4e40a413f143bdea0` and initial deployment was `appgdep_6ae59631577081918806c915134c2129`. The public v0.5 release used Sites source commit `e3d4fb654eb991870f7a344a404501ac0ddaca15` and deployment `appgdep_6ae5a0e4eb608191898ebd529303b61e`. These records do not configure the current Pages publication.

The ignored `hosting/open-campus-uo/` checkout preserves that separate history. Current main-branch publication uses GitHub Actions directly and needs no Sites credentials or source mirroring. Raw geographic data and editable Blender asset storage remain separate from website hosting.
