# Phone layout and first-person touch

English · [中文说明](#中文说明)

Phone UI uses a compact header/search, a small top-right minimap, 44px view buttons at the bottom and safe-area spacing. Desktop keyboard hints are hidden on phones. Search uses a 16px input font to avoid focus zoom on common mobile browsers. Short landscape screens hide the minimap to leave room for the scene.

In First person, touch anywhere on the lower half of the scene to create a floating joystick. Drag to walk relative to the viewing direction; displacement sets speed, with a dead zone and maximum walking speed. Release to stop. Touch the upper half to look. Two fingers can move and look simultaneously; each finger keeps its initial role when crossing the midpoint. UI controls do not start walking. Follow keeps its look gesture and Overview keeps orbit/pinch.

Movement clears on cancellation/lost capture, blur, hidden page, resize, search, Settings and view changes. Existing keyboard, collision and jump behavior remain available. Touch jump and Follow-mode walking are not added in this pass.

The shared implementation lives upstream in `src/touch.js`, the main input integration and responsive CSS, pinned by `viewer-template.lock.json`. UO models, photo references and art pipeline pins remain separate.

Verification: Chromium touch emulation with native CDP touch events checks analog movement, independent look/move fingers, cancellation, Settings stop and portrait/landscape bounds. Existing desktop, search and landmark tests remain in the suite. This is browser emulation, not a physical iOS/Android device certification.

## 中文说明

手机使用紧凑顶栏、搜索、右上小地图和底部视角切换，适配安全区域。第一人称下半屏任意位置按住拖动产生浮动摇杆，相对镜头方向行走，松手停止；上半屏拖动转向，可双指同时操作，跨过中线不改变该手指用途。切换视角、搜索、设置、取消触摸或失焦等均清除移动。Follow 保持拖动看向，Overview 保持环绕／捏合。原键鼠、碰撞和跳跃保留，本轮未增加触屏跳跃或 Follow 行走。

通用实现回流上游并由模板锁固定，UO 美术资产独立。验证使用 Chromium 原生触摸事件模拟与现有回归，不冒充实体 iOS／Android 真机测试。
