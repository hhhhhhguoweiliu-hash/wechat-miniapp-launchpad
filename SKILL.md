---
name: wechat-miniapp-launchpad
description: 从零开始把一个想法做成可上线的微信小程序的完整流程。当用户说"帮我做个小程序""我想上线一个微信小程序""小程序怎么开发/发布/过审"，或只有一个创意但没有任何开发基础时使用。覆盖注册账号、搭项目、原生框架开发（WXML/WXSS/JS）、Canvas 动画、音频素材、包体积控制、隐私合规、提审发布全链路，以及各环节的实战坑。
agent_created: true
---

# 微信小程序：从想法到上线

把一个创意变成可上线的微信小程序，按六个阶段推进。每个阶段先看要点，需要细节时读对应 references 文件。

```
①想清楚 → ②注册与工具 → ③搭项目骨架 → ④功能开发 → ⑤素材与体积 → ⑥调试与上线
```

## 总原则

- 原生框架优先：零基础项目直接用原生 WXML/WXSS/JS，不引入 Taro/uni-app 等跨端框架，减少一层复杂度。
- 小步快跑：先跑通"首页→一个核心页面"的最小闭环，再迭代功能。每加一个页面立刻在开发者工具里验证。
- 用户必须决策的事不要替他定：小程序名称、类目、主体类型（个人/企业）、图标、隐私协议内容，列清楚选项让用户拍板。
- 包体积从第一天就盯：主包上限 2MB，每加一个素材就查一次 `du -sh`。

## 阶段① 想清楚（不写代码）

先和用户确认四件事，再动手：

1. **一句话定位**：这个小程序给谁用、解决什么乐子/痛点？（例："和朋友线上拼酒的娱乐工具"）
2. **页面清单**：一般不超过 5 个页面，画出页面跳转链（例：选酒→喝酒→结算）。
3. **核心数据**：需要记住什么？存本地（wx.setStorageSync）还是必须上云？零基础优先纯本地，无后端。
4. **类目预判**：去微信公众平台查目标类目是否对个人主体开放（很多类目个人不能上架，如医疗、金融、社交某些子类）。这一步能避免做完才发现不能上线。

产出：一句话定位 + 页面流程图 + 数据清单，写进工作区 memory。

## 阶段② 注册与工具

读 `references/account-setup.md`。要点：

- 在 mp.weixin.qq.com 注册小程序，拿到 **AppID**（个人主体免费，一个身份证最多 5 个）。
- 装**微信开发者工具**（稳定版 Stable Build），用 AppID 创建项目；也可以先用"测试号"模式起步，但上线必须有正式 AppID。
- 让用户自己完成注册（需要微信扫码+实名），助手负责指路。

## 阶段③ 搭项目骨架

读 `references/project-structure.md`。要点：

- 标准目录：`app.js / app.json / app.wxss / pages/ / utils/ / assets/`。
- `app.json` 里注册所有页面（第一项即首页）、配 window 主题、按需声明 permission（如 scope.camera）。
- 每个页面四件套：`.wxml .wxss .js .json`，先在 app.json 注册再写代码。
- 开 `lazyCodeLoading: "requiredComponents"` 减少启动耗时。

## 阶段④ 功能开发

读 `references/common-apis.md`，里面有可直接改用的代码片段。按需求对号入座：

| 需求 | 方案 | 注意 |
|---|---|---|
| 页面跳转 | wx.navigateTo / wx.redirectTo | redirectTo 不压栈，结算页用它 |
| 数据持久化 | wx.setStorageSync / getStorageSync | 只存小数据，别存图片 |
| 动画 | CSS keyframes（优先）/ Canvas 2D（复杂绘制） | canvas 用 `type="2d"` 新版接口 |
| 音效/音乐 | wx.createInnerAudioContext，统一管理模块 | 见 references/audio-assets.md |
| 拍照/相册 | wx.chooseMedia（别用旧的 chooseImage） | 临时路径，退出即失效，正好符合隐私要求 |
| 摇晃手机 | wx.startAccelerometer | 模拟器无效，保留点击兜底 |
| 分享 | onShareAppMessage + button open-type="share" | 分享图 5:4 |
| 人脸/AI | wx.faceDetect 等 | 模拟器不支持，必须兜底；需 scope.camera 声明 |
| 震动反馈 | wx.vibrateShort | 模拟器无效，静默容错 |

**Canvas 局部形变/网格动画**：如果要做"照片里的人物动起来"这类效果，参考本项目实战 `utils/facefx.js`（8×8 三角网格 + 高斯衰减场位移 + 逐三角形仿射绘制），思路：顶点按关键点局部位移，只动五官不动背景。

**长列表/高频更新**：setData 有开销，动画状态、引擎实例等挂 Page 实例属性（this._fx），不进 data。

## 阶段⑤ 素材与体积

读 `references/audio-assets.md`。要点：

- **音效零版权方案**：用 `scripts/gen_sfx.py`（numpy 合成）自产短音效，或 Pixabay 下载 CC0 素材（注意其接口有反爬，让用户浏览器手动下）。
- **ffmpeg 压缩**：背景音乐裁剪 30~60s + 单声道 + 80kbps + 淡入淡出，40s 约 400KB。
- **图片**：全部压缩，图标用 emoji 代替能省大量体积。
- 每加素材跑一次 `du -sh 项目目录`，超 1.5MB 就要警惕。

## 阶段⑥ 调试与上线

读 `references/publish.md`。要点：

1. 开发者工具编译无误 → **真机预览**（扫码），模拟器不支持的能力（传感器/人脸/震动）必须真机验。
2. 上传为**体验版**，发给朋友试用收反馈。
3. 补齐**用户隐私保护指引**（mp 后台→设置→服务内容声明），用了什么权限写什么，写不实会被驳回。
4. 提交审核：选类目、填功能页面截图。个人主体常见驳回点见 publish.md。
5. 审核通过 → 发布 → 全量。

## 实战坑速查（都来自真实项目）

- `wx:if` 切换后 canvas 节点不会立刻存在，SelectorQuery 拿不到就 setTimeout 100ms 重试（上限 10 次）。
- `wx.faceDetect` 要 `wx.initFaceDetect` 先初始化；参数是 RGBA ArrayBuffer 不是文件路径；离线图片要用离屏 canvas 取像素；模拟器必失败，永远准备兜底。
- `chooseMedia` 的 tempFilePath 不要持久化——既是坑也是隐私卖点（"照片不保存，退出即销毁"）。
- InnerAudioContext 一个实例同时只能播一个音；需要叠音就按音效名各建实例并缓存。
- 背景音乐循环拼接处会咔哒响：导出时加淡入淡出。
- canvas 2d 的 drawImage 用 `canvas.createImage()` 加载本地临时图，不能直接给路径。
- CSS 动画能干的别用 JS 逐帧；JS 逐帧只在需要形变/粒子时才上。
- 微信开发者工具的"详情→本地设置"里勾选"不校验合法域名"仅开发期用；上线前所有请求域名必须在 mp 后台配置（纯本地无后端项目忽略）。

## 需要用户出面的环节（提前告知）

注册账号（扫码实名）、小程序命名与图标、类目与主体确认、隐私指引内容确认、提审按钮点击、审核期间可能的材料补充。其余环节助手可以全包。
