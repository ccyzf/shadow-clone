import os
import shutil

read_dir = r'C:\Users\yzf\Desktop/1/'
save_dir = r'C:\Users\yzf\Desktop/ALEX/'
for i in os.listdir(read_dir):
    num = int(i.split('.')[0])-1
    save_file = save_dir+str(num)+'.wav'
    shutil.copy(read_dir+i, save_file)