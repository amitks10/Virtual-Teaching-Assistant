# -*- coding: utf-8 -*-
"""
Created on Wed Nov 21 18:52:27 2018

@author: amitks
"""

"""
Created on Sun Nov 18 21:46:57 2018

@author: amitks
"""
import wave
import pyaudio
import subprocess
import math as m
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
	while data :
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
				f2.write(" ".join(word_def[mid][k+1:]) if word_def[mid][k+1] not in ['is','of']  else " ".join(word_def[mid][k+1:]))
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
            x=math.index(ques[0])
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
def main():
     if get_answer(word_def_big,word_def_small,word_def_geo):
          print("Log: Answer found.")
          read_script()
     else:
          print("Not Found, Adding in our record file.")
          f=open("ques.txt",'r')
          f2=open('unans.txt','a')
          f2.write(f.read()+'\n')
          f.close()
          f2.close()



