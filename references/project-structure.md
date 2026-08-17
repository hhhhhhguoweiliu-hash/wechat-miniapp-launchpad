# 阶段③：项目骨架与页面模式

## 1. 标准目录结构

```
project/
├── app.js          # 全局逻辑：onLaunch、globalData
├── app.json        # 全局配置：页面注册、窗口样式、权限声明
├── app.wxss        # 全局样式：CSS 变量、通用类
├── sitemap.json    # 搜索收录配置（默认即可）
├── project.config.json  # 工具自动维护，别手改
├── pages/
│   ├── index/      # 首页（app.json pages 数组第一项）
│   │   ├── index.wxml   # 结构（类似 HTML）
│   │   ├── index.wxss   # 样式（类似 CSS，单位用 rpx）
│   │   ├── index.js     # 逻辑（Page({...})）
│   │   └── index.json   # 页面级配置（导航标题等）
│   └── page2/ ...
├── utils/          # 公共 JS 模块（数据、音频管理、引擎）
└── assets/         # 图片/音频，能压就压
```

## 2. app.json 模板（可直接改）

```json
{
  "pages": [
    "pages/index/index",
    "pages/page2/page2"
  ],
  "window": {
    "navigationBarBackgroundColor": "#1a1a2e",
    "navigationBarTitleText": "小程序名",
    "navigationBarTextStyle": "white",
    "backgroundColor": "#0f0f1e"
  },
  "style": "v2",
  "sitemapLocation": "sitemap.json",
  "lazyCodeLoading": "requiredComponents",
  "permission": {
    "scope.camera": {
      "desc": "用于拍摄照片"
    }
  }
}
```

- `pages` 第一项 = 首页；新增页面必须在这里注册，否则跳转 404。
- `permission` 只在用到对应能力时加（相机/定位等），desc 会展示给用户。
- `lazyCodeLoading: "requiredComponents"` 按需注入，减少启动时间。

## 3. 页面四件套最小模板

**page.js**

```javascript
Page({
  data: { count: 0 },
  onLoad(options) {},     // 首次进入，options 带 URL 参数
  onShow() {},            // 每次显示（适合恢复音乐）
  onHide() {},            // 每次隐藏（适合暂停音乐）
  onUnload() {},          // 页面销毁（适合清临时资源）
  handleTap(e) {
    // 读取 data-* 传参
    const id = e.currentTarget.dataset.id
    // 改数据必须 setData，直接 this.data.x = 1 不触发渲染
    this.setData({ count: this.data.count + 1 })
  },
  onShareAppMessage() {   // 右上角分享
    return { title: '分享文案', path: '/pages/index/index' }
  }
})
```

**page.wxml**

```xml
<view class="container">
  <text>{{count}}</text>
  <button bindtap="handleTap" data-id="{{item.id}}">点我</button>
  <view wx:for="{{list}}" wx:key="id">{{item.name}}</view>
  <view wx:if="{{show}}">条件渲染</view>
</view>
```

**关键规则**：

- 数据绑定 `{{ }}` 里不能写函数调用，只能写简单表达式。
- 事件：`bindtap`（点击）、`bindlongpress`（长按）、`bindtouchmove`（滑动）。
- 循环必须 `wx:key`，否则警告+性能差。
- 图片/媒体临时路径退出页面即失效，不要存 storage。

## 4. rpx 与样式

- `rpx` 自适应单位：屏幕宽恒为 750rpx。设计稿按 375pt 宽想，数值×2 就是 rpx。
- 主题切换推荐 **CSS 变量**：页面根节点 inline style 注入 `--accent: #EF9F27`，wxss 里 `color: var(--accent)`，一套代码多套主题。
- 全局背景渐变这类通用样式放 app.wxss。

## 5. 全局数据与模块

```javascript
// app.js
App({
  globalData: { styleMode: 'heroic' },
  onLaunch() {}
})
// 页面里：const app = getApp(); app.globalData.styleMode
```

公共逻辑（常量数据、音频管理）放 `utils/xxx.js`，`module.exports` 导出，页面 `require('../../utils/xxx.js')` 引入。

## 6. 高频状态别进 data

setData 每次都会序列化并触发渲染 diff。动画引擎实例、定时器 ID、Canvas 上下文、关键点数据等挂实例属性：

```javascript
Page({
  data: { /* 只有需要渲染的 */ },
  _engine: null,   // 挂这里
  onUnload() { if (this._engine) this._engine.stop() }
})
```
