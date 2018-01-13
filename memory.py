# coding=utf-8

import os

import MySQLdb

import resolve
import re
import subprocess

class memory():
 def __init__(self, host, port, user, passwd, db):
  self.host = host
  self.port = port
  self.user = user
  self.passwd = passwd
  self.db = db

 def addsong(self, path,extra,album):
  if type(path) != str:
   print 'path need string'
   return None
  basename = os.path.basename(path)
  try:
   conn = MySQLdb.connect(host=self.host, port=self.port, user=self.user, passwd=self.passwd, db=self.db,
         charset='utf8')
  except:
   print 'DataBase error'
   return None
  cur = conn.cursor()
  namecount = cur.execute("select * from fingerprint.musicdata WHERE song_name ='%s'" % basename)
  if namecount > 0:
   print 'the song has been record!'
   return None
  v = resolve.voice()
  v.loaddata(path)
  v.fft()
  cur.execute("insert into fingerprint.musicdata VALUES('%s','%s','%s','%s')" % (basename, v.high_point.__str__(),extra,album))
  conn.commit()
  cur.close()
  conn.close()

 def fp_compare(self, search_fp, match_fp):
  if len(search_fp) > len(match_fp):
   return 0
  max_similar = 0
  search_fp_len = len(search_fp)
  match_fp_len = len(match_fp)
  for i in range(match_fp_len - search_fp_len):
   temp = 0
   for j in range(search_fp_len):
    if match_fp[i + j] == search_fp[j]:
     temp += 1
   if temp > max_similar:
    max_similar = temp
  return max_similar

 def search(self, path):
  v = resolve.voice()
  v.loaddata(path)
  v.fft()
  try:
   conn = MySQLdb.connect(host=self.host, port=self.port, user=self.user, passwd=self.passwd, db=self.db,
         charset='utf8')
  except:
   print 'DataBase error'
   return None
  cur = conn.cursor()
  cur.execute("SELECT * FROM fingerprint.musicdata")
  result = cur.fetchall()
  compare_res = []
  for i in result:
   compare_res.append((self.fp_compare(v.high_point[:-1], eval(i[1])), i[0]))
  compare_res.sort(reverse=True)
  cur.close()
  conn.close()
  print compare_res[:5]
  return compare_res

if __name__ == '__main__':
 sss = memory('localhost', 3306, 'music', 'root', 'fingerprint')
 filepath='Music'
 p1 = re.compile('.*?.m4a')
 p2 = re.compile('.*?.jpg')
 p3 = re.compile('^album')
 for i in os.walk(filepath):
   extra=""
   for name in i[2]:
      if type(p1.match(name))==type(None):
          continue
      if len(i[2])==4:
          continue
      print i[0]
      for item in os.listdir(i[0]):
         if type(p1.match(item))==type(None) and type(p2.match(item))==type(None):
             extraf=open(os.path.join(i[0],item).decode('utf8').encode('utf8'))
             extra=extraf.read()
             extraf.close()
             continue
         elif type(p2.match(item))<>type(None):
             continue
         else:
             origin=os.path.join(i[0],item).decode('utf8').encode('utf8')
             newsr=origin.replace("m4a","wav")
             newsr2=newsr.replace("'","prime")
      sub=i[0].split('/')
      sub='/'.join(sub[:-1])
      album=""
      for fi in os.listdir(sub):
         if type(p3.match(fi))==type(None):
              continue
         else:
              albumf=open(os.path.join(sub,fi).decode('utf8').encode('utf8'))
              album=albumf.read()
              albumf.close()
      try:
           subprocess.call(["ffmpeg","-i",origin,newsr])
           sss.addsong(newsr2,extra,album)
      except:
           continue
 #sss.search('chuanqi.wav')
