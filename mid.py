#!/usr/bin/env python
# -*- coding: utf-8 -*-
INDEX_DIR = "IndexFiles.index"


import resolve

import web
from web import form

import os
import sys
import lucene
import jieba

import cv2
import re
import h5py
import numpy as np

from java.io import File
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.util import Version
from org.apache.lucene.analysis.core import WhitespaceAnalyzer
from org.apache.lucene.search import BooleanQuery



reload(sys)
sys.setdefaultencoding('utf8')


urls = (
    '/', 'index',
    '/s', 's',
    '/img','img_index',
    '/i_s','i_s',
    '/aud','aud_index',
    '/a_s','a_s'
)

render = web.template.render('templates',cache = False) 

login = form.Form(
    form.Textbox('keyword'),
    form.Button('Search for pages'),)

def run(searcher, analyzer,command):
    if command=="":
        return
    seg=jieba.cut(command)
    command=" ".join(seg)

    query = QueryParser(Version.LUCENE_CURRENT, "contents",
                        analyzer).parse(command)
    scoreDocs = searcher.search(query, 20).scoreDocs

    command_list=command.split()

    geming=[]
    geshou=[]
    imgurl=[]
    zhuanji=[]
    shijian=[]
    liupai=[]
    jianjie=[]
    geci=[]

    for scoreDoc in scoreDocs:
        doc = searcher.doc(scoreDoc.doc)
        geming.append(doc.get("geming"))
        geshou.append(doc.get("geshou"))
        imgurl.append(doc.get("imgurl"))
        zhuanji.append(doc.get("zhuanji"))
        shijian.append(doc.get("shijian"))
        liupai.append(doc.get("liupai"))
        jianj=doc.get("jianjie")
        if len(jianj)>250:
        	jianj=jianj[0:250]
        jianjie.append(jianj)
        gec=doc.get("geci")
        if len(geci)>250:
        	gec=gec[0:250]
        geci.append(gec)


    return geshou,geming,zhuanji,imgurl,liupai,shijian,jianjie,geci

def func(command):
    vm_env=lucene.getVMEnv()
    vm_env.attachCurrentThread()
    STORE_DIR = "index"
    directory = SimpleFSDirectory(File(STORE_DIR))
    searcher = IndexSearcher(DirectoryReader.open(directory))
    analyzer = StandardAnalyzer(Version.LUCENE_CURRENT)
    geshou,geming,zhuanji,imgurl,liupai,shijian,jianjie,geci=run(searcher, analyzer,command)
    del searcher
    return command,geshou,geming,zhuanji,imgurl,liupai,shijian,jianjie,geci

class index:
    def GET(self):
        f = login()
        return render.formtest(f)

class s:
    def GET(self):
        user_data = web.input()
        f=login()
        command,geshou,geming,zhuanji,imgurl,liupai,shijian,jianjie,geci = func(user_data.keyword)
        return render.result(f,command,geshou,geming,zhuanji,imgurl,liupai,shijian,jianjie,geci)


login_img = form.Form(
    form.Textbox('image'),
    form.Button('Search for pictures'),)


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
	for i in range(len(geci)):
		if len(geci[i])==0:
			geci[i].append("暂时没有歌词")				
	return geshou,geming,zhuanji,imgurl,liupai,shijian,jianjie,geci

class img_index():
    def GET(self):
        f=login_img()
        return render.formtest_img(f)

class i_s:
    def GET(self):
        img=web.input()
        f=login_img()
        imgpath=img['uploadfile']
        geshou,geming,zhuanji,imgurl,liupai,shijian,jianjie,geci=interface(imgpath)
        print "======"
        print len(geshou)
        return render.result_img(f,geshou,geming,zhuanji,imgurl,liupai,shijian,jianjie,geci)


login_aud = form.Form(
    form.Textbox('audio'),
    form.Button('Search for audio'),)

def run_aud(searcher, analyzer,path):
        print
        print "Searching for:", path
        p = resolve.voice()
        p.loaddata(path)
        p.fft()
        command=str(p.high_point[:-1])
        command=command[1:-1]
        command='+'.join(command.split('('))
        command='+'.join(command.split(')'))
        BooleanQuery.setMaxClauseCount(100000)
        query = QueryParser(Version.LUCENE_CURRENT, "contents",
                            analyzer).parse(command)
        scoreDocs = searcher.search(query, 50).scoreDocs

        geshou=[]
        geming=[]
        zhuanji=[]
        liupai=[]
        shijian=[]
        jianjie=[]
        geci=[]
        imgurl=[]

        for scoreDoc in scoreDocs:
            doc = searcher.doc(scoreDoc.doc)
            geming.append(doc.get("song_name"))
            geshou.append(doc.get('singer_name'))
            zhuanji.append(doc.get('album_name'))
            liupai.append(doc.get('style'))
            shijian.append(doc.get('time'))
            geci.append(doc.get('lyrics'))
            jianjie.append(doc.get('describe'))
            imgurl.append(doc.get("img"))

        return geshou,geming,zhuanji,liupai,shijian,jianjie,geci,imgurl

class aud_index():
    def GET(self):
        f=login_aud()
        return render.formtest_aud(f)

class a_s:
    def GET(self):
        aud=web.input()
        f=login_aud()
        audpath=str(aud['uploadfile'])
        STORE_DIR = "index2"
        vm_env=lucene.getVMEnv()
        vm_env.attachCurrentThread()
        directory = SimpleFSDirectory(File(STORE_DIR))
        searcher = IndexSearcher(DirectoryReader.open(directory))
        analyzer = WhitespaceAnalyzer(Version.LUCENE_CURRENT)
        geshou,geming,zhuanji,liupai,shijian,jianjie,geci,imgurl=run_aud(searcher, analyzer,audpath)
        del searcher
        return render.result_aud(f,geshou,geming,zhuanji,imgurl,liupai,shijian,jianjie,geci)


if __name__ == "__main__":
    vm_env = lucene.initVM()
    app = web.application(urls, globals())
    app.run()

"""
        vm_env=lucene.getVMEnv()
    vm_env.attachCurrentThread()
    STORE_DIR = "index"
    directory = SimpleFSDirectory(File(STORE_DIR))
    searcher = IndexSearcher(DirectoryReader.open(directory))
    analyzer = StandardAnalyzer(Version.LUCENE_CURRENT)
"""
