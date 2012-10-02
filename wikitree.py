#!/usr/bin/env python

''' Module designed to be used with gedcom module to read wikitree exported data.
While generic GEDCOM functionality is contained in the gedcom module, this module is for
the details that are specific to wikitree data'''

import gedcom

handlers = gedcom.handlers.copy()

privacy_table = {'10':'Unlisted',
                 '20':'Private',
                 '30':'Private_public_bio',
                 '40':'Private_public_bio_and_tree',
                 '50':'Public',
                 '60':'Open'
                 }

class Gedcom(gedcom.LineageLinkedGedcom):
    def __init__(self,g):
        if type(g) == str:
            gedcom.LineageLinkedGedcom.__init__(self,gedcom.Gedcom(g),handlers)
        else:
            gedcom.LineageLinkedGedcom.__init__(self,g,handlers)

class IndividualRecord(gedcom.IndividualRecord):
    def __init__(self,rec,h):
        gedcom.IndividualRecord.__init__(self,rec,h)

        self.privacy_level = (0,'Unspecified') # not on trusted list?
        if self.reference_numbers.has_key('wikitree.privacy'):
            self.privacy_level = (int(self.reference_numbers['wikitree.privacy']),privacy_table[self.reference_numbers['wikitree.privacy']])

    def isPrivate(self):
        return self.privacy_level[0] > 0 and self.privacy_level[0] < 50

    def treeLabel(self,public=True):
        if public and self.privacy_level[0] > 0:
            if self.privacy_level[0] < 20:
                return None
            if self.privacy_level[0] < 50:
                return 'private'
        return self.label()
        

handlers['INDI'] = IndividualRecord
            

if __name__ == '__main__':
    import sys
    g = Gedcom(sys.argv[1])
    for i in g.individuals:
        print i.get('NAME'),i.privacy_level
        print i.treeLabel()
