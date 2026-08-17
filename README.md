# wechat-miniapp-launchpad

> WorkBuddy 技能包：把一个想法做成可上线的微信小程序，零基础全流程陪跑。

适用场景：只有一个创意，没有任何小程序开发经验，想做出一个**能真正上架**的微信小程序。

## 覆盖内容

六阶段主流程（`SKILL.md`）：

```
①想清楚 → ②注册与工具 → ③搭项目骨架 → ④功能开发 → ⑤素材与体积 → ⑥调试与上线
```

| 文件 | 内容 |
|---|---|
| `SKILL.md` | 主流程 + 实战坑速查表（faceDetect 兜底、canvas 重试、包体积红线等） |
| `references/account-setup.md` | 注册小程序账号、AppID、微信开发者工具、测试号 |
| `references/project-structure.md` | 目录约定、app.json 模板、页面四件套、rpx、CSS 变量主题 |
| `references/common-apis.md` | 10 类常用能力的可直接改用代码：跳转/存储/音频/Canvas/拍照/摇晃/震动/分享/人脸检测/性能 |
| `references/audio-assets.md` | 零版权音频三路线（真实录音/程序合成/混合）+ ffmpeg 压缩命令 |
| `references/publish.md` | 体验版、隐私指引、提审流程、个人主体常见驳回原因与对策 |
| `scripts/gen_sfx.py` | numpy 音效合成器：声门谐波 + 共振峰滤波，改参数产新音效 |

所有内容来自真实上线级小程序项目（赛博喝酒）的实战经验，不是教科书摘抄。

## 安装

**方式一：文件夹安装**

把整个文件夹复制到 WorkBuddy 用户级技能目录：

```
Windows: %USERPROFILE%\.workbuddy\skills\wechat-miniapp-launchpad\
macOS/Linux: ~/.workbuddy/skills/wechat-miniapp-launchpad/
```

**方式二：zip 导入**

下载 Release 中的 `wechat-miniapp-launchpad.zip`，在 WorkBuddy 技能管理里导入。

安装后对 WorkBuddy 说"我想做个微信小程序"即可触发。

## 依赖

- 开发：微信开发者工具（免费）
- 音效合成脚本：Python + numpy + ffmpeg（可选，仅 `scripts/gen_sfx.py` 需要）

## License

MIT
