#!/usr/bin/python

import sys
import random
import math
import json
from subprocess import Popen, PIPE

from aanmeta import aanmeta
from citation_nw import CitationNetwork
from utils import get_year_from_id
from network_features import CitationNetworkFeatures

class create_data:

    def __init__(self):
        self.cnw_feat = CitationNetworkFeatures()

    def main(self):

        n = int(sys.argv[1])
        diff = sys.argv[2] if len(sys.argv) > 2 else 3

        init = 1980
        last = 2006

        aan = aanmeta()
        all_papers = aan.get_restricted_papers(init, last)
        
        till_n = [p for p in all_papers if p.year <= n]
    
        training = random.sample(till_n, int(math.ceil(0.8 * len(till_n))))
        model_test = [i for i in till_n if i not in training]
        test = [i for i in all_papers if i.year == (n+diff)]

        print "Total files: %d" % (len(training)+len(model_test)+len(test))

        self.feats = {}
        featfile = open("1980_2006.pruned_feats", "r")
        for line in featfile:
            line = line.strip()
            [pid, featstr] = line.split("\t")
            self.feats[pid] = featstr.split("<>")

        training_fname = "experiment_files/1980_%s.train.txt" % n
        model_test_fname = "experiment_files/1980_%s.modeltest.txt" % n
        test_fname = "experiment_files/%s.test.txt" % (n+diff)

        self.write_data(training, training_fname)
        self.write_data(model_test, model_test_fname)
        self.write_data(test, test_fname)

        # creating the response files 
        self.cnw = CitationNetwork()
        training_resp_file = open("experiment_files/1980_%s.train.resp.txt" % n, "w")
        model_test_resp_file = open("experiment_files/1980_%s.modeltest.resp.txt" % n, "w")
        test_resp_file = open("experiment_files/%s.test.resp.txt" % (n+diff), "w")
        self.write_response(training, training_resp_file, n)
        self.write_response(model_test, model_test_resp_file, n)
        self.write_response(test, test_resp_file, n)

        # write the time step files
        ts_file = open("experiment_files/%s_%s_timesteps.txt" % (init, n), "w")
        for pid in [i.pid for i in all_papers if i.year >= init and i.year <= n]:
            ts_file.write("%s\t%d\n" % (pid, get_year_from_id(pid)))
            

    def get_lex_features(self, pid):
        features = {}
#        features_str = Popen(["perl", "../citation_prediction/get_lexical_features.pl", pid, str(get_year_from_id(pid))], stdout=PIPE).communicate()[0]
        features_str = Popen(["perl", "../citation_prediction/get_lexical_features.pl", pid, "0"], stdout=PIPE).communicate()[0]
        for idx,feat in enumerate(features_str.split("\t")[1:]):
            try:
                features["lf_"+str(idx)] = float(feat)
            except:
                features["lf_"+str(idx)] = 0.0
        return features
    
    def write_data(self, pobjs, data_fname):
        pids = [p.pid for p in pobjs]
        dataout = open(data_fname, "w")
#       dataout_nw = open(data_fname+".nw", "w")
#        dataout_nwlex = open(data_fname+".nwlex", "w")
        dataout_lex = open(data_fname+".lex", "w")

        for pid in pids:
            print pid
            sys.stdout.flush()
            out = {feat:1 for feat in self.feats[pid]}
            lex =  self.get_lex_features(pid)
#            nw = self.cnw_feat.cited_nw_features(pid)
#            out_nw =  dict(out.items() + nw.items())
#            out_nw_lex = dict(out.items() + nw.items() +lex.items())
            out_lex = dict(out.items() + lex.items())
            try:
                jsonout = json.dumps(out)
                jsonout_lex = json.dumps(out_lex)
#               jsonout_nw = json.dumps(out_nw)
#                jsonout_nwlex = json.dumps(out_nw_lex)
            except(UnicodeDecodeError):
                print "error with "+str(out)
                continue

            dataout.write(pid+"\t"+jsonout+"\n")
            dataout_lex.write(pid+"\t"+jsonout_lex+"\n")
#            dataout_nw.write(pid+"\t"+jsonout_nw+"\n")
#            dataout_nwlex.write(pid+"\t"+jsonout_nwlex+"\n")

        dataout.close()
#        dataout_nw.close()
#        dataout_nwlex.close()
        dataout_lex.close()

    def write_response(self, pobjs, outfile, n=0):
        pids = [p.pid for p in pobjs]
        for pid in pids:
            outfile.write("%s\t%s\n" % (pid, self.cnw.if_cited_first_n_years(pid, 3)))
#            outfile.write("%s\t%s\n" % (pid, self.cnw.get_prominence(pid, n, n+3)))


if __name__ == '__main__':
    cd = create_data()
    cd.main()
