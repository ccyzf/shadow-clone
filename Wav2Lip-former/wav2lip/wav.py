from aip import AipSpeech
from pydub import AudioSegment
from pydub.playback import play
import io
""" 你的 APPID AK SK """
APP_ID = '31144360'
API_KEY = 'mczgzQtIBAGSUvbSjBsFfq9Z'
SECRET_KEY = 'AizeqeW9VPYvLTKetO7FNx7sfgCftpqD'
speech = AipSpeech(APP_ID, API_KEY, SECRET_KEY)
"""----------------------------------------------
read_text函数
输入
    text：需要读的文本
    save：是否保存成音频
    name：如果保存那保存成什么名字

输出
    直接读出音频，成功返回1
----------------------------------------------"""
def read_text(text,save = 0,name ="./audio"):
    '''
    result = speech.synthesis(
    text, # UTF-8编码的文本，小于1024字节
    "zh", # zh/en
    1,)
    '''
    result = speech.synthesis(text, 'zh', 1,
                              {'vol': 5,  # 音量，取值0-15，默认为5中音量
                               'per': 0,  # 发音人选择, 0为女声，1为男声，3为情感合成-度逍遥，4为情感合成-度丫丫，默认为普通女
                               'spd': 5,  # 语速，取值0-9，默认为5中语速
                               'pit': 5  # 音调，取值0-9，默认为5中语调
                               }
                              )


    if not isinstance(result, dict):
        print('识别成功，正在播放音频')
        #voice = AudioSegment.from_file(io.BytesIO(result), format="mp3")
        #play(voice)
        if save:
            with open(name+'.mp3', 'wb') as f:
                f.write(result)
        return 1
read_text('通过AI驱动数字人，只需要提前准备好文案，即可让AI数字人24小时不间断直播，及生产海量短视频，为自媒体行业大大降本增效。',1,'audio_woman')
