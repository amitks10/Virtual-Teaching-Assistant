# -*- coding: utf-8 -*-
"""
Created on Mon Nov 19 23:47:26 2018

@author: amitks
"""
import random
def get_dict():
	f1=open("science_terms_big.txt","rb")
	word_def_temp=f1.read().decode()
	word_def_temp=word_def_temp.split('$')
	#word_def_temp=[dt.rstrip('\n') for dt in open("science_terms.txt","r")]
	n=len(word_def_temp)
	word_def=[]
	word_def1=[]
	for i in range(0,n):
		if word_def_temp[i] in []:
			continue
		word_def.append(word_def_temp[i].split())
		word_def[i][0]=word_def[i][0].upper()
		if word_def[i][0][len(word_def[i][0])-1]==',':
			word_def[i][0]=word_def[i][0][:-1]
			print (word_def[i][0])
		word_def1.append(word_def[i][0])
	f1.close()
	return word_def1
word_def=get_dict()
print(word_def,len(word_def))
s="999-2-"
cnt=0
f1=open("999-2.trans.txt","wt")
msg=""
for i in range(0,len(word_def)):
	k=random.randint(0,2)
	if k==1:
		if cnt%5==0:
			msg=msg+s	
			if cnt/5<10:
				msg=msg+"00"+str(int(cnt/5))
			elif cnt/5<100:
				msg=msg+"0"+str(int(cnt/5))
			else:
				msg=msg+str(int(cnt/5))
		msg=msg+" "+word_def[i]
		cnt=cnt+1
f1.write(msg)
print(cnt)
f1.close()

		
		
	