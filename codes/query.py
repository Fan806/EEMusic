# -*- coding: utf-8 -*-
import cv2
import os
import re
import sys
import h5py
import numpy as np

reload(sys)
sys.setdefaultencoding('utf8')

def HashProcess(des):
	r,c=des.shape
	argmaximum=np.argmax(des)
	argminimum=np.argmin(des)
	nmax=argmaximum/c
	nmin=argminimum/c
	maximum=des[nmax][argmaximum-nmax*c]
	minimum=des[nmin][argminimum-nmin*c]
	normalize=(des-minimum)/(maximum-minimum)

	b=[0.07,0.1,0.13,0.16,0.19,0.22,0.25]
	zhist=np.zeros(len(b)-1)
	for i in normalize:
		hist=np.histogram(i,bins=b)[0]
		hargmax=np.argmax(hist)
		hargmin=np.argmin(hist)
		hmax=float(hist[hargmax])
		hmin=float(hist[hargmin])
		hnorm=(hist-hmin)/(hmax-hmin)
		zhist+=hnorm
	return str(np.around(zhist/100))

def match(des):
	f=h5py.File('imgdata.h5py','r')
	hashname=HashProcess(des)
	imgpaths=f["pathgroup"]
	imgs=f["imggroup"]
	imggroup=f[hashname]
	bf=cv2.BFMatcher()

	keys=imggroup.keys()
	paths=[]
	matchimgs=[]
	
	for k in keys:
		des1=imggroup[k][:]
		matches=bf.match(des1,des)

		d=0
		for j in matches:
			d+=j.distance

		if d<400:
			paths.append(imgpaths[k].value)
			matchimgs.append(imgs[k][:])
	f.close()

	return paths,matchimgs

def interface(imgpath):
	img=cv2.imread(imgpath,cv2.IMREAD_GRAYSCALE)
	sift=cv2.SIFT()
	kp,des=sift.detectAndCompute(img,None)

	#test(des)
	paths,matchimgs=match(des)
	re_img=re.compile(r'.*?\.jpg')
	re_music=re.compile(r'.*?\.wav')
	re_album=re.compile(r'album-')
	geshou=[]
	geming=[]
	zhuanji=[]
	imgurl=[]
	liupai=[]
	shijian=[]
	jianjie=[]
	geci=[]

	for i in paths:
		li=i.split('/')
		musicdir='/'.join(li[:-1]).encode('utf8')
		albumdir='/'.join(li[:-2]).encode('utf8')
		for dirpath,dirname,filenames in os.walk(musicdir):
			for filename in filenames:
				if re.match(re_img,filename):
					continue
				if re.match(re_music,filename):
					continue
				with open(os.path.join(dirpath,filename),'r') as f:
					info1=f.readlines()
					geshou.append(info1[0])
					geming.append(info1[1])
					zhuanji.append(info1[2])
					imgurl.append(info1[3])
					geci.append(info1[4:])
		for dirpath,dirname,filenames in os.walk(albumdir):
			for filename in filenames:
				if re.match(re_album,filename):
					with open(os.path.join(dirpath,filename),'r') as f:
						info2=f.readlines()
						liupai.append(info2[2])
						shijian.append(info2[4])
						jianjie.append(info2[5:])
				else:
					continue	
	print geshou,geming,zhuanji,imgurl,liupai,shijian,jianjie,geci
	return geshou,geming,zhuanji,imgurl,liupai,shijian,jianjie,geci

if __name__ == '__main__':

	imgpath="江湖 - 李艳秋.jpg"
	s=interface(imgpath)
