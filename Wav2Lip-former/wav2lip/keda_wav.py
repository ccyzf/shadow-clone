import base64
import json
import time
import hashlib
import requests

# API请求地址、API KEY、APP ID等参数，提前填好备用
api_url = "http://tts-api.xfyun.cn/v2/tts"
API_KEY = "bd889f2723f6b48b1f8637ea81c7f5aa"
APP_ID = "3ceb01a3"
OUTPUT_FILE = "outputkeda.mp3"    # 输出音频的保存路径，请根据自己的情况替换
TEXT = "通过AI驱动数字人，只需要提前准备好文案，即可让AI数字人24小时不间断直播，及生产海量短视频，为自媒体行业大大降本增效。"

# 构造输出音频配置参数
Param = {
    "auf": "audio/L16;rate=16000",    #音频采样率
    "aue": "lame",    #音频编码，raw(生成wav)或lame(生成mp3)
    "voice_name": "aisjiuxu",
    "speed": "50",    #语速[0,100]
    "volume": "77",    #音量[0,100]
    "pitch": "50",    #音高[0,100]
    "engine_type": "intp65"    #引擎类型。aisound（普通效果），intp65（中文），intp65_en（英文）
}
# 配置参数编码为base64字符串，过程：字典→明文字符串→utf8编码→base64(bytes)→base64字符串
Param_str = json.dumps(Param)    #得到明文字符串
Param_utf8 = Param_str.encode('utf8')    #得到utf8编码(bytes类型)
Param_b64 = base64.b64encode(Param_utf8)    #得到base64编码(bytes类型)
Param_b64str = Param_b64.decode('utf8')    #得到base64字符串

# 构造HTTP请求的头部
time_now = str(int(time.time()))
checksum = (API_KEY + time_now + Param_b64str).encode('utf8')
checksum_md5 = hashlib.md5(checksum).hexdigest()
header = {
    "X-Appid": APP_ID,
    "X-CurTime": time_now,
    "X-Param": Param_b64str,
    "X-CheckSum": checksum_md5
}

# 发送HTTP POST请求
def getBody(text):
    data = {'text':text}
    return data
response = requests.post(api_url, data=getBody(TEXT), headers=header)

# 读取结果
response_head = response.headers['Content-Type']
if(response_head == "audio/mpeg"):
    out_file = open(OUTPUT_FILE, 'wb')
    data = response.content # a 'bytes' object
    out_file.write(data)
    out_file.close()
    print('输出文件: ' + OUTPUT_FILE)
else:
    print(response.read().decode('utf8'))