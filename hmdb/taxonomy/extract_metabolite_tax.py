#!/usr/bin/env python

"""
Extracts metabolite taxonomy (kingdom, super class, class, sub class) from the HMDB all 
metabolites XML file and dumps it in tab seperated format

Take care: some metabolite names can not be represented in ASCII. One way to get 
around this limitation is to use UTF8 for input/output encoding. This can be easily achieved 
by setting the environment variable PYTHONIOENCODING to UTF8 (on BASH use: export PYTHONIOENCODING=UTF8)  
"""

import sys
from xml.sax import handler, make_parser


class HMDBMetabolite(object):
    def __init__(self):
        self.accession = None
        self.name = None
        self.kingdom = None
        self.super_clazz = None
        self.clazz = None
        self.sub_clazz = None

        

class HMDBMetaboliteContentHandler(handler.ContentHandler):
    def __init__(self, new_metabolite_callback):
        handler.ContentHandler.__init__(self)
        self.path = list()
        self.char_buffer = None
        self.current_metabolite = None
        self.new_metabolite_callback = new_metabolite_callback

        
    def startElement(self, name, attrs):
        self.path_append(name)
        if self.is_current_path("hmdb", "metabolite"):
            self.handle_metabolite(True)
        elif self.is_current_path("hmdb", "metabolite", "accession"):
            self.handle_text_property(True, self.current_metabolite, "accession")
        elif self.is_current_path("hmdb", "metabolite", "name"):
            self.handle_text_property(True, self.current_metabolite, "name")
        elif self.is_current_path("hmdb", "metabolite", "taxonomy", "kingdom"):
            self.handle_text_property(True, self.current_metabolite, "kingdom")
        elif self.is_current_path("hmdb", "metabolite", "taxonomy", "super_class"):
            self.handle_text_property(True, self.current_metabolite, "super_clazz")
        elif self.is_current_path("hmdb", "metabolite", "taxonomy", "class"):
            self.handle_text_property(True, self.current_metabolite, "clazz")
        elif self.is_current_path("hmdb", "metabolite", "taxonomy", "sub_class"):
            self.handle_text_property(True, self.current_metabolite, "sub_clazz")
        
            
    def endElement(self, name):
        if self.is_current_path("hmdb", "metabolite"):
            self.handle_metabolite(False)
        elif self.is_current_path("hmdb", "metabolite", "accession"):
            self.handle_text_property(False, self.current_metabolite, "accession")
        elif self.is_current_path("hmdb", "metabolite", "name"):
            self.handle_text_property(False, self.current_metabolite, "name")
        elif self.is_current_path("hmdb", "metabolite", "taxonomy", "kingdom"):
            self.handle_text_property(False, self.current_metabolite, "kingdom")
        elif self.is_current_path("hmdb", "metabolite", "taxonomy", "super_class"):
            self.handle_text_property(False, self.current_metabolite, "super_clazz")
        elif self.is_current_path("hmdb", "metabolite", "taxonomy", "class"):
            self.handle_text_property(False, self.current_metabolite, "clazz")
        elif self.is_current_path("hmdb", "metabolite", "taxonomy", "sub_class"):
            self.handle_text_property(False, self.current_metabolite, "sub_clazz")

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


    def handle_metabolite(self, start):
        if start:
            assert(self.current_metabolite == None)
            self.current_metabolite = HMDBMetabolite()
        else:
            assert(self.current_metabolite != None)
            self.new_metabolite_callback(self.current_metabolite)
            self.current_metabolite = None


    def handle_text_property(self, start, target, name):
        if start:
            self.start_character_capturing()
        else:
            assert(getattr(target, name) == None)
            setattr(target, name, self.stop_character_capturing())
 
            
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
        print >>sys.stderr, "USAGE {} hmdb_metabolites.xml".format(sys.argv[0])
        sys.exit(1)

    fn_metabolites = sys.argv[1]
    
    header = ["accession", "name", "kingdom", "super_class", "class", "sub_class"]
    def dump_metabolite_tax(metabolite):
        ele = [
            metabolite.accession,
            metabolite.name,
            metabolite.kingdom, 
            metabolite.super_clazz,
            metabolite.clazz,
            metabolite.sub_clazz
            ]

        ele = map(lambda _: _ if _ != None else "", ele)
        ele = map(lambda _: _.replace("\t", " ").replace("\n", " ").replace("\r", ""), ele)
        print "\t".join(ele)

    parser = make_parser()
    parser.setContentHandler(HMDBMetaboliteContentHandler(dump_metabolite_tax))
    print "\t".join(header)
    parser.parse(fn_metabolites)
    

if __name__ == "__main__":
    main()
