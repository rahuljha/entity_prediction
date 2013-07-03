#!/usr/bin/python

from __future__ import division # makes integer divison floating point

from utils import get_year_from_id;

class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class EdgeError(Error):
    def __init__(self, msg):
        self.msg = msg
        pass

class citation_edge:
    def __init__(self, edge):
        if(len(edge) != 2):
            raise EdgeError("Found anomalous number of elements (%s) in list" % len(edge))
        self.citing = edge[0]
        self.cited = edge[1]

    def __repr__(self):
        return "%s -> %s" % (self.citing,self.cited)

class CitationNetwork:
    def __init__(self):
        self.network = []

        cnw_file = "/data0/projects/aan/release/2012/acl.txt"
        

        try:
            infile = open(cnw_file, "r")
            for line in infile:
                line = line.strip()
                edge = line.split(" ==> ")
                try:
                    self.network.append(citation_edge(edge)) # since we want edges to be immutable
                except EdgeError as e:
                    print "Error while reading edge: " + e.msg;
                    continue
        except:
            print "Error while reading file:", sys.exc_info()[0]
            sys.exit(1)
        finally:
            infile.close()

    def get_citing(self, pid):
        return [edge.citing for edge in self.network if edge.cited == pid]
    
    def get_cited(self, pid):
        return [edge.cited for edge in self.network if edge.citing == pid]

    def get_cited_projection(self, pid):
        cited = self.get_cited(pid)
        return self.citation_projection(cited)

    def get_cited_projection_self_included(self, pid):
        cited = self.get_cited(pid)
        cited.append(pid)
        return self.citation_projection(cited)

    def if_cited_first_n_years(self, pid_in, n):
        citing_ids = self.get_citing(pid_in)
        lags = [get_year_from_id(pid) - get_year_from_id(pid_in) for pid in citing_ids]
        lags.sort()
        if(len(lags) > 0):
            return (lags[0] < n)
        else:
            return False

    def get_prominence(self, pid, ref, fc):
        citing_ids = self.get_citing(pid)
        cr = len([cid for cid in citing_ids if (get_year_from_id(cid) <= ref)])
        fr = len([cid for cid in citing_ids if (get_year_from_id(cid) <= fc)])

        if(fr < cr):
            return -1
        elif(fr >= cr and fr < 1):
            return 0
        else:
            return ((1 - cr/fr)*(1-1/fr))

    def citation_projection(self, pids):
        # if takes too long, optimize using hashes
        projection = [i for i in self.network if i.citing in pids and i.cited in pids]
        return projection

if __name__ == "__main__":
    cnw = CitationNetwork()
    print cnw.get_prominence('P01-1069', 2002, 2003)
    print cnw.get_prominence('P01-1069', 2002, 2004)
    print cnw.get_prominence('P98-2247', 2001, 2003)
    print cnw.citation_projection(['J04-4002', 'J93-2003', 'J97-3002', 'N03-1017', 'N04-1033'])
    print cnw.get_cited('P05-1033')
    print cnw.get_cited_projection('P05-1033')
    print cnw.get_cited_projection_self_included('P05-1033')
