from txt2wav import read_text
import os,sys,argparse,time

start_time = time.time()
dirname, _ = os.path.split(os.path.abspath(__file__))
dirname = dirname+'/'
sys.path.append(dirname)
tmp_dir = dirname+'tmp/'
os.makedirs(tmp_dir,exist_ok=True)

parser=argparse.ArgumentParser()
parser.add_argument('--input_img',type=str,default=r'C:\Users\yzf\Desktop\ALEX/3-ALEX-face.mp4')
parser.add_argument('--input_wav',type=str,default=r'C:\Users\yzf\Desktop\ALEX/ALEX.wav')
parser.add_argument('--output',type=str,default=r'C:\Users\yzf\Desktop\ALEX/')
opt=parser.parse_args()
'''
parser.add_argument('--gender',type=str,default=r'man')
parser.add_argument('--input_txt',type=str,default=r'D:\yzf\SR/talk-head\Wav2Lip-former/input.txt')
#step 1 txt2speech
input_txt = opt.input_txt
if opt.gender=='woman':
    gender = 0
else:
    gender = 1
mid_wav = tmp_dir+input_txt.split('/')[-1].split('.')[0]+'.wav'
with open(input_txt, 'r', encoding='utf-8') as f:
    data = f.readlines()
txt = data[0]
speech_status = read_text(txt,gender, mid_wav)
if not speech_status:
    exit()
'''
mid_wav =  opt.input_wav
#step 2 speech2lip
midout_lip = opt.output
input_img=opt.input_img
#a = os.path.isfile(input_img)
str_v_p = 'python '+dirname+"wav2lip/inference.py --face ~ --audio ~ --outfile ~"
temp = str_v_p.split(' ')  # 4,13
temp[3] = input_img  # bmp
temp[5] = mid_wav  # bmp
temp[-1] = midout_lip  # bmp
command = ' '.join(temp)
print(command)
os.system(command)
#os.remove(mid_wav)


#step 3 face super resolution
face_name = input_img.split('/')[-1].split('.')[0]
audio_name = mid_wav.split('/')[-1].split('.')[0]
name = face_name+'_'+audio_name+'.mp4'
inputfile = dirname+'/tmp/'+name
outfile = dirname+'/tmp/sr/'+name
outvideofile = dirname+'/result/'+name

str_v_p = 'python '+dirname+"former/inference_codeformer.py -i ~ -o ~ -ov ~"
temp = str_v_p.split(' ')  # 4,13
temp[3] = inputfile  # bmp
temp[5] = outfile  # bmp
temp[-1] = outvideofile  # bmp
command = ' '.join(temp)
print(command)
os.system(command)
os.remove(inputfile)

