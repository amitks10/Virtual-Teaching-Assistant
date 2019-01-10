# -*- coding: utf-8 -*-
"""
Created on Sat Nov 17 21:13:02 2018

@author: MZAIDGAUR
"""
import wave
import pyaudio
f={}
n={}
d={}
f3=wave.open('amit.wav','wb')
params=[]
data=b''
lis=['SP','M' ,'AH' ,'DH' ,'ER','SP']
sum1=0
for i in range(0,len(lis)):
     f[i]=wave.open(lis[i]+'.wav','rb')
     n[i]=f[i].getnframes()
     d[i]=f[i].readframes(n[i])
     sum1+=n[i]
     data+=d[i]
     params=list(f[i].getparams())
     f[i].close()
params[3]=sum1
f3.setparams(tuple(params))
f3.writeframesraw(data)
f3.close()
CHUNK = 1024
f=wave.open('amit.wav', 'rb')
p=pyaudio.PyAudio()
stream=p.open(format=p.get_format_from_width(f.getsampwidth()),channels=f.getnchannels(),rate=f.getframerate(),output=True)
data=f.readframes(CHUNK)
while data :
     stream.write(data)
     data=f.readframes(CHUNK)
stream.stop_stream()
stream.close()
f.close()
p.terminate()
