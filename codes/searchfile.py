#!/usr/bin/env python

INDEX_DIR = "IndexFiles.index"

import sys, os, lucene

from java.io import File
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.util import Version
from org.apache.lucene.search import BooleanQuery
from org.apache.lucene.search import BooleanClause

import jieba

def run(searcher, analyzer):
    while True:
        print
        print "Hit enter with no input to quit."
        command = raw_input("Query:")
        command = unicode(command, 'utf-8')
        if command == '':
            return

        print

        seg_result=jieba.cut(command)
        command=" ".join(seg_result)
        print "Searching for:", command
        
        query = QueryParser(Version.LUCENE_CURRENT,"contents",analyzer).parse(command)
        scoreDocs = searcher.search(query, 50).scoreDocs
        print "%s total matching documents." % len(scoreDocs)

        for scoreDoc in scoreDocs:
            doc = searcher.doc(scoreDoc.doc)
            print "------------------------"
            print 'imgurl:', doc.get("imgurl")
            print 'geming:', doc.get('geming')
            print 'geshou:', doc.get('geshou')
            print "zhaunji",doc.get("zhuanji")
            print "liupai",doc.get("liupai")
            print "shijian",doc.get("shijian")
            print "jianjie",doc.get("jianjie")
            print "geci",doc.get("geci")


if __name__ == '__main__':
    STORE_DIR = "index"
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    print 'lucene', lucene.VERSION
    #base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    directory = SimpleFSDirectory(File(STORE_DIR))
    searcher = IndexSearcher(DirectoryReader.open(directory))
    analyzer = StandardAnalyzer(Version.LUCENE_CURRENT)
    run(searcher, analyzer)
    del searcher


