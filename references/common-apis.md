# 阶段④：常用能力实战片段

所有片段来自真实上线级项目，可直接改用。每个都标注了坑。

## 1. 页面跳转

```javascript
wx.navigateTo({ url: '/pages/drink/drink?id=' + id })   // 保留当前页，可返回
wx.redirectTo({ url: '/pages/result/result' })          // 替换当前页（结算页用，防返回到中间态）
wx.switchTab({ url: '/pages/index/index' })             // 仅 tabBar 页面
// 接参：目标页 onLoad(options) { options.id }
```

## 2. 本地存储

```javascript
wx.setStorageSync('key', value)        // 自动序列化，对象直接存
const v = wx.getStorageSync('key')     // 不存在返回 ''（空字符串）
// 判空要写 v === '' || v === undefined，布尔值会被 '' 坑
```

## 3. 音效统一管理（utils/audio.js 模式）

```javascript
const SFX = { click: '/assets/audio/click.mp3', cheers: '/assets/audio/cheers.mp3' }
const cache = {}
let sfxEnabled = true

function playSfx(name) {
  if (!sfxEnabled || !SFX[name]) return
  if (!cache[name]) {
    const ctx = wx.createInnerAudioContext()
    ctx.src = SFX[name]
    ctx.volume = 0.8
    cache[name] = ctx
  }
  const ctx = cache[name]
  ctx.stop()   // 关键：先停再播，否则连点不触发
  ctx.play()
}
```

**坑**：一个 InnerAudioContext 同时只播一个音；要叠音（如 BGM+音效、双人音效错开）就一名一实例。BGM 单独实例开 `loop: true`、`volume` 降到 0.3~0.4。页面 onHide 调 `pause()`，onShow 调 `play()`。

## 4. Canvas 2D 动画（新版接口）

```xml
<canvas type="2d" id="myCanvas" class="my-canvas"></canvas>
```

```javascript
wx.createSelectorQuery().select('#myCanvas')
  .fields({ node: true, size: true })
  .exec((res) => {
    const canvas = res[0].node
    const dpr = (wx.getWindowInfo ? wx.getWindowInfo() : wx.getSystemInfoSync()).devicePixelRatio || 2
    canvas.width = res[0].width * dpr    // 必须乘 dpr，否则糊
    canvas.height = res[0].height * dpr
    const ctx = canvas.getContext('2d')

    // 加载图片：不能直接给路径
    const img = canvas.createImage()
    img.onload = () => ctx.drawImage(img, 0, 0, canvas.width, canvas.height)
    img.src = tempFilePath

    // 逐帧动画
    const loop = () => {
      // ... 绘制
      canvas.requestAnimationFrame(loop)
    }
    loop()
  })
```

**坑**：`wx:if` 控制的 canvas 渲染有延迟，query 拿不到节点要 setTimeout 100ms 重试（最多 10 次）；页面 onUnload 必须停 rAF 循环。

**网格形变（照片里的人物动起来）**：把图切 8×8 三角网格，顶点按关键点高斯衰减局部位移，逐三角形 `ctx.transform(a,b,c,d,e,f)` + `ctx.clip()` 仿射绘制（clip 路径外扩 0.9px 消接缝）。完整实现参考 cyber-drink 项目 `utils/facefx.js`。

## 5. 拍照/相册选图

```javascript
wx.chooseMedia({
  count: 1,
  mediaType: ['image'],
  sourceType: ['album', 'camera'],
  sizeType: ['compressed'],           // 省流量省内存
  success: (res) => {
    const tempPath = res.tempFiles[0].tempFilePath  // 临时路径！退出即失效
  }
})
```

**坑**：别用已废弃的 wx.chooseImage；用相机需 app.json 声明 scope.camera；临时路径别存 storage——这正好可以当隐私卖点写进 UI："照片不保存，退出即销毁"。

## 6. 摇晃检测（加速度计）

```javascript
wx.startAccelerometer({ interval: 'game' })
wx.onAccelerometerChange((res) => {
  const g = Math.sqrt(res.x ** 2 + res.y ** 2 + res.z ** 2)
  if (g > 2.2) { /* 判定为摇晃 */ }
})
// onUnload: wx.stopAccelerometer()
```

**坑**：模拟器完全无效，必须保留点击/滑动兜底，否则开发期没法测。

## 7. 震动反馈

```javascript
wx.vibrateShort({ type: 'light' })   // light/medium/heavy
wx.vibrateLong()
```

模拟器无效，静默跳过即可，不用判错。

## 8. 分享

```javascript
// 页面 js
onShareAppMessage() {
  return { title: '来一起玩！', path: '/pages/index/index' }
}
```

```xml
<!-- 按钮触发分享 -->
<button open-type="share">分享给朋友</button>
```

**坑**：朋友圈分享（onShareTimeline）需要单独声明且部分类目不支持；分享图 imageUrl 比例 5:4。

## 9. 人脸检测（AI 能力示例）

```javascript
// 1) 图片 → 离屏 canvas → RGBA 像素（大图先缩到最长边 480px）
const off = wx.createOffscreenCanvas({ type: '2d', width: dw, height: dh })
const octx = off.getContext('2d')
const img = off.createImage()
img.onload = () => {
  octx.drawImage(img, 0, 0, dw, dh)
  const data = octx.getImageData(0, 0, dw, dh)
  // 2) 先初始化再检测
  wx.initFaceDetect({
    success: () => {
      wx.faceDetect({
        frameBuffer: data.data.buffer,   // ArrayBuffer，不是路径！
        width: dw, height: dh,
        success: (res) => {
          if (res.x === -1) return // 没人脸
          const rect = res.detectRect   // {originX, originY, width, height}
        },
        fail: fallback                  // 必须兜底
      })
    },
    fail: fallback
  })
}
img.src = tempFilePath
```

**坑**：基础库 2.18.0+；开发者工具模拟器必失败；detectRect 异常小（<12% 图宽）视为误检；拿到脸框后按人脸比例反推五官（眼 33%/67%×40%，嘴 50%×76%）比赌 106 点序号稳。

## 10. 性能与稳定通则

- setData 只传变化字段，对象用大路径局部更新：`this.setData({ 'obj.field': v })`。
- 动画优先 CSS keyframes；JS 逐帧只用于形变/粒子。
- 所有 wx API 调用都当它会失败：写 fail 或 try/catch，永远有降级路径。
