# gen_sfx.py - 小程序零版权音效合成器
# 用 numpy 合成短音效，ffmpeg 转 mp3。改 main 里的生成函数即可产出新音效。
# 依赖：numpy + ffmpeg（命令行可用）
# 用法：python gen_sfx.py 输出目录
#
# 合成套路（来自真实项目验证）：
#   人声音色 = 声门谐波激励(glottal) 过共振峰滤波(fft_filter) + 气声噪声
#   a 元音共振峰：F1 700 / F2 1150 / F3 2600；i 元音：F1 300 / F2 2200
#   粗糙/醉酒感 = 基频加 20~35% 随机抖动；打击感 = 频率快速下扫 + 短噪声瞬态

import numpy as np
import subprocess
import os
import sys

SR = 44100


# ---------- 基础件（一般不用改） ----------

def fft_filter(x, bands):
    """FFT 频域滤波。bands = [(f_lo, f_hi, gain), ...]，升余弦边缘防振铃"""
    n = len(x)
    X = np.fft.rfft(x)
    freqs = np.fft.rfftfreq(n, 1.0 / SR)
    mask = np.zeros_like(freqs)
    for (lo, hi, gain) in bands:
        edge_lo = lo * 0.6
        edge_hi = hi * 1.5
        m = np.zeros_like(freqs)
        rise = (freqs >= edge_lo) & (freqs < lo)
        m[rise] = 0.5 - 0.5 * np.cos(np.pi * (freqs[rise] - edge_lo) / max(lo - edge_lo, 1))
        mid = (freqs >= lo) & (freqs <= hi)
        m[mid] = 1.0
        fall = (freqs > hi) & (freqs <= edge_hi)
        m[fall] = 0.5 + 0.5 * np.cos(np.pi * (freqs[fall] - hi) / max(edge_hi - hi, 1))
        mask += m * gain
    return np.fft.irfft(X * mask, n)


def glottal(dur, f0_start, f0_end, jitter=0.0, n_harm=12):
    """声门脉冲激励：谐波叠加（1/k 衰减），jitter 控制嗓子粗糙度"""
    n = int(dur * SR)
    f0 = np.linspace(f0_start, f0_end, n)
    if jitter > 0:
        f0 = f0 * (1 + jitter * np.random.randn(n) * 0.5)
        f0 = np.clip(f0, 30, 1200)
    phase = 2 * np.pi * np.cumsum(f0) / SR
    sig = np.zeros(n)
    for k in range(1, n_harm + 1):
        sig += np.sin(k * phase) / k
    return sig


def env_ar(n, attack, release):
    """快攻慢放包络"""
    e = np.ones(n)
    a = max(int(attack * SR), 1)
    r = max(int(release * SR), 1)
    e[:a] = np.linspace(0, 1, a)
    e[-r:] = np.linspace(1, 0, r)
    return e


def sweep_pop(dur, f_start, f_end, decay=55):
    """频率下扫爆裂音：咂嘴/气泡/敲击的基础件"""
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = (f_start - f_end) * np.exp(-t * decay * 0.8) + f_end
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * decay)


def save_mp3(name, x, out_dir, peak=0.85):
    """归一化并转 mp3（单声道 64kbps，短音效够用）"""
    m = np.max(np.abs(x))
    if m > 1e-9:
        x = x / m * peak
    raw = os.path.join(out_dir, name + '.raw')
    mp3 = os.path.join(out_dir, name + '.mp3')
    (np.clip(x, -1, 1) * 32767).astype(np.int16).tofile(raw)
    subprocess.run(['ffmpeg', '-y', '-f', 's16le', '-ar', str(SR), '-ac', '1',
                    '-i', raw, '-ac', '1', '-b:a', '64k', mp3],
                   check=True, capture_output=True)
    os.remove(raw)
    print(f'  {name}.mp3  {os.path.getsize(mp3) // 1024}KB')


# ---------- 示例音效（按需改写/增删） ----------

def gen_ha(out):
    """哈气"哈~"：喝完东西的满足叹息"""
    dur = 0.85
    n = int(dur * SR)
    t = np.arange(n) / SR
    voice = glottal(dur, 165, 105, jitter=0.02, n_harm=10)
    voice_fmt = (fft_filter(voice, [(550, 900, 1.0)]) +
                 fft_filter(voice, [(950, 1400, 0.55)]) +
                 fft_filter(voice, [(2200, 3000, 0.22)]))
    voice_fmt *= np.exp(-t * 6.0) * env_ar(n, 0.03, 0.15)
    breath = fft_filter(np.random.randn(n), [(400, 3800, 1.0)])
    breath *= (0.9 * np.exp(-t * 4.5) + 0.25 * np.exp(-t * 2.0)) * env_ar(n, 0.02, 0.2)
    save_mp3('voice_ha', voice_fmt * 0.55 + breath * 0.45, out)


def gen_pop(out):
    """咂嘴"啧"：唇音爆裂"""
    dur = 0.3
    n = int(dur * SR)
    sig = np.zeros(n)
    pop = sweep_pop(0.06, 1100, 250, decay=55)
    cl = np.random.randn(int(0.006 * SR)) * np.exp(-np.arange(int(0.006 * SR)) / (0.0015 * SR))
    seg = np.concatenate([cl, pop])
    sig[:len(seg)] = seg
    sig = sig * 0.7 + fft_filter(sig, [(300, 900, 0.8)]) * 0.5
    save_mp3('voice_pop', sig, out)


def gen_burp(out):
    """打嗝"呃~"：超低基频 + 重抖动"""
    dur = 0.6
    n = int(dur * SR)
    t = np.arange(n) / SR
    voice = glottal(dur, 80, 55, jitter=0.35, n_harm=8)
    am = np.convolve(np.random.randn(n), np.ones(int(0.02 * SR)), 'same')
    voice *= np.clip(0.6 + am * 0.8, 0.1, 1.4)
    voice = fft_filter(voice, [(50, 450, 1.0)])
    env = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 0.7 * env_ar(n, 0.02, 0.1)
    noise = fft_filter(np.random.randn(n), [(80, 500, 0.6)]) * env * 0.35
    save_mp3('voice_burp', voice * env * 0.8 + noise, out)


def gen_click(out):
    """点击音：UI 反馈"""
    sig = sweep_pop(0.05, 2000, 800, decay=90)
    save_mp3('ui_click', sig, out)


if __name__ == '__main__':
    out_dir = sys.argv[1] if len(sys.argv) > 1 else '.'
    os.makedirs(out_dir, exist_ok=True)
    np.random.seed(42)
    print('合成音效到', out_dir)
    gen_ha(out_dir)
    gen_pop(out_dir)
    gen_burp(out_dir)
    gen_click(out_dir)
    print('完成')
