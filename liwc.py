#!/usr/bin/python

import nltk
import re

class Matcher:
    def __init__(self, matchstr, ids):
        
        matchstr = "^"+matchstr.replace("*", ".*")+"$"
        self.regex = re.compile(matchstr, flags=re.IGNORECASE)
        self.ids = ids

    def ismatch(self, word):
        return True if self.regex.match(word) else False

class Liwc:
    def __init__(self):
        self.id_to_name = {}
        self.matchers = []

        cat_file = open("./liwccat_restricted.txt", "r")
        for line in cat_file:
            (cid, cdesc) = line.strip().split("\t")
            cdesc = cdesc.replace(" ", "_")
            self.id_to_name[cid] = cdesc

        dict_file = open("/data0/corpora/liwc/liwcdic2007.dic", "r")
        for line in dict_file:
            parts = line.strip().split("\t")

            matchstr = parts[0]
            cids = [i for i in parts[1:] if i in self.id_to_name]
            self.matchers.append(Matcher(matchstr, cids))


    def get_classes(self, tokens):
        classes = {}
        for t in tokens:
            for m in self.matchers:
                if(m.ismatch(t)):
                    for i in m.ids:
                        idstr = self.id_to_name[i]
                        if idstr not in classes:
                            classes[idstr] = []    
                    
                        classes[idstr].append(t)

        return classes


if(__name__ == "__main__"):
    liwc = Liwc()
    print liwc.get_classes(nltk.word_tokenize("I am glad to acknowledge your success and I will tell you to shut up."))
    print liwc.get_classes(nltk.word_tokenize("I am terribly dissapointed in your failures."))
