#!/usr/bin/python

import sys
import subprocess

class ClairlibNw:

    @classmethod
    def from_edges(cls, edges):
        fname = 'tempnw.txt'
        tempfile = open('tempnw.txt', "w")
        for e in edges:
            tempfile.write(e[0]+"\t"+e[1]+"\n")
        tempfile.close()

        return cls(fname)


    
    def __init__(self, infile, delim = "\t", undirected = False):
        self.indicators = {}

        try:
            clairlib_cmd = ['print_network_stats.pl', '-i', infile, '--delim', delim, '--all']
            out, err = subprocess.Popen(clairlib_cmd, stdout=subprocess.PIPE).communicate()
        except:
            return

        deg_mode = "in_deg"
        for line in out.splitlines():
            line = line.strip()
            values = line.split(": ")

            # set degree mode here
            if "in degree stats" in line:
                deg_mode = "in_deg"
            elif "out degree stats" in line:
                deg_mode = "out_deg"
            elif "total degree stats" in line:
                deg_mode = "total_deg"

            if len(values) < 2 or line.startswith("Note:") or line.startswith("Network information:"):
                continue;

            if("r-squared" in line or "error" in line):
                value = None;
            else:
                value = float(values[1])

            if "nodes" in line:
                self.indicators["nodes"] = value
            elif "edges" in line:
                self.indicators["edges"] = value
            elif "average degree" in line:
                self.indicators["average_degree"] = value
            elif "largest connected component size" in line:
                self.indicators["largest_connected_comp_size"] = value
            elif "diameter" in line:
                self.indicators["diameter"] = value
            elif "Watts Strogatz clustering coefficient" in line:
                self.indicators["ws_clustering"] = value
            elif "Newman clustering coefficient" in line:
                self.indicators["newman_clustering"] = value
            elif "harmonic mean geodesic distance:" in line:
                self.indicators["harmonic_mean_geodesic_distance"] = value
            elif "Strongly connected components" in line:
                self.indicators["strongly_connected_components"] = value
            elif "clairlib avg. directed shortest path" in line:
                self.indicators["clairlib_avg_shortest_path"] = value
            elif "Ferrer avg. directed shortest path" in line:
                self.indicators["ferrer_avg_shortest_path"] = value
            elif "clairlib avg. undirected shortest path" in line:
                self.indicators["clairlib_avg_shortest_path"] = value
            elif "Ferrer avg. undirected shortest path" in line:
                self.indicators["ferrer_avg_shortest_path"] = value
            elif "full average shortest path" in line:
                self.indicators["full_avg_shortest_path"] = value
            elif "Assortativity" in line:
                self.indicators["assortativity"] = value

            # handle degree indicators

            if "power law exponent" in line:
                prefix = "_newman" if "Newman" in line else ""
                parts = values[1].split(" ");
                power_law_exp = parts[0].replace(",", "")

                self.indicators[deg_mode+prefix+"_power_law_exp"] = float(power_law_exp)
                self.indicators[deg_mode+prefix+"_r_squared"] = float(values[2])

        nodes = self.indicators['nodes']
        edges = self.indicators['edges']
        self.indicators['density'] = edges/(nodes * (nodes-1)) if nodes > 1 else 0

        self.indicators['betweenness'] = self.get_centralities(infile+".betweenness-centrality")
        self.indicators['closeness'] = self.get_centralities(infile+".betweenness-centrality")
        self.indicators['degree'] = self.get_centralities(infile+".degree-centrality")
        self.indicators['lexrank'] = self.get_centralities(infile+".lexrank-centrality")

    def get_centralities(self, fname):
        cents = {}
        cent_file = open(fname, "r")
        for line in cent_file:
            (pid, cent) = line.strip().split(" ")
            cents[pid] = cent

        return cents

if(__name__ == "__main__"):
    if len(sys.argv) < 2:
        print "Usage %s <input file> [<delim>]" % sys.argv[0]

    else:
        
        if len(sys.argv) > 2:
            cl = ClairlibNw(sys.argv[1], sys.argv[2])
        else:
            cl = ClairlibNw(sys.argv[1])
        for i in cl.indicators.keys():
            print "%s:%.3f" % (i, cl.indicators[i])
        
