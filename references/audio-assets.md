# 阶段⑤：音频/图片素材与包体积控制

## 1. 包体积红线

- **主包上限 2MB**（整个项目目录），超了无法上传。
- 从零养成习惯：每加一个素材跑一次 `du -sh 项目目录`。超 1.5MB 开始警惕。
- 大头永远是音频和图片。图标能用 emoji 就用 emoji（零体积还自带风格）。
- 生成素材的脚本（Python 等）放项目目录**外面**，别打进包。

## 2. 零版权音频三条路（按质量排序）

### 路线 A：真实录音（质量最好，背景音乐首选）

1. 让用户去 Pixabay（pixabay.com/music）浏览器手动搜索下载，CC0 协议可商用无需署名。
   - **注意**：Pixabay/Mixkit 下载接口有反爬（403），curl/脚本下不动，别浪费时间，直接让用户手动下。
2. ffmpeg 裁剪压缩（小程序 BGM 标准处理）：

```bash
# 裁剪 40s + 单声道 + 80kbps + 淡入淡出（循环不咔哒）
ffmpeg -y -i input.mp3 -t 40 -ac 1 -b:a 80k \
  -af "afade=t=in:st=0:d=1,afade=t=out:st=37:d=3" output.mp3
# 40s 约 400KB；从中间截取用 -ss 5 -t 50
```

### 路线 B：程序合成音效（短音效首选，零版权零下载）

用 `scripts/gen_sfx.py`（numpy 合成，需 numpy + ffmpeg）：

- 提供 fft_filter（频域滤波）、glottal（声门谐波激励）、env_ar（包络）等基础件
- 内置示例：哈气/咂嘴/打嗝/酒嗝，改参数就能产新音效
- 要点：人声感 = 谐波激励过共振峰滤波（a 元音 F1 700/F2 1150/F3 2600）+ 气声噪声；粗糙感 = 基频加 30% 随机抖动
- 短音效 64kbps 单声道足够，一个文件 2~7KB

### 路线 C：混合

BGM 用真实录音（路线 A），短音效用合成（路线 B）。本项目最终形态：2 首 BGM 880KB + 11 个音效约 60KB。

## 3. 图片素材

- 一律压缩：tinypng.com 或 `ffmpeg -i in.png -vf scale=目标宽 out.png`。
- 列表图标/装饰 → emoji；背景 → CSS 渐变；只有照片类才用真图。
- 用户上传图必须 `sizeType: ['compressed']`。

## 4. 体积 audit 清单

```bash
du -sh 项目目录            # 总量，红线 2MB
du -sh 项目目录/assets/*   # 找出大头
ls -la 项目目录/assets/audio/  # 单个音频检查
```

发现超限的处理顺序：音频降码率/裁短 → 图片压缩/降分辨率 → 删未用文件 → 最后才考虑分包加载（subpackages）。
