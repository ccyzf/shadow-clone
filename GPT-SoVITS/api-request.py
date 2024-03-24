import requests

data={
    "text": "先帝创业未半而中道崩殂，今天下三分，益州疲弊，此诚危急存亡之秋也。",
    "text_language": "zh"
}
response = requests.post("http://127.0.0.1:9880",json=data)
with open("succ.wav",'wb') as f:
    f.write(response.content)