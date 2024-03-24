import subprocess
import re

def parse_subtitles(subtitle_file):
    with open(subtitle_file, 'r', encoding='utf-8') as file:
        subtitles = file.read()

    pattern = r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.*?)\n\n'
    matches = re.findall(pattern, subtitles, re.DOTALL)

    return [{
        'index': int(match[0]),
        'start': match[1],
        'end': match[2],
        'audio_file': r'C:\Users\yzf\Desktop\ALEX/'+match[0]+'_s.wav'
    } for match in matches]



r'''
def generate_silence(audio_file, duration):
    """生成指定时长的空白音频片段"""
    cmd = [
        'ffmpeg',
        '-f', 'lavfi',
        '-i', 'anullsrc=r=44100:cl=stereo',
        '-t', str(duration),
        audio_file
    ]
    subprocess.run(cmd, check=True)


def merge_audio_with_silence(subtitles, output_file):
    input_files = []
    filter_complex_script = ''
    stream_count = 0

    prev_end_time = 0.0

    for subtitle in subtitles:
        start_time = float(subtitle['start'].replace(',', '.').split(':')[-1])
        if start_time > prev_end_time:
            # 如果有间隔，生成并添加空白片段
            silence_duration = start_time - prev_end_time
            silence_file = rf'C:\Users\yzf\Desktop\ALEX/silence_{stream_count}.mp3'
            generate_silence(silence_file, silence_duration)
            input_files.extend(['-i', silence_file])
            filter_complex_script += f"[{stream_count}:a]"
            stream_count += 1

        input_files.extend(['-i', subtitle['audio_file']])
        filter_complex_script += f"[{stream_count}:a]"
        stream_count += 1
        prev_end_time = float(subtitle['end'].replace(',', '.').split(':')[-1])

    filter_complex_script += f"concat=n={stream_count}:v=0:a=1[a]"

    cmd = [
        'ffmpeg',
        *input_files,
        '-filter_complex', filter_complex_script,
        '-map', '[a]',
        output_file
    ]
    subprocess.run(cmd, check=True)
r'''
def seconds(time_str):
    """将时间字符串转换为秒数"""
    h, m, s = time_str.split(':')
    return int(h) * 3600 + int(m) * 60 + float(s.replace(',', '.'))

def merge_audio_with_silence(subtitles, output_file):
    inputs = []  # 输入文件列表
    filter_complex = []  # filter_complex 字符串列表
    inputs_index = 0  # 输入文件的索引

    for i, subtitle in enumerate(subtitles):
        # 音频片段
        inputs.extend(['-i', subtitle['audio_file']])
        filter_complex.append(f"[{inputs_index}:a]")

        inputs_index += 1

        if i < len(subtitles) - 1:
            next_start = seconds(subtitles[i + 1]['start'])
            current_end = seconds(subtitle['end'])

            # 如果下一个字幕的开始时间晚于当前字幕的结束时间，则插入空白
            if next_start > current_end:
                silence_duration = next_start - current_end
                # 使用anullsrc生成指定长度的空白音频
                inputs.extend(['-f', 'lavfi', '-t', str(silence_duration), '-i', 'anullsrc=channel_layout=stereo:sample_rate=44100'])
                filter_complex.append(f"[{inputs_index}:a]")
                inputs_index += 1

    # 构建完整的filter_complex字符串
    filter_complex_string = ''.join(filter_complex) + f"concat=n={inputs_index}:v=0:a=1[a]"

    # 构建并运行ffmpeg命令
    cmd = ['ffmpeg', *inputs, '-filter_complex', filter_complex_string, '-map', '[a]', output_file]
    subprocess.run(cmd, check=True)



subtitles = parse_subtitles(r'C:\Users\yzf\Desktop/ALEX_subtitles - 副本.txt')
# 假设已有subtitles列表和音频文件路径
merge_audio_with_silence(subtitles, r'C:\Users\yzf\Desktop\ALEX/merged_audio.mp3')
