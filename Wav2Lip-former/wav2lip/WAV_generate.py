
# 读取音频文件
import numpy as np
import matplotlib.pyplot as plt
import moviepy.editor as mpy

# 读取音频文件
audio = mpy.AudioFileClip('92030600-1-208.mp3')

# 获取音频的一维频谱
spectrum = audio.to_soundarray()[..., 0].T

# 设置频谱动画的参数
fps = 30  # 视频帧率
duration = audio.duration  # 视频时长
fig_size = (8, 4.5)  # 图像尺寸
cmap = 'coolwarm'  # 色彩映射

# 创建频谱动画
frames = []
for i in range(int(fps * duration)):
    # 计算当前帧对应的时间点
    t = i / fps
    # 取出当前时间点对应的频谱
    spec_t = spectrum[:, int(t * audio.fps)]
    # 绘制频谱图像
    fig, ax = plt.subplots(figsize=fig_size)
    ax.imshow(spec_t[np.newaxis, :], cmap=cmap, aspect='auto')
    ax.axis('off')
    plt.tight_layout()
    # 将图像转换为numpy数组，并添加到帧列表中
    frames.append(np.array(fig.canvas.renderer.buffer_rgba()))

# 保存频谱动画为MP4视频文件
animation = mpy.ImageSequenceClip(frames, fps=fps)
animation.write_videofile('spectrum_animation.mp4')

