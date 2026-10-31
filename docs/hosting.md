**English** | [简体中文](zh-CN/hosting.md)

# Public web explorer

**[Open OpenCampus: UO](https://opencampus-uo-williamq96.fluffy-chub-9311.chatgpt.site)** — no sign-in required. UO repository visibility and website access are independent settings. The UO repository is public; the upstream repository is also public.

The site serves the same Vite output as local development, including GLB, heightfield, road/name metadata, logo and self-hosted fonts. Anonymous requests have been verified for both the homepage and scene manifest.

## Identity and publication

The existing Sites project is `appgprj_6ae5957c229c8191a784fdc457532774`; reuse it. Its canonical local identity is `apps/web-preview/.openai/hosting.json`, with static directory `dist`.

The first deployment used application commit `881c7464e7b9984e79bfb7e8b4a8c3e14f84dac5`, Sites source commit `489b305d46542b10b1c904e4e40a413f143bdea0`, and deployment `appgdep_6ae59631577081918806c915134c2129`. That initial audience was owner-private. The user subsequently requested public, anonymous access; the access policy is now `public`.

`hosting/open-campus-uo/` is an ignored independent publication checkout with its own Sites source history. Mirror the current application source and public assets, preserve its hosting identity, build with `npm ci` and `npm run build`, and use the Sites source helper to push and package the exact source state. Save the matching archive and deploy through the public deployment operation. Confirm a terminal successful deployment and test without cookies or stored login state.

Keep source credentials only in session memory and pass them to the helper through stdin. Do not persist credentials in Git, shell arguments or documentation. Source hosting and editable Blender/raw geospatial storage are separate concerns.
