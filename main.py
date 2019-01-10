# -*- coding: utf-8 -*-
"""
Created on Fri Nov 23 14:37:20 2018

@author: MZAIDGAUR and AMITKS and no one else( baaki sabne BT di)
"""

import os
import soundfile as sf
import htk_featio as htk
import speech_sigproc as sp
import sd_beta
import tkinter as tk
import threading
import pyaudio
import wave
import argparse
import subprocess
import math as m

class App():
    def __init__(self, master):
        self.isrecording = False
        self.play = False
        self.button = tk.Button(main, text='rec')
        self.ques = tk.StringVar()
        self.ques.set('Question')
        self.ans = tk.StringVar()
        self.ans.set('Answer')
        self.label_q = tk.Label(main,textvariable=self.ques,bg='#d3d3d3')
        self.label_q.config(anchor='nw',height='8',width='47',wraplength='320',relief='raised')
        self.label_a = tk.Label(main,textvariable=self.ans,bg='#d3d3d3')
        self.label_a.config(anchor='nw',height='15',width='47',wraplength='320',relief='raised')
        string="gif -index {}"
        self.photo=[]
        for i in range(0,10):
             self.photo.append(tk.PhotoImage(master=master,file="record.gif",format=string.format(i)))
        self.button.config(image=self.photo[0],width="325",height="200")
        self.button.bind("<Button-1>", self.startrecording)
        self.button.bind("<ButtonRelease-1>", self.stoprecording)
        self.button.pack()
        self.label_q.pack()
        self.label_a.pack()

    def startrecording(self, event):
        self.play=False
        self.isrecording = True
        self.ques.set('Question')
        self.ans.set('Answer')
        t = threading.Thread(target=self._record)
        t.start()

    def stoprecording(self, event):
        self.isrecording = False

    def _record(self):
        if self.isrecording:
            CHUNK = 1024
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            RATE = 16000
            WAVE_OUTPUT_FILENAME = "rec.wav"
            p = pyaudio.PyAudio()
            stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)
            self.play=True
            print("* recording")
            frames = []
            i=1
            while self.isrecording:
                 self.button.config(image=self.photo[i],width="325",height="200")
                 data = stream.read(CHUNK)
                 frames.append(data)
                 i=i+1
                 if(i==10):
                      i=0
            self.button.config(image=self.photo[0],width="325",height="200")
            print("* done recording")

            stream.stop_stream()
            stream.close()
            p.terminate()
            wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
            wf.close()
            wav_file='rec.wav'
            feat_file='rec.feat'
            x, s = sf.read(wav_file)
            fe = sp.FrontEnd(samp_rate=16000,mean_norm_feat=True)
            feat = fe.process_utterance(x)
            htk.write_htk_user_feat(feat, feat_file)
            feat_rscp_line = os.path.join(feat_file)
            line="%s=%s[0,%d]\n" % (feat_file, feat_rscp_line,feat.shape[1]-1)
            try:
                 ret=sd_beta.decode(line,args.trn,args.beam_width,args.lmweight,z,fst,1)
                 self.ques.set(ret)
                 nlp_main()
            except KeyboardInterrupt:
                 print('End')


def textToWav(text):
     text.upper()
     subprocess.call(["C:\Program Files (x86)\eSpeak\command_line\espeak.exe", "-w words/"+text+".wav", text])


def audio_pronun(lis):
	f={}
	n={}
	d={}
	f3=wave.open('answer_audio.wav','wb')
	params=[]
	data=b''
	#lis.append('SP')
	sum1=0
	for i in range(0,len(lis)):
		try:
			f[i]=wave.open('words/'+lis[i]+'.wav','rb')
		except:
			print("File not found---",lis[i])
			print("Creating and entering in database")
			textToWav(lis[i])
			f[i]=wave.open('words/'+lis[i]+'.wav','rb')
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
	f=wave.open('answer_audio.wav', 'rb')
	p=pyaudio.PyAudio()
	stream=p.open(format=p.get_format_from_width(f.getsampwidth()),channels=f.getnchannels(),rate=f.getframerate(),output=True)
	data=f.readframes(CHUNK)
	while data and app.play:
		stream.write(data)
		data=f.readframes(CHUNK)
	stream.stop_stream()
	stream.close()
	f.close()
	p.terminate()

def read_script():
        f=open("answer.txt","rt")
        wrds=f.read().split()
        n1=len(wrds)
        i=0
        while (i<n1):
                if wrds[i] in ['.','[',']','(',')','-',',','?','!']:
                    wrds.pop(i)
                    n1=n1-1
                    continue
                if len(wrds[i])==0:
                    wrds.pop(i)
                if wrds[i][len(wrds[i])-1] in ['.',',','?','-','!',')']:
                    wrds[i]=wrds[i][:-1]
                if wrds[i][0] in ['(','[']:
                    wrds[i]=wrds[i][1:]
                if wrds[i]=='e.g.':
                    wrds[i]='example'
                i=i+1
        print(' '.join(wrds))
        app.ans.set(' '.join(wrds))
        audio_pronun(wrds)




def get_dict_small(): #Kids dictionary
	word_def_temp=[dt.rstrip('\n') for dt in open("science_terms.txt","r")]

	n=len(word_def_temp)
	word_def=[]
	for i in range(0,n):
		if word_def_temp[i] in []:
			continue
		word_def.append(word_def_temp[i].split())
		word_def[i][0]=word_def[i][0].upper()

	return word_def

def get_dict_big(): #Beautiful soup extracted dictionary
	f=open("science_terms_big.txt","rb")
	word_def_temp=f.read().decode()
	word_def_temp=word_def_temp.split("$")
	f.close()
	n=len(word_def_temp)
	word_def=[]
	for i in range(0,n):
		if word_def_temp[i] in []:
			continue
		word_def.append(word_def_temp[i].split())
		word_def[i][0]=word_def[i][0].upper() 

	return word_def

def get_geo_dict():
        word_def_temp=[dt.rstrip('\n') for dt in open("geographic_terms.txt","r")]
        n=len(word_def_temp)
        word_def=[]
        for i in range(0,n):
            if word_def_temp[i] in []:
                continue
            word_def.append(word_def_temp[i].split())
            word_def[i][0]=word_def[i][0].upper()
        return word_def

def bin_search_answer(word_def,ques,mode):
	f2=open("answer.txt","wt")
	fnd=False
	n2=len(word_def)
	for i in range(0,len(ques)):
		wrd=ques[i]
		if wrd in ["!",".","?"]:
			continue
		if len(wrd)>=2 and wrd[len(wrd)-2] == '\'' and wrd[len(wrd)-1]=='s':
			wrd=wrd[:-2]
		if wrd[len(wrd)-1] in ['?','.']:
			wrd=wrd[:-1]
		wrd=wrd.upper()
		n1=len(wrd)
		l=0
		r=n2
		while(l<=r):
			mid=int((l+r)/2)
			if wrd<word_def[mid][0]:
				r=mid
			elif wrd>word_def[mid][0]:
				l=mid
			else:
				fnd=True
				k=0
				for j in range (0,len(word_def[mid])):
					if word_def[mid][j][len(word_def[mid][j])-1] in [':','-','=',']','$']:
						k=j
						break
				#print(" ".join(word_def[mid][k+1:]))
				f2.write(" ".join(word_def[mid][k+1:]) if word_def[mid][k+1] not in ['is','of']  else " ".join((x if x not in ['-','$'] else '') for x in word_def[mid]))
				break
			if (r-l)==1:
				break
		if fnd:
			break
	if fnd:
		f2.close()
		return fnd



def get_answer(word_def_big,word_def_small,word_def_geo):
        f1=open("ques.txt","r")
        math=['add','subtract','multiply','divide','log','power','square of','square root of']
        ques=f1.read().split()
        f1.close()
        ans_mat=0
        #print(" ".join(ques))
        if len(ques)>=1 and (ques[0] in math):
            f2=open("answer.txt","wt")
            x=math.index(ques[0])
            if x==0:
                add=0
                for i in range(1,len(ques)):
                    add=add+int(ques[i].strip(','))
                ans_mat=add
            elif x==1:
                if 'from' in ques:
                    i=ques.index('from')
                    a=int(ques[i+1].strip(','))
                    b=int(ques[i-1].strip(','))
                else:
                    a=int(ques[1].strip(','))
                    b=int(ques[2].strip(','))
                ans_mat=a-b
            elif x==2:
                add=1
                for i in range(1,len(ques)):
                    add=add*int(ques[i].strip(','))
                ans_mat=add
            elif x==3:
                if 'by' in ques:
                    i=ques.index('by')
                    a=int(ques[i-1].strip(','))
                    b=int(ques[i+1].strip(','))
                else:
                    a=int(ques[1].strip(','))
                    b=int(ques[2].strip(','))
                ans_mat=a/b
            elif x==4:
                if len(ques)>=2 and ques[1]=="of":
                    a=int(ques[2].strip(','))
                else:
                    a=int(ques[1].strip(','))
                b=int(ques[len(ques)-1].strip(','))
                ans_mat=m.log(a,b)
            elif x==5:
                a=int(ques[1].strip(','))
                b=int(ques[len(ques)-1].strip(','))
                ans_mat=b**a
            if (ans_mat<0):
                f2.write("negative "+str(-1*ans_mat))
            else:
                f2.write(str(ans_mat))
            f2.close()
            return True
        elif len(ques)>=2 and (ques[0]+' '+ques[1] in math):
            f2=open("answer.txt","wt")
            for i in range(2,len(ques)):
                ans_mat=int(ques[i].strip(','))**2
            if (ans_mat<0):
                f2.write("negative "+str(-1*ans_mat))
            else:
                f2.write(str(ans_mat))
            f2.close()
            return True
        elif len(ques)>=3 and (ques[0]+' '+ques[1]+' '+ques[2] in math):
            f2=open("answer.txt","wt")
            for i in range(3,len(ques)):
                ans_mat=m.sqrt(int(ques[i].strip(',')))
            if (ans_mat<0):
                f2.write("negative "+str(-1*ans_mat))
            else:
                f2.write(str(ans_mat))
            f2.close()
            return True
        elif bin_search_answer(word_def_small,ques,0):
            return True
        elif bin_search_answer(word_def_big,ques,0):
            return True
        elif bin_search_answer(word_def_geo,ques,1):
            return True
        return False


word_def_small=get_dict_small()
word_def_big=get_dict_big()
word_def_geo=get_geo_dict()
def nlp_main():
     if get_answer(word_def_big,word_def_small,word_def_geo):
          print("Log: Answer found.")
          read_script()
     else:
          print("Not Found. Adding in our record file.")
          app.ans.set("Sorry! Answer not Found. Adding in our record file.")
          f=open("ques.txt",'r')
          f2=open('unans.txt','a')
          f2.write(f.read()+'\n')
          f.close()
          f2.close()



parser = argparse.ArgumentParser(description="Decode speech from parameter files.")
parser.add_argument('-am', '--am', help='CNTK trained acoustic model', required=False, default='D:\GIT_ROOT\Speech-Recognition/Experiments/am/DNN/DNN_CE_forCTC')
parser.add_argument('-decoding_graph', '--decoding_graph', help="Text-format openfst decoding graph", required=False, default='DecodingGraph.fst.txt')
parser.add_argument('-label_map', '--label_map', help="Text files containing acoustic model state labels in the same order used when training the acoustic model", required=False, default='D:\GIT_ROOT\Speech-Recognition/Experiments/am/labels.ciphones')
parser.add_argument('-trn', '--trn', help='Filename to write output hypotheses', required=False, default='ques.txt')
parser.add_argument('-lmweight', '--lmweight', help='Relative weight of LM score', required=False, type=float, default=30.0)
parser.add_argument('-beam_width', '--beam_width', help='Maximum token count per frame', required=False, type=int, default=100)
args = parser.parse_args()
z,fst=sd_beta.main(args.am,args.decoding_graph, args.label_map)

main = tk.Tk()
app = App(main)
main.mainloop()
