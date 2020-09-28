# pydub,baidu-aip,moviepy,googletrans,tkinter,multiprocessing
from pydub import AudioSegment
import sys
import os
import shutil
import time
from pydub.silence import detect_nonsilent
from pydub.silence import split_on_silence
from aip import AipSpeech
from moviepy.editor import *
from googletrans import Translator
from multiprocessing import Process
from tkinter import filedialog
from tkinter import *

trans=Translator(service_urls=['translate.google.cn'])
 #百度验证部分
APP_ID = '21476936'
API_KEY = 'baYfkkhB33FP9alPbLp8FYOV'
SECRET_KEY = 'rkOSqWBye5Xx5XkEggAxp6VtkkAXDAj8'
min_silence_len=400
silence_thresh=-38
client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)
silent = AudioSegment.silent(duration=1000)
geshi='mp4'
file =''

#将音频转换为wav
def gotwave(audio,fpz,yppath):
    new = AudioSegment.empty()
    for inx,val in enumerate(audio):
        new=val+silent
        new.export(fpz+'/'+yppath+'/%d.wav' % inx,format='wav')  
        print('分割数量:%d' % inx)

#毫秒换算 根据需要只到分
def ms2s(ms):
    mspart=ms%1000
    mspart=str(mspart).zfill(3)
    spart=(ms//1000)%60
    spart=str(spart).zfill(2)
    mpart=(ms//1000)//60
    mpart=str(mpart).zfill(2)
    
    #srt的时间格式
    stype="00:"+mpart+":"+spart+","+mspart
    return stype
#读取切割后的文件
def get_file_content(filePath):
    with open(filePath, 'rb') as fpx:
        return fpx.read()

#语音识别
def audio2text(wavsample):
    rejson=client.asr(wavsample, 'wav', 16000, {'dev_pid': 1737,})
    if (rejson['err_no']==0):
        result=rejson['result'][0]
    else:
        #result="erro"+str(rejson['err_no'])   
        result="[Music]"
    return result

    
#输出字幕
def text2str(inx,text,starttime,endtime):
    strtext=str(inx)+'\n'+ms2s(starttime)+' --> '+ms2s(endtime)+'\n'+text+'\n'+'\n'
    return strtext

#读写文件
def strtxt(text,videoname,fpc):
    with open(fpc+'/'+videoname.split(".")[0]+'.srt','a') as fpx:
        fpx.write(text)
        fpx.close()
        

    
#main
def listentrans(fp,inputvideo):
    #fp=os.path.split( os.path.realpath( sys.argv[0] ) )[0]
    yp=inputvideo.split('.')[0]
    os.makedirs(fp+'/'+yp)

    #读取音频 预处理
    videofp=fp+'/'+inputvideo
    print(videofp)
    video=VideoFileClip(videofp)
    au=video.audio
    au.write_audiofile(fp+'/'+yp+'/export.wav')

    sound=AudioSegment.from_wav(fp+'/'+yp+'/export.wav')
    sound=sound.set_frame_rate(16000)
    sound=sound.set_channels(1)

    #切割音频
    
    pieces=split_on_silence(sound,min_silence_len,silence_thresh)
    setime=detect_nonsilent(sound,min_silence_len,silence_thresh,1)
    
    start_t=[]
    end_t=[]
    for x in setime:
        start_t.append(x[0])
        end_t.append(x[1]+400)
        
    gotwave(pieces,fp,yp)
    os.remove(fp+'/'+yp+'/export.wav')
    for inx,val in enumerate(pieces):
        wav=get_file_content(fp+'/'+yp+'/%d.wav' % inx)
        text=audio2text(wav)
        t_text=trans.translate(text,dest='zh-cn').text+'\n'+text
        text2=text2str(inx,t_text,start_t[inx],end_t[inx])
        strtxt(text2,inputvideo,fp)
        print(str(round((inx/len(pieces))*100))+'%')
    shutil.rmtree(fp+'/'+yp)

def mainexe():
    print('母线程：{}'.format(os.getpid()))
    st=time.time()
    cv=locals()
    for w,e,r in os.walk(file):
        for i in range(len(r)):
            if r[i].split('.')[1]==geshi:
                cv['p'+str(i)]=Process(target=listentrans,args=(w,r[i]))
                cv.get('p'+str(i)).start()
        for o in range(len(r)):
            cv.get('p'+str(i)).join()
    end=time.time()
    print('用时{}s'.format((end-st)))

t=Tk()
lb=Entry(t,bd=2,width=50)
lb.pack(side=LEFT)
lb.insert(0,'请打开视频目录')
def getdir():
    global file
    fp=filedialog.askdirectory()
    file=fp
    lb.delete(0,'end')
    lb.insert(0,fp)

but=Button(t,text='open',command=getdir)
but.pack()
but2=Button(t,text='start',command=mainexe)
but2.pack()
t.mainloop()