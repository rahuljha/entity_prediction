#!/usr/bin/python

import sys
import nltk
import json
import math
from nltk.corpus import stopwords
from utils import get_ft_ngrams

import time

from aanmeta import aanmeta
from citation_nw import CitationNetwork

# Given a reference year and forecast year
# start from 1980 and get all titles till reference 
# Extract 1,2 and 3 grams from the titles and create feature files for training data

lyear = 1980
hyear = 2006

aan = aanmeta()
refpapers = aan.get_restricted_papers(1980, 2006)

# # refpapers.sort(key=lambda x: x.year)

ngram_sep = "_"

feat_file_name = "%s_%s.pruned_feats" % (lyear, hyear)
feat_file = open(feat_file_name, 'w')
# resp_file = open(resp_file_name, 'w')

stopwords = stopwords.words('english')
featfreq = {}
initfeats = {}

print "Total %d papers" % len(refpapers)

for p in refpapers:
    print "Processing %s (%d)" % (p.pid, time.time())
    words = [i.strip().lower() for i in nltk.word_tokenize(p.title)]
    
#    titleunigrams = [w for w in words if not w in stopwords]
    titleunigrams = words
    
    titlebigrams = [ngram_sep.join(i) for i in nltk.bigrams(words)]
    titletrigrams = [ngram_sep.join(i) for i in nltk.trigrams(words)]

    lastnames = ["author_"+i.split(",")[0].strip().lower() for i in p.author.split(";")]

    feats = titleunigrams + titlebigrams + titletrigrams + lastnames #+ get_ft_ngrams(p.pid)

    feats.append("Venue_"+p.pid[0])
    initfeats[p.pid] = feats
    for i in feats:
        if(i not in featfreq):
            featfreq[i] = 0
        featfreq[i] += 1
        
upperbound = math.ceil(len(refpapers) * 0.98)
lowerbound = math.ceil(len(refpapers) * 0.02)

prunedfeats = [i for i in featfreq.keys() if (featfreq[i]) <= upperbound and (featfreq[i] >= lowerbound)]
prunedfeats = featfreq.keys()

print "Using %d final features" % len(prunedfeats);

for pid in initfeats.keys():
    finalfeats = [f for f in initfeats[pid] if f in prunedfeats]
    feat_file.write(str(pid)+"\t"+'<>'.join(finalfeats)+"\n")

feat_file.close()
