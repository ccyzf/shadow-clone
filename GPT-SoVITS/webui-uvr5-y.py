import os
import traceback,gradio as gr
import logging
import sys
from tools.i18n.i18n import I18nAuto
i18n = I18nAuto()

logger = logging.getLogger(__name__)
import librosa,ffmpeg
import soundfile as sf
import torch

from mdxnet import MDXNetDereverb
from vr import AudioPre, AudioPreDeEcho
from tools.slice_audio_y import slice
from subprocess import Popen
now_dir = os.getcwd()
sys.path.append(now_dir)
tmp = os.path.join(now_dir, "TEMP")
os.makedirs(tmp, exist_ok=True)

from tools.asr.funasr_asr import execute_asr
weight_uvr5_root = "tools/uvr5/uvr5_weights"
uvr5_names = []
for name in os.listdir(weight_uvr5_root):
    if name.endswith(".pth") or "onnx" in name:
        uvr5_names.append(name.replace(".pth", ""))

python_exec = 'D:\yzf\SR\GPT-SoVITS-beta\GPT-SoVITS-beta0217/runtime\python.exe'
device="cuda"
is_half=True
is_share=False

exp_name = 'xxx'
model_name = 'HP2_all_vocals'
model_name_DeEchoAggressive = 'VR-DeEchoAggressive'
inp_root = ''
save_root_vocal = "output/uvr5_opt"
save_root_ins = "output/uvr5_opt"
paths =['D:\yzf\SR\GPT-SoVITS-beta\GPT-SoVITS-beta0217\ALEX/vocal_ALEX.wav_10.mp3']
agg = 10
format0 = 'mp3'
def uvr_1(model_name, inp_root, save_root_vocal, paths, save_root_ins, agg, format0):
    infos = []
    print(model_name, inp_root, save_root_vocal, paths, save_root_ins, agg, format0)

    inp_root = inp_root.strip(" ").strip('"').strip("\n").strip('"').strip(" ")
    save_root_vocal = (
        save_root_vocal.strip(" ").strip('"').strip("\n").strip('"').strip(" ")
    )
    save_root_ins = (
        save_root_ins.strip(" ").strip('"').strip("\n").strip('"').strip(" ")
    )
    is_hp3 = "HP3" in model_name
    if model_name == "onnx_dereverb_By_FoxJoy":
        pre_fun = MDXNetDereverb(15)
    else:
        func = AudioPre if "DeEcho" not in model_name else AudioPreDeEcho
        pre_fun = func(
            agg=int(agg),
            model_path=os.path.join(weight_uvr5_root, model_name + ".pth"),
            device=device,
            is_half=is_half,
        )
    if inp_root != "":
        paths = [os.path.join(inp_root, name) for name in os.listdir(inp_root)]
    else:
        paths = [path for path in paths]
    for path in paths:
        inp_path = os.path.join(inp_root, path)
        if(os.path.isfile(inp_path)==False):continue
        need_reformat = 1
        done = 0
        try:
            info = ffmpeg.probe(inp_path, cmd="ffprobe")
            if (
                info["streams"][0]["channels"] == 2
                and info["streams"][0]["sample_rate"] == "44100"
            ):
                need_reformat = 0
                pre_fun._path_audio_(
                    inp_path, save_root_ins, save_root_vocal, format0,is_hp3
                )
                done = 1
        except:
            need_reformat = 1
            traceback.print_exc()
        if need_reformat == 1:
            tmp_path = "%s/%s.reformatted.wav" % (
                os.path.join(os.environ["TEMP"]),
                os.path.basename(inp_path),
            )
            os.system(
                "ffmpeg -i %s -vn -acodec pcm_s16le -ac 2 -ar 44100 %s -y"
                % (inp_path, tmp_path)
            )
            inp_path = tmp_path
        try:
            if done == 0:
                pre_fun._path_audio_(
                    inp_path, save_root_ins, save_root_vocal, format0,is_hp3
                )
            infos.append("%s->Success" % (os.path.basename(inp_path)))

        except:
            infos.append(
                "%s->%s" % (os.path.basename(inp_path), traceback.format_exc())
            )

#uvr_1(model_name, inp_root, save_root_vocal, paths, save_root_ins, agg, format0)

#uvr_1(model_name_DeEchoAggressive, inp_root, save_root_vocal, paths, save_root_ins, agg, format0)

####slice
min_length = 5000
min_interval = 200
#slice(r"D:\yzf\SR\GPT-SoVITS-beta\GPT-SoVITS-beta0217\output\uvr5_opt/vocal_vocal_ALEX.wav_10.mp3_10.mp3",r"output\slicer_opt_1",-34,min_length,min_interval,10,500,0.9,0.25,0,1)

####asr
#execute_asr("D:\yzf\SR\GPT-SoVITS-beta\GPT-SoVITS-beta0217\output\slicer_opt","output/asr_opt_1", 'large','zh')


## 1A
ps1a=[]
def open1a(exp_name,inp_text,inp_wav_dir,bert_pretrained_dir,gpu_numbers):
    global ps1a
    opt_dir = "%s/%s" % ('logs', exp_name)
    config = {
        "inp_text": inp_text,
        "inp_wav_dir": inp_wav_dir,
        "exp_name": exp_name,
        "opt_dir": opt_dir,
        "bert_pretrained_dir": bert_pretrained_dir,
    }
    gpu_names = gpu_numbers.split("-")
    all_parts = len(gpu_names)
    for i_part in range(all_parts):
        config.update(
            {
                "i_part": str(i_part),
                "all_parts": str(all_parts),
                "_CUDA_VISIBLE_DEVICES": gpu_names[i_part],
                "is_half": str(is_half)
            }
        )
        os.environ.update(config)
        print(config)
        cmd = '"%s" GPT_SoVITS/prepare_datasets/1-get-text.py' % python_exec
        print(cmd)
        p = Popen(cmd, shell=True)
        ps1a.append(p)
    for p in ps1a:
        p.wait()
    opt = []
    for i_part in range(all_parts):
        txt_path = "%s/2-name2text-%s.txt" % (opt_dir, i_part)
        with open(txt_path, "r", encoding="utf8") as f:
            opt += f.read().strip("\n").split("\n")
        os.remove(txt_path)
    path_text = "%s/2-name2text.txt" % opt_dir
    with open(path_text, "w", encoding="utf8") as f:
        f.write("\n".join(opt) + "\n")
    ps1a = []

ps1b=[]
def open1b(inp_text,inp_wav_dir,exp_name,gpu_numbers,ssl_pretrained_dir):
    global ps1b
    if (ps1b == []):
        config={
            "inp_text":inp_text,
            "inp_wav_dir":inp_wav_dir,
            "exp_name":exp_name,
            "opt_dir":"%s/%s"%('logs',exp_name),
            "cnhubert_base_dir":ssl_pretrained_dir,
            "is_half": str(is_half)
        }
        gpu_names=gpu_numbers.split("-")
        all_parts=len(gpu_names)
        for i_part in range(all_parts):
            config.update(
                {
                    "i_part": str(i_part),
                    "all_parts": str(all_parts),
                    "_CUDA_VISIBLE_DEVICES": gpu_names[i_part],
                }
            )
            os.environ.update(config)
            cmd = '"%s" GPT_SoVITS/prepare_datasets/2-get-hubert-wav32k.py'%python_exec
            print(cmd)
            p = Popen(cmd, shell=True)
            ps1b.append(p)
        for p in ps1b:
            p.wait()
        ps1b=[]

ps1c=[]
def open1c(inp_text,exp_name,gpu_numbers,pretrained_s2G_path):
    global ps1c
    if (ps1c == []):
        opt_dir="%s/%s"%('logs',exp_name)
        config={
            "inp_text":inp_text,
            "exp_name":exp_name,
            "opt_dir":opt_dir,
            "pretrained_s2G":pretrained_s2G_path,
            "s2config_path":"GPT_SoVITS/configs/s2.json",
            "is_half": str(is_half)
        }
        gpu_names=gpu_numbers.split("-")
        all_parts=len(gpu_names)
        for i_part in range(all_parts):
            config.update(
                {
                    "i_part": str(i_part),
                    "all_parts": str(all_parts),
                    "_CUDA_VISIBLE_DEVICES": gpu_names[i_part],
                }
            )
            os.environ.update(config)
            cmd = '"%s" GPT_SoVITS/prepare_datasets/3-get-semantic.py'%python_exec
            print(cmd)
            p = Popen(cmd, shell=True)
            ps1c.append(p)
        for p in ps1c:
            p.wait()
        opt = ["item_name\tsemantic_audio"]
        path_semantic = "%s/6-name2semantic.tsv" % opt_dir
        for i_part in range(all_parts):
            semantic_path = "%s/6-name2semantic-%s.tsv" % (opt_dir, i_part)
            with open(semantic_path, "r", encoding="utf8") as f:
                opt += f.read().strip("\n").split("\n")
            os.remove(semantic_path)
        with open(path_semantic, "w", encoding="utf8") as f:
            f.write("\n".join(opt) + "\n")
        ps1c=[]


inp_text = 'D:/yzf/SR/GPT-SoVITS-beta/GPT-SoVITS-beta0217/output/asr_opt_1/slicer_opt.list'
inp_wav_dir = 'D:/yzf/SR/GPT-SoVITS-beta/GPT-SoVITS-beta0217/output/slicer_opt'

bert_pretrained_dir = 'GPT_SoVITS/pretrained_models/chinese-roberta-wwm-ext-large'
ssl_pretrained_dir = 'GPT_SoVITS/pretrained_models/chinese-hubert-base'
pretrained_s2G_path = 'GPT_SoVITS/pretrained_models/s2G488k.pth'
gpu_numbers = '0-0'
#open1a(exp_name,inp_text,inp_wav_dir,bert_pretrained_dir,gpu_numbers)
#open1b(inp_text,inp_wav_dir,exp_name,gpu_numbers,ssl_pretrained_dir)
#open1c(inp_text,exp_name,gpu_numbers,pretrained_s2G_path)

import json
import yaml
SoVITS_weight_root = "SoVITS_weights"
GPT_weight_root = 'GPT_weights'
p_train_SoVITS=None
def open1Ba(batch_size,total_epoch,exp_name,text_low_lr_rate,if_save_latest,if_save_every_weights,save_every_epoch,gpu_numbers1Ba,pretrained_s2G,pretrained_s2D):
    global p_train_SoVITS
    if(p_train_SoVITS==None):
        with open("GPT_SoVITS/configs/s2.json")as f:
            data=f.read()
            data=json.loads(data)
        s2_dir="%s/%s"%('logs',exp_name)
        os.makedirs("%s/logs_s2"%(s2_dir),exist_ok=True)
        if(is_half==False):
            data["train"]["fp16_run"]=False
            batch_size=max(1,batch_size//2)
        data["train"]["batch_size"]=batch_size
        data["train"]["epochs"]=total_epoch
        data["train"]["text_low_lr_rate"]=text_low_lr_rate
        data["train"]["pretrained_s2G"]=pretrained_s2G
        data["train"]["pretrained_s2D"]=pretrained_s2D
        data["train"]["if_save_latest"]=if_save_latest
        data["train"]["if_save_every_weights"]=if_save_every_weights
        data["train"]["save_every_epoch"]=save_every_epoch
        data["train"]["gpu_numbers"]=gpu_numbers1Ba
        data["data"]["exp_dir"]=data["s2_ckpt_dir"]=s2_dir
        data["save_weight_dir"]=SoVITS_weight_root
        data["name"]=exp_name
        tmp_config_path="%s/tmp_s2.json"%tmp
        with open(tmp_config_path,"w")as f:f.write(json.dumps(data))

        cmd = '"%s" GPT_SoVITS/s2_train.py --config "%s"'%(python_exec,tmp_config_path)
        print(cmd)
        p_train_SoVITS = Popen(cmd, shell=True)
        p_train_SoVITS.wait()
        p_train_SoVITS=None

batch_size = 4
total_epoch = 4
text_low_lr_rate = 0.4
if_save_latest = True
if_save_every_weights = True
save_every_epoch = 4
gpu_numbers1Ba = "0"
pretrained_s2G = "GPT_SoVITS/pretrained_models/s2G488k.pth"
pretrained_s2D = "GPT_SoVITS/pretrained_models/s2D488k.pth"

#open1Ba(batch_size,total_epoch,exp_name,text_low_lr_rate,if_save_latest,if_save_every_weights,save_every_epoch,gpu_numbers1Ba,pretrained_s2G,pretrained_s2D)

p_train_GPT=None
def open1Bb(batch_size,total_epoch,exp_name,if_dpo,if_save_latest,if_save_every_weights,save_every_epoch,gpu_numbers,pretrained_s1):
    global p_train_GPT
    if(p_train_GPT==None):
        with open("GPT_SoVITS/configs/s1longer.yaml")as f:
            data=f.read()
            data=yaml.load(data, Loader=yaml.FullLoader)
        s1_dir="%s/%s"%('logs',exp_name)
        os.makedirs("%s/logs_s1"%(s1_dir),exist_ok=True)
        if(is_half==False):
            data["train"]["precision"]="32"
            batch_size = max(1, batch_size // 2)
        data["train"]["batch_size"]=batch_size
        data["train"]["epochs"]=total_epoch
        data["pretrained_s1"]=pretrained_s1
        data["train"]["save_every_n_epoch"]=save_every_epoch
        data["train"]["if_save_every_weights"]=if_save_every_weights
        data["train"]["if_save_latest"]=if_save_latest
        data["train"]["if_dpo"]=if_dpo
        data["train"]["half_weights_save_dir"]=GPT_weight_root
        data["train"]["exp_name"]=exp_name
        data["train_semantic_path"]="%s/6-name2semantic.tsv"%s1_dir
        data["train_phoneme_path"]="%s/2-name2text.txt"%s1_dir
        data["output_dir"]="%s/logs_s1"%s1_dir

        os.environ["_CUDA_VISIBLE_DEVICES"]=gpu_numbers.replace("-",",")
        os.environ["hz"]="25hz"
        tmp_config_path="%s/tmp_s1.yaml"%tmp
        with open(tmp_config_path, "w") as f:f.write(yaml.dump(data, default_flow_style=False))
        # cmd = '"%s" GPT_SoVITS/s1_train.py --config_file "%s" --train_semantic_path "%s/6-name2semantic.tsv" --train_phoneme_path "%s/2-name2text.txt" --output_dir "%s/logs_s1"'%(python_exec,tmp_config_path,s1_dir,s1_dir,s1_dir)
        cmd = '"%s" GPT_SoVITS/s1_train.py --config_file "%s" '%(python_exec,tmp_config_path)
        print(cmd)
        p_train_GPT = Popen(cmd, shell=True)
        p_train_GPT.wait()
        p_train_GPT=None

batch_size = 4
total_epoch = 5
if_save_latest = True
if_save_every_weights = True
if_dpo = False
save_every_epoch = 5
gpu_numbers = '0'
pretrained_s1 ='GPT_SoVITS/pretrained_models/s1bert25hz-2kh-longer-epoch=68e-step=50232.ckpt'
open1Bb(batch_size,total_epoch,exp_name,if_dpo,if_save_latest,if_save_every_weights,save_every_epoch,gpu_numbers,pretrained_s1)