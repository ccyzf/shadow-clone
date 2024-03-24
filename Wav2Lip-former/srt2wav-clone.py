import os
import subprocess
import pysrt
from aip import AipSpeech
import datetime
import requests
import json
import edge_tts
import shutil
import asyncio

def read_text(content,man,name):
    communicate = edge_tts.Communicate(content, 'en-US-JennyNeural')
    communicate.save(name)

def transtime(s):
    out = s.TIME_PATTERN%(s.hours,s.minutes,s.seconds,s.milliseconds)
    return out

def get_audio_duration(audio_file):
    cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', audio_file]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    duration = float(result.stdout)
    return duration


def adjust_sub_end_time(sub, audio_duration):
    """根据音频时长调整字幕的结束时间"""
    total_seconds = sub.start.hours * 3600 + sub.start.minutes * 60 + sub.start.seconds + sub.start.milliseconds / 1000 + audio_duration
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)
    milliseconds = int((total_seconds - int(total_seconds)) * 1000)

    # 更新字幕的结束时间
    sub.end = pysrt.SubRipTime(hours=hours, minutes=minutes, seconds=seconds, milliseconds=milliseconds)


tmp_dir = r'C:\Users\yzf\Desktop\ALEX/'
os.makedirs(tmp_dir,exist_ok=True)
srt = pysrt.open(r'C:\Users\yzf\Desktop/ALEX最终版 (transcribed on 13-Mar-2024 00-19-55).en.srt')
input_video = r'C:\Users\yzf\Desktop\ALEX/ALEX.mp4'
for i in srt:

    start = transtime(i.start)
    end = transtime(i.end)
    dur = i.end.seconds*1000+i.end.milliseconds-(i.start.seconds*1000+i.start.milliseconds)
    start_ms = i.start.seconds*1000+i.start.milliseconds

    mp3name = tmp_dir+str(i.index)+'.wav'
    mp3name_speed = tmp_dir + str(i.index) + '_s.wav'

    en_dur = get_audio_duration(mp3name)
    speed = en_dur*1000/dur
    if speed<1:
        # new_end_time = i.start.ordinal + int(en_dur * 1000)  # 计算新的结束时间（微秒）
        adjust_sub_end_time(i, en_dur)
        #i.end = pysrt.SubRipTime(ordinal=new_end_time)
        shutil.copy(mp3name, mp3name_speed)
    else:
        str_v = "ffmpeg -i ~ -filter:a ~ -vn -y ~"
        temp = str_v.split(' ')
        temp[2] = mp3name
        temp[4] = '"atempo='+str(speed)+'"'
        temp[-1] = mp3name_speed
        command = ' '.join(temp)
        os.system(command)
srt.save(r'C:\Users\yzf\Desktop/ALEX_subtitles.srt', encoding='utf-8')
    #os.remove(mp3name)
    #os.remove(name)
'''
    if i.index==1:
        str_v = "ffmpeg -i output_video.mp4 -i 2_s.mp3 -c:a aac -c:v copy -y output_video1.mp4"
        temp = str_v.split(' ')
        temp[2] = input_video
        temp[4] = mp3name_speed
        temp[-1] = tmp_dir + 'output' + str(i.index) + '.mp4'
        command = ' '.join(temp)
        print(command)
        os.system(command)

    else:
        str_v = "ffmpeg -i output_video.mp4 -i 2_s.mp3 -filter_complex ~ -map \"[aout]\" -map 0:v -c:v copy -c:a aac -y output_video1.mp4"
        temp = str_v.split(' ')
        temp[2] = input_video
        temp[4] = mp3name_speed
        temp[6] = '"[1:a]adelay='+str(start_ms)+'|'+str(start_ms)+'[a1];[0:a][a1]amix=inputs=2:dropout_transition=2:normalize=0[aout]"'
        temp[-1] = tmp_dir+'output'+str(i.index)+'.mp4'
        command = ' '.join(temp)
        print(command)
        os.system(command)
        os.remove(input_video)
    os.remove(mp3name_speed)
    input_video = tmp_dir+'output'+str(i.index)+'.mp4'
'''

