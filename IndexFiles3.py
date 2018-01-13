#!/usr/bin/env python
# encoding: utf-8
INDEX_DIR = "IndexFiles.index"

import sys, os, lucene, threading, time
from datetime import datetime

from java.io import File
from org.apache.lucene.analysis.miscellaneous import LimitTokenCountAnalyzer
from org.apache.lucene.analysis.core import WhitespaceAnalyzer
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.index import FieldInfo, IndexWriter, IndexWriterConfig
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.util import Version
import MySQLdb
import resolve
import re
import subprocess
reload(sys)
sys.setdefaultencoding('utf-8')
class Ticker(object):

    def __init__(self):
        self.tick = True

    def run(self):
        while self.tick:
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(1.0)

class IndexFiles(object):
    """Usage: python IndexFiles <doc_directory>"""

    def __init__(self, storeDir, analyzer):

        if not os.path.exists(storeDir):
            os.mkdir(storeDir)

        store = SimpleFSDirectory(File(storeDir))
        analyzer = LimitTokenCountAnalyzer(analyzer, 1048576)
        config = IndexWriterConfig(Version.LUCENE_CURRENT, analyzer)
        config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
        writer = IndexWriter(store, config)

        self.indexDocs(writer)
        ticker = Ticker()
        print 'commit index',
        threading.Thread(target=ticker.run).start()
        writer.commit()
        writer.close()
        ticker.tick = False
        print 'done'

    def indexDocs(self, writer):

        t1 = FieldType()
        t1.setIndexed(True)
        t1.setStored(True)
        t1.setTokenized(False)
        t1.setIndexOptions(FieldInfo.IndexOptions.DOCS_AND_FREQS)
        
        t2 = FieldType()
        t2.setIndexed(True)
        t2.setStored(False)
        t2.setTokenized(True)
        t2.setIndexOptions(FieldInfo.IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)
        try:
              conn = MySQLdb.connect(host='localhost', port=3306, user='music', passwd='root', db='fingerprint',charset='utf8')
        except:
            print 'DataBase error'
            return None
        cur = conn.cursor()
        cur.execute("SELECT * FROM fingerprint.musicdata")
        result = cur.fetchall()
        for i in result:
           extra=i[2].split('\n')
           singer_name=extra[0]
           song_name=extra[1]
           album_name=extra[2]
           img=extra[3]
           if len(extra)>4:
             lyrics=' '.join(extra[4:])
           else:
             lyrics='暂时没有歌词'
           if lyrics=='':
             lyrics='暂时没有歌词'
           album=i[3].split('\n')
           style=album[2]
           time=album[4]
           if len(album)>7:
              describe=album[-1]
           else:
              describe='暂时没有简介'
           if describe=='':
              describe='暂时没有简介'
           content=i[1][1:-1]
           content=' '.join(content.split('('))
           content=' '.join(content.split(')'))
           try:
                    doc = Document()
                    print "adding", song_name
                    doc.add(Field("singer_name", singer_name, t1))
                    doc.add(Field("song_name", song_name, t1))
                    doc.add(Field("album_name", album_name, t1))
                    doc.add(Field("img", img, t1))
                    doc.add(Field("style", style, t1))
                    doc.add(Field("time", time, t1))
                    doc.add(Field("describe", describe, t1))
                    doc.add(Field("lyrics", lyrics, t1))
                    doc.add(Field("contents", content, t2))
                    writer.addDocument(doc)
           except Exception, e:
                    print "Failed in indexDocs:", e
        cur.close()
        conn.close()

if __name__ == '__main__':
    """
    if len(sys.argv) < 2:
        print IndexFiles.__doc__
        sys.exit(1)
    """
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    print 'lucene', lucene.VERSION
    start = datetime.now()
    
    """
        base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        IndexFiles(sys.argv[1], os.path.join(base_dir, INDEX_DIR),
                   StandardAnalyzer(Version.LUCENE_CURRENT))
                   """
    analyzer = WhitespaceAnalyzer(Version.LUCENE_CURRENT)
    IndexFiles("index2", analyzer)
    end = datetime.now()
    print end - start
