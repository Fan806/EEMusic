#!/usr/bin/env python
# encoding: utf-8
INDEX_DIR = "IndexFiles.index"

import sys, os, lucene

from java.io import File
from org.apache.lucene.analysis.core import WhitespaceAnalyzer
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.search import BooleanQuery
from org.apache.lucene.util import Version
import resolve

"""
This script is loosely based on the Lucene (java implementation) demo class 
org.apache.lucene.demo.SearchFiles.  It will prompt for a search query, then it
will search the Lucene index in the current directory called 'index' for the
search query entered against the 'contents' field.  It will then display the
'path' and 'name' fields for each of the hits it finds in the index.  Note that
search.close() is currently commented out because it causes a stack overflow in
some cases.
"""
def run_aud(searcher, analyzer,path):
        print 1
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
	print geci[0]
        print jianjie
        return geshou,geming,zhuanji,liupai,shijian,jianjie,geci,imgurl




if __name__ == '__main__':
    STORE_DIR = "index2"
    print 2
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    print 'lucene', lucene.VERSION
    #base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    directory = SimpleFSDirectory(File(STORE_DIR))
    print 3
    searcher = IndexSearcher(DirectoryReader.open(directory))
    analyzer = WhitespaceAnalyzer(Version.LUCENE_CURRENT)
    geshou,geming,zhuanji,liupai,shijian,jianjie,geci,imgurl=run_aud(searcher, analyzer,'醉在女儿国 - 达坡阿玻.wav')
    del searcher
