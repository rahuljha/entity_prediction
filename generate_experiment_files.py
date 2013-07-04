#!/usr/bin/python

import sys
import random
import math
import json
import re

from aanmeta import aanmeta
from citation_nw import CitationNetwork
from utils import get_year_from_id
from network_features import CitationNetworkFeatures

from subprocess import Popen, PIPE

class BuildExperiment:

    def __init__(self):
        self.aan = aanmeta()
        self.cnw = CitationNetwork()

        self.prestige_features = {}
        self.position_features = {}
        self.content_features = {}
        self.style_features = {}

        self.load_features()

    def write_features(self, tyear):

        all_papers = [p for p in self.aan.get_restricted_papers(1980, tyear)]
        train_normal = [p.pid for p in all_papers if p.year <= (tyear-3)]
        train_ext_1 = [p.pid for p in all_papers if p.year == (tyear-1)]
        train_ext_2 = [p.pid for p in all_papers if p.year == (tyear-2)]
        test= [p.pid for p in all_papers if p.year == tyear]

        # write feature files
        ft_types = {"prestige": self.prestige_features,
                    "position": self.position_features,
                    "content": self.content_features,
                    "style": self.style_features
                    }

        experiment_combs = [["prestige"],
                            ["prestige", "position"],
                            ["prestige", "content"],
                            ["prestige", "position", "content"],
                            ["prestige", "style"],
                            ["prestige", "content", "style"],
                            ["prestige", "content", "style", "position"],
                            ]

        for comb in experiment_combs:
            print "Writing %s features" % str(comb)
            trainfile = open("experiment_files/train_feat."+str(tyear)+"."
                             +"_".join([i[0:2] for i in comb])+".txt", "w")
            for pid in train_normal+train_ext_1 + train_ext_2: # join these since there is no difference in terms of features
                # dict(dict1.items()+dic2.items()) merges two dictionaries; reduce adds all the feature dictionaries in the comb
                features = dict(reduce(lambda x,y: x+y, [ft_types[c][pid].items() for c in comb if pid in ft_types[c]]))
                trainfile.write(pid+"\t"+json.dumps(features)+"\n")
            trainfile.close()
            print "Finished training features"
                
            testfile = open("experiment_files/test_feat."+str(tyear)+"."
                             +"_".join([i[0:2] for i in comb])+".txt", "w")
            for pid in test: 
                features = dict(reduce(lambda x,y: x+y, [ft_types[c][pid].items() for c in comb if pid in ft_types[c]]))
                testfile.write(pid+"\t"+json.dumps(features)+"\n")                
            testfile.close()
            print "Finished test features"

            normal_train_labels = {pid: self.cnw.if_cited_first_n_years(pid, 3) for pid in train_normal}
            ext_1_labels = self.get_ext_labels(train_ext_1, train_normal, 1)
            ext_2_labels = self.get_ext_labels(train_ext_2, train_normal, 2)
            training_labels = dict(normal_train_labels.items() + ext_1_labels.items() + ext_2_labels.items())
            test_labels = {pid: self.cnw.if_cited_first_n_years(pid, 3) for pid in test}

            train_label_f = open("experiment_files/train_resp."+str(tyear)+".txt", "w")
            for (pid,label) in training_labels.items():
                train_label_f.write("%s\t%s\n" % (pid, str(label)))
            train_label_f.close()

            test_label_f = open("experiment_files/test_resp."+str(tyear)+".txt", "w")
            for (pid,label) in test_labels.items():
                test_label_f.write("%s\t%s\n" % (pid, str(label)))
            test_label_f.close()

    
    def get_ext_labels(self, train_ext, train_normal, n):
        gold = 3
        ratios = []
        for pid in train_normal:
            cits_3 = self.cnw.citations_first_n_years(pid, 3)
            cits_n = self.cnw.citations_first_n_years(pid, n)
            if cits_3 > 0:
                ratios.append(cits_n/float(cits_3))
        mult =  sum(ratios) / len(ratios)

        ret_labels = {}
        for pid in train_ext:
            ret_labels[pid] = True if math.ceil(self.cnw.citations_first_n_years(pid, n) / mult) > 1 else False
        return ret_labels

    def load_features(self):
        print "Loading base features ..."
        self.load_base_features()
        print "Loading ft ngram features ..."
        self.load_ft_features()
        print "Loading cited sentiment/purpose features ..."
        self.load_amjad_features()
        print "Loading liwc features ..."
        self.load_liwc_features()
        print "Loading cited network features ..."
        self.load_network_features()
        print "Loading lexical network features ..."
        self.load_lexical_features()
    def load_network_features(self):

        nw_file = open("/data0/projects/fuse/entity_prediction/features_cache/citednw_features_cache.txt", "r")
        for line in nw_file:
            items = line.strip().split(";")
            pid = items[0]

            if not pid in self.position_features:
                self.position_features[pid] = {}

            for item in items[1:]:
                (feat, value) = item.split(":")
                self.position_features[pid][feat] = float(value)
        
    def load_liwc_features(self):
        
        liwc_file = open("/data0/projects/fuse/entity_prediction/features_cache/wordclass_features_cache.txt", "r")
        for line in liwc_file:
            items = line.strip().split(";")
            pid = items[0]

            if not pid in self.style_features:
                self.style_features[pid] = {}

            for item in items[1:]:
                if item == "":
                    continue
                (feat, value) = item.split(":")
                self.style_features[pid][feat] = float(value)
            

    def load_base_features(self):
        # get author, venue, institution and term features
        for p in self.aan.metadata:
            authors = ["author_"+str(i.authorid) for i in p.authors]
            insts = ["inst_"+str(i.instid) for i in p.institutions]

            pid = p.pid

            if pid not in self.prestige_features:
                self.prestige_features[pid] = {}

            for a in authors:
                self.prestige_features[pid][a] = 1
            for i in insts:
                self.prestige_features[pid][i] = 1 # add inst so that features won't be mixed up

            self.prestige_features[pid]["Venue_"+p.pid[0]] = 1

            if pid not in self.content_features:
                self.content_features[pid] = {}

            for term in p.terms:
                self.content_features[pid][term.termid] = 1        

    def load_ft_features(self):
        # features from Yogatama's paper
        ngrams_file = open("features_cache/1980_2006.pruned_feats.ft", "r")
        
        for line in ngrams_file:
            (pid, featstr) = line.strip().split("\t")

            if pid not in self.content_features:
                self.content_features[pid] = {}

            feats = featstr.split("<>")
            
            venue_regex = re.compile("^Venue_")
            author_regex = re.compile("^author_")
            
            for f in feats:
                if(venue_regex.match(f) or author_regex.match(f)): # we have better venue and author features now, so ignore these
                    continue
                self.content_features[pid][f] = 1

    def load_amjad_features(self):
        # features from Amjad's code
        position_cit_features = ["positive_outgoing_citation_cnt",  "negative_outgoing_citation_cnt",  "neutral_outgoing_citation_cnt",  "criticizing_outgoing_citation_cnt",  "comparison_outgoing_citation_cnt",  "use_outgoing_citation_cnt",  "substantiating_outgoing_citation_cnt",  "basis_outgoing_citation_cnt",  "other_outgoing_citation_cnt"]

        amjad_file = open("features_cache/amjad_features_cache.txt", "r")
        for line in amjad_file:
            items = line.strip().split(";")
            pid = items[0]

            if pid not in self.position_features:
                self.position_features[pid] = {}
            
            feat_hash = {}
            for item in items[1:]:
                (feat,val) = item.split(":")
                feat_hash[feat] = float(val)

            total_out = feat_hash['outgoing_citation_cnt'] if 'outgoing_citation_cnt' in feat_hash else 0
            for i in position_cit_features:
                if i in feat_hash:
                    self.position_features[pid][i] = feat_hash[i]/total_out if total_out > 0 else 0

    def load_lexical_features(self):
        # features from lexical code

        papers = [p.pid for p in self.aan.get_restricted_papers(1980, 2011)]
        position_lex_features = ["lexrank_same_year", "lexrank_prev_year",  "min_sim_cited",  "max_sim_cited",  "avg_sim_cited",  # from lexrank file
                                 "min_sim_same_year",  "max_sim_same_year",  "avg_sim_same_year",  "min_sim_prev_year",  "max_sim_prev_year",  "avg_sim_prev_year",  # from sim file
                                 "min_title_term_weight",  "max_title_term_weight",  "avg_title_term_weight",  "title_term_density",  # from title term
                                 "min_abs_term_weight",  "max_abs_term_weight",  "avg_abs_term_weight",  "abs_term_density" # from abs term
                                 ]

        for pid in papers:
            if pid not in self.position_features:
                self.position_features[pid] = {}

            lf_string = Popen(["perl", "../citation_prediction/get_lexical_features.pl", pid, "0"], stdout=PIPE).communicate()[0]
            items = lf_string.strip().split("\t");
            items = items[1:] # remove the pid
            if len(items) < 19: # this means features weren't calculated
                continue

            for i,name in enumerate(position_lex_features):
                try:
                    self.position_features[pid][name] = float(items[i])
                except:
                    self.position_features[pid][name] = 0
    
if(__name__ == "__main__"):
    year = sys.argv[1]
    be = BuildExperiment()
    be.write_features(int(year))
    print "done"
