# -*- coding: utf-8 -*-
"""
Created on Sat Nov 17 22:01:37 2018

@author: amitks
"""

import wave
import pyaudio
def audio_pronun(lis):
	f={}
	n={}
	d={}
	f3=wave.open('sample_test.wav','wb')
	params=[]
	data=b''
	#lis.append('SP')
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
	f=wave.open('sample_test.wav', 'rb')
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


def load_pronun(pronun):
	pronun_t=[dt.rstrip('\n') for dt in open("pronunciation.txt","r")]
	n=len(pronun_t)
	pronun=[]
	for i in range (0,n):
		pronun.append(pronun_t[i].split())
	return pronun
	
def get_pronun(pronun,wrd,n2):	
	wrd=wrd.upper()
	n1=len(wrd)
	l=0
	r=n2-1
	while(l<=r):
		mid=int((l+r)/2)
		fnd=False
		if wrd<pronun[mid][0]:
			r=mid
		elif wrd>pronun[mid][0]:
			l=mid
		else:
			fnd=True
			audio_pronun(pronun[mid][1:])
			
			break
		if (r-l)==1:
			break
	if not fnd:	
		print("---",wrd)
"""
->take care of sentence endings '.'
->pauses??

"""			
def read_script(pronun,n):
	f=open("tts.txt","rt")
	
	wrds=f.read().split()
	print(' '.join(wrds))
	for i in range (0,len(wrds)):
		if wrds[i][len(wrds[i])-1] in ['.',',','?']:
			wrds[i]=wrds[i][:-1]
		get_pronun(pronun,wrds[i],n)
		
	
pronun=[]
pronun=load_pronun(pronun)
pronun_n=len(pronun)
#get_pronun(pronun,"pronunciation",pronun_n)
read_script(pronun,pronun_n)
	
