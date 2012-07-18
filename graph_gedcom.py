#!/usr/bin/env python

import gedcom
import sys

g = gedcom.Gedcom(sys.argv[1])
llg = gedcom.LineageLinkedGedcom(g)

print 'digraph g {'
for k,v in llg.index.iteritems():
    print '\t'+k[1:-1],
    if k[1] == 'I':
        print '[label="'+str(v.records['NAME'][0])+'", ',
        if v.getValue('SEX') == 'M':
            print 'color=Blue, shape=box]'
        else:
            print 'color=Pink, shape=box]'
        f = v.getValue('FAMC')
        if f is not None:
            print '\t'+k[1:-1],'->',f.xref_id[1:-1]
    else:
        print
        if v.getValue('HUSB') is not None:
            print k[1:-1],'->',v.getValue('HUSB').xref_id[1:-1]
        if v.getValue('WIFE') is not None:
            print k[1:-1],'->',v.getValue('WIFE').xref_id[1:-1]
        
print '}'


	