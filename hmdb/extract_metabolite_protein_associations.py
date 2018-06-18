#!/usr/bin/env python

"""
Extracts metabolite protein associations from the HMDB all proteins XML file and dumps them in tab seperated format

Take care: some metabolite names can not be represented using only ASCII. One way to get around this limitation is to use UTF8 for input/output encoding. This can be easily achieved by setting the environment variable PYTHONIOENCODING to UTF8 (on BASH use: export PYTHONIOENCODING=UTF8)  
"""

import sys
from xml.sax import saxutils, handler, make_parser


class HMDBMetabolite(object):
    def __init__(self):
        self.accession = None
        self.name = None

        
        
class HMDBProtein(object):
    def __init__(self):
        self.accession = None
        self.gene_name = None
        self.uniprot_id = None
        self.metabolites = list()

        

class HMDBProteinContentHandler(handler.ContentHandler):
    def __init__(self, new_protein_callback):
        handler.ContentHandler.__init__(self)
        self.path = list()
        self.char_buffer = None
        self.current_protein = None
        self.current_metabolite = None
        self.new_protein_callback = new_protein_callback

        
    def startElement(self, name, attrs):
        self.path_append(name)
        if self.is_current_path("hmdb", "protein"):
            self.handle_protein(True)
        elif self.is_current_path("hmdb", "protein", "gene_name"):
            self.handle_gene_name(True)
        elif self.is_current_path("hmdb", "protein", "accession"):
            self.handle_accession(True)
        elif self.is_current_path("hmdb", "protein", "uniprot_id"):
            self.handle_uniprot_id(True)
        elif self.is_current_path("hmdb", "protein", "metabolite_associations", "metabolite"):
            self.handle_metabolite(True)
        elif self.is_current_path("hmdb", "protein", "metabolite_associations", "metabolite", "accession"):
            self.handle_metabolite_accession(True)
        elif self.is_current_path("hmdb", "protein", "metabolite_associations", "metabolite", "name"):
            self.handle_metabolite_name(True)

            
    def endElement(self, name):
        if self.is_current_path("hmdb", "protein"):
            self.handle_protein(False)
        elif self.is_current_path("hmdb", "protein", "gene_name"):
            self.handle_gene_name(False)
        elif self.is_current_path("hmdb", "protein", "accession"):
            self.handle_accession(False)
        elif self.is_current_path("hmdb", "protein", "uniprot_id"):
            self.handle_uniprot_id(False)
        elif self.is_current_path("hmdb", "protein", "metabolite_associations", "metabolite"):
            self.handle_metabolite(False)
        elif self.is_current_path("hmdb", "protein", "metabolite_associations", "metabolite", "accession"):
            self.handle_metabolite_accession(False)
        elif self.is_current_path("hmdb", "protein", "metabolite_associations", "metabolite", "name"):
            self.handle_metabolite_name(False)

        self.path_pop(name)

        
    def characters(self, content):
        if self.char_buffer != None:
            self.char_buffer.append(content)

            
    def start_character_capturing(self):
        assert(self.char_buffer == None)
        self.char_buffer = list()

        
    def stop_character_capturing(self):
        assert(self.char_buffer != None)
        content = "".join(self.char_buffer)
        self.char_buffer = None
        return content

    
    def handle_protein(self, start):
        if start:
            assert(self.current_protein == None)
            self.current_protein = HMDBProtein()
        else:
            assert(self.current_protein != None)
            self.new_protein_callback(self.current_protein)
            self.current_protein = None

            
    def handle_gene_name(self, start):
        if start:
            self.start_character_capturing()
        else:
            assert(self.current_protein.gene_name == None)
            self.current_protein.gene_name = self.stop_character_capturing()

            
    def handle_accession(self, start):
        if start:
            self.start_character_capturing()
        else:
            assert(self.current_protein.accession == None)
            self.current_protein.accession = self.stop_character_capturing()

            
    def handle_uniprot_id(self, start):
        if start:
            self.start_character_capturing()
        else:
            assert(self.current_protein.uniprot_id == None)
            self.current_protein.uniprot_id = self.stop_character_capturing()

            
    def handle_metabolite(self, start):
        if start:
            assert(self.current_metabolite == None)
            self.current_metabolite = HMDBMetabolite()
        else:
            assert(self.current_metabolite != None)
            self.current_protein.metabolites.append(self.current_metabolite)
            self.current_metabolite = None


    def handle_metabolite_accession(self, start):
        if start:
            self.start_character_capturing()
        else:
            assert(self.current_metabolite.accession == None)
            self.current_metabolite.accession = self.stop_character_capturing()


    def handle_metabolite_name(self, start):
        if start:
            self.start_character_capturing()
        else:
            assert(self.current_metabolite.name == None)
            self.current_metabolite.name = self.stop_character_capturing()
 
            
    def path_append(self, ele):
        self.path.append(ele)

        
    def path_pop(self, name = None):
        assert(len(self.path) > 0)
        last_ele = self.path.pop()
        assert(name == None or last_ele == name)

        
    def equal_path(self, path_ele_a, path_ele_b):
        if len(path_ele_a) == len(path_ele_b):
            for i in reversed(range(0, len(path_ele_b))):
                if path_ele_a[i] != path_ele_b[i]:
                    return False

            return True

        return False

    
    def is_current_path(self, *path_ele):
        return self.equal_path(self.path, path_ele)
    


def main():
    if len(sys.argv) != 2:
        print >>sys.stderr, "USAGE {} hmdb_proteins.xml".format(sys.argv[0])
        sys.exit(1)

    fn_proteins = sys.argv[1]
    
    def dump_protein_info(prot):
        for m in prot.metabolites:
            print "\t".join( (prot.accession, prot.uniprot_id, prot.gene_name, m.accession, m.name) )

        if len(prot.metabolites) == 0:
            print "\t".join( (prot.accession, prot.uniprot_id, prot.gene_name, "", "") )
        
    parser = make_parser()
    parser.setContentHandler(HMDBProteinContentHandler(dump_protein_info))
    print "\t".join(["prot_hmdb_acc", "prot_uniprot_acc", "prot_gene_name", "metabo_acc", "metabo_name"])
    parser.parse(fn_proteins)
    

if __name__ == "__main__":
    main()
