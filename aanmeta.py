#!/usr/bin/python

import sys
import re

class aanpaper:
    def __init__(self, pid, author = None, title = None, venue = None, year = None):
        self.pid = pid
        self.author = author
        self.title = title
        self.venue = venue
        self.year = year

    def __repr__(self):
        return "('%s','%s', '%s', '%s', '%s')" % (self.pid, self.title, self.venue, self.year, self.author)

class aanmeta:
    def __init__(self):
        metafile = "/data0/projects/aan/release/2012/acl-metadata.txt"
        self.metadata = []
        curobj = None
        try:
            infile = open(metafile, "r")
            for line in infile:
                line = line.strip()
                if(line.startswith("id = ")):
                    curobj = aanpaper(line[len("id = "):].replace("{", "").replace("}", "")) # take the string starting from where the "id =" string ends till the end of the line and then remove the braces
                    self.metadata.append(curobj)
                elif(line.startswith("author = ")):
                    curobj.author = line[len("author ="):].replace("{", "").replace("}", "").strip()
                elif(line.startswith("title = ")):
                    curobj.title = line[len("title ="):].replace("{", "").replace("}", "").strip()
                elif(line.startswith("venue = ")):
                    curobj.venue = line[len("venue ="):].replace("{", "").replace("}", "").strip()
                elif(line.startswith("year = ")):
                    curobj.year = int(line[len("year ="):].replace("{", "").replace("}", "").strip())
        except:
            print "Error while reading file:", sys.exc_info()[0]
            sys.exit(1)
        finally:
            infile.close()

        self.metadata_hash = {i.pid: i for i in self.metadata}
        
            
    def get_restricted_papers(self, lyear, hyear):
        """Accepts a lower and upper bound on years.

        Returns papers within these years from the four venues, ACL, NAACL, EACL and HLT excluding workshop papers as described in Yogatama et al., 2009
        """
        retpapers = []

        acl_regex = re.compile("(ACL|Association For Computational Linguistics)", re.IGNORECASE)
        naacl_regex = re.compile("(NAACL|North American (Chapter of the )?Association for Computational Linguistics)", re.IGNORECASE)
        eacl_regex = re.compile("(EACL|European Association For Computational Linguistics)", re.IGNORECASE)
        hlt_regex = re.compile("(HLT|Human Language Technolog)", re.IGNORECASE)
        workshop_regex = re.compile("Workshop", re.IGNORECASE)

        for p in self.metadata:
            ven = p.venue
            if((acl_regex.search(ven) or naacl_regex.search(ven) or eacl_regex.search(ven) or hlt_regex.search(ven)) 
               and (not workshop_regex.search(ven))):
                retpapers.append(p)

        return [p for p in retpapers if p.year >= lyear and p.year <= hyear]


# t = aanmeta()
# for p in t.get_restricted_papers():
#                    print p.pid + "\t" + p.venue
