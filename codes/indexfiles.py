#!/usr/bin/env python

INDEX_DIR = "IndexFiles.index"

import jieba

import sys, os, lucene, threading, time, re
from datetime import datetime
from java.io import File
from org.apache.lucene.analysis.miscellaneous import LimitTokenCountAnalyzer
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.index import FieldInfo, IndexWriter, IndexWriterConfig
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.util import Version

reload(sys)
sys.setdefaultencoding("utf-8")

"""
This class is loosely based on the Lucene (java implementation) demo class 
org.apache.lucene.demo.IndexFiles.  It will take a directory as an argument
and will index all of the files in that directory and downward recursively.
It will index on the file path, the file name and the file contents.  The
resulting Lucene index will be placed in the current directory and called
'index'.
"""

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

    def __init__(self, root, storeDir, analyzer):

        if not os.path.exists(storeDir):
            os.mkdir(storeDir)

        store = SimpleFSDirectory(File(storeDir))
        analyzer = LimitTokenCountAnalyzer(analyzer, 1048576)
        config = IndexWriterConfig(Version.LUCENE_CURRENT, analyzer)
        config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
        writer = IndexWriter(store, config)

        self.indexDocs(root, writer)
        ticker = Ticker()
        print 'commit index',
        threading.Thread(target=ticker.run).start()
        writer.commit()
        writer.close()
        ticker.tick = False
        print 'done'

    def indexDocs(self, root, writer):

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

        files = os.listdir(root)

        for filename in files:
            print "adding", filename
            try:
                path = os.path.join(root, filename)
                file = open(path)
                total = file.read()
                totallist=total.split("\n")

                geshou=totallist[0]
                geming=totallist[1]
                zhuanji=totallist[2]
                imgurl=totallist[3]
                liupai=totallist[4]
                shijian=totallist[5]
                jianjie=totallist[6]
                geci=totallist[7]


                contents = geming+geshou+zhuanji+liupai+geci
                seg_result = jieba.cut(contents)
                contents = ' '.join(seg_result)

                doc = Document() 
                doc.add(Field("contents",contents,t2))
                doc.add(Field("geming", geming, t1))
                doc.add(Field("geshou", geshou, t1))
                doc.add(Field("zhuanji", zhuanji, t1))
                doc.add(Field("liupai",liupai,t1))
                doc.add(Field("geci",geci,t1))
                doc.add(Field("imgurl", imgurl, t1))
                doc.add(Field("shijian",shijian,t1))
                doc.add(Field("jianjie",jianjie,t1))
                    
                writer.addDocument(doc)
                file.close()
            except Exception, e:
                print "Failed in indexDocs:", e

def create_url_dictionary():
    myfile=open("index.txt")
    dic={}
    for line in myfile.readlines():
        split_result=line.split()
        if len(split_result)<=1:
            dic[split_result[0]]="no name"
        dic[split_result[1]]=split_result[0]
    myfile.close()
    return dic



if __name__ == '__main__':
    """
    if len(sys.argv) < 2:
        print IndexFiles.__doc__
        sys.exit(1)
    """
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    print 'lucene', lucene.VERSION
    start = datetime.now()
    try:
        """
        base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        IndexFiles(sys.argv[1], os.path.join(base_dir, INDEX_DIR),
                   StandardAnalyzer(Version.LUCENE_CURRENT))
                   """
        analyzer = StandardAnalyzer(Version.LUCENE_CURRENT)
        IndexFiles("songs","Index" ,analyzer)
        end = datetime.now()
        print end - start
    except Exception, e:
        print "Failed: ", e
        raise e

