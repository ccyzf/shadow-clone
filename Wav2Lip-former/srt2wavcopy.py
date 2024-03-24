import os

import pysrt
from aip import AipSpeech
import datetime
import requests
import json
import edge_tts
import asyncio

def read_text(content,man,name):
    communicate = edge_tts.Communicate(content, 'en-US-JennyNeural')
    communicate.save(name)

def transtime(s):
    out = s.TIME_PATTERN%(s.hours,s.minutes,s.seconds,s.milliseconds)
    return out

tmp_dir = 'D:\yzf\SR/talk-head\Wav2Lip-former/tmp/srt2wav/'
os.makedirs(tmp_dir,exist_ok=True)
srt = pysrt.open(r'C:\Users\yzf\Desktop/互联网经济发展趋势是什么？你会抓住嘛？ (transcribed on 28-Nov-2023 19-03-33).en.srt')
input_video = 'D:\yzf\SR/talk-head\Wav2Lip-former/tmp\srt2wav/net.mp4'
for i in srt:

    start = transtime(i.start)
    end = transtime(i.end)
    dur = i.end.seconds*1000+i.end.milliseconds-(i.start.seconds*1000+i.start.milliseconds)
    start_ms = i.start.seconds*1000+i.start.milliseconds

    mp3name = tmp_dir+str(i.index)+'.mp3'
    mp3name_speed = tmp_dir + str(i.index) + '_s.mp3'
    name = tmp_dir + str(i.index) + '.srt'
    content = i.text
    #read_text(content, 0, tmp_dir+name)

    str_v_p = "edge-tts --text ~ --voice ~ --write-media ~ --write-subtitles ~"
    temp = str_v_p.split(' ')  # 4,13
    temp[2] = '\"'+content+'\"'  # bmp
    #temp[4] = 'en-US-JennyNeural'
    temp[4] = 'en-US-ChristopherNeural'
    temp[6] = mp3name
    temp[-1] = name
    command = ' '.join(temp)
    os.system(command)

    with open(name,'r') as file:
        line = file.readlines()
        en_dur = float(line[4].split(' ')[2].split(':')[2].strip('\n')) * 1000
    speed = en_dur/dur
    if speed<0.5:
        speed = 0.5
    if i.index==len(srt):
        speed = 1
    str_v = "ffmpeg -i ~ -filter:a ~ -vn -y ~"
    temp = str_v.split(' ')
    temp[2] = mp3name
    temp[4] = '"atempo='+str(speed)+'"'
    temp[-1] = mp3name_speed
    command = ' '.join(temp)
    os.system(command)

    os.remove(mp3name)
    os.remove(name)

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
        #os.remove(input_video)
    os.remove(mp3name_speed)
    input_video = tmp_dir+'output'+str(i.index)+'.mp4'

