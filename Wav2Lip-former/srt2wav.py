import os

import pysrt
from aip import AipSpeech
import datetime
""" 你的 APPID AK SK """
APP_ID = '43896354'
API_KEY = 'PZnyp5atQeUPsjGGPvQsO5k1'
SECRET_KEY = '64a0YeqZUu2DEoB2tBfoLYykdy0hCwTD'

#APP_ID = '31144360'
#API_KEY = 'mczgzQtIBAGSUvbSjBsFfq9Z'
#SECRET_KEY = 'AizeqeW9VPYvLTKetO7FNx7sfgCftpqD'

speech = AipSpeech(APP_ID, API_KEY, SECRET_KEY)
def read_text(text,gender,name ="./audio.mp3"):
    '''
    result = speech.synthesis(
    text, # UTF-8编码的文本，小于1024字节
    "zh", # zh/en
    1,)
    '''
    #zh
    output = False
    try:
        result = speech.synthesis(text, 'en', 1,
                                  {'vol': 5,  # 音量，取值0-15，默认为5中音量
                                   'per': gender,  # 发音人选择, 0为女声，1为男声，3为情感合成-度逍遥，4为情感合成-度丫丫，默认为普通女
                                   'spd': 5,  # 语速，取值0-9，默认为5中语速
                                   'pit': 5  # 音调，取值0-9，默认为5中语调
                                   }
                                  )

        with open(name, 'wb') as f:
            f.write(result)
        print('success output audio')
        output=True
    except:
        print('failed to output audio')
    return output

def transtime(s):
    out = s.TIME_PATTERN%(s.hours,s.minutes,s.seconds,s.milliseconds)
    return out

tmp_dir = 'D:\yzf\SR/talk-head\Wav2Lip-former/tmp/srt2wav/'
os.makedirs(tmp_dir,exist_ok=True)
srt = pysrt.open(r'C:\Users\yzf\Desktop/11月23日 (transcribed on 28-Nov-2023 12-32-22).en.srt')
for i in srt:
    start = transtime(i.start)
    end = transtime(i.end)
    name = start+'-'+end+'.mp3'
    content = i.text
    read_text(content, 0, tmp_dir+name)
