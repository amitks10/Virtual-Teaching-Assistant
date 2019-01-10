# -*- coding: utf-8 -*-
"""
Created on Tue Nov 20 11:26:43 2018

@author: amitks
"""

def load_pronun(pronun):
	pronun_t=[dt.rstrip('\n') for dt in open("pronunciation.txt","r")]
	n=len(pronun_t)
	pronun=[]
	for i in range (0,n):
		pronun.append(pronun_t[i].split())
	return pronun

def get_all_sounds(pronun):
	f1=open("diff_sounds.txt","wt")
	msg=""
	n=len(pronun)
	word_list=[]
	cnt=0
	for i in range (0,n):
		for j in range (1,len(pronun[i])):
			if pronun[i][j] not in word_list:
				word_list.append(pronun[i][j])
				msg=msg+"\n"+pronun[i][j]
				cnt=cnt+1
			if cnt==40:
				print("0\n")
	print(cnt)
	f1.write(msg)

pronun=[]
pronun=load_pronun(pronun)
get_all_sounds(pronun)