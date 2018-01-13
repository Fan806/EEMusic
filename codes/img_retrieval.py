import cv2
import os
import re
import h5py
import numpy as np

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

def main():
	cwd=os.getcwd()
	imgdata="Music"
	re_img=re.compile(r'.*?\.jpg')
	re_music=re.compile(r'.*?\.wav')
	re_album=re.compile(r'album-')

	sift=cv2.SIFT()
	count=0

	f=h5py.File("imgdata.h5py","a")
	grpimg=f.create_group("imggroup")
	grppath=f.create_group("pathgroup")
	dic={}

	for dirpath,dirname,filenames in os.walk(os.path.join(cwd,imgdata)):
		for filename in filenames:
			if re.match(re_img,filename):
				count+=1
				imgpath=os.path.join(os.path.join(dirpath,filename))
				img=cv2.imread(imgpath,cv2.IMREAD_GRAYSCALE)
				imgori=cv2.imread(imgpath)
				if type(img)==type(None):
					continue
				kp,des=sift.detectAndCompute(img,None)
				hashname=HashProcess(des)
				print filename,hashname
				if not dic.has_key(hashname):
					grphash=f.create_group(hashname)
					dic[hashname]=grphash

				imgname="img"+str(count)
				desname="des"+str(count)

				grpimg.create_dataset(imgname,data=imgori)
				grppath.create_dataset(imgname,data=imgpath)
				dic[hashname].create_dataset(imgname,data=des)

	f.close()

main()
