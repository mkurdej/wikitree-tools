#!/usr/bin/env python

import gedcom
import sys

if len(sys.argv) not in (2,3):
    print 'usage: graph_gedcom.py in.ged [name]'
    exit(1)
    

g = gedcom.Gedcom(sys.argv[1])
llg = gedcom.LineageLinkedGedcom(g)


root = None

if len(sys.argv) == 3:
    root_name = sys.argv[2]
    for i in llg.individuals:
        if i.isName(root_name):
            root = i
            break
        

def print_record(r):
    print '\t'+r.xref_id[1:-1],
    if r.xref_id[1] == 'I':
        print '[label="'+str(r.records['NAME'][0])+'", ',
        if r.getValue('SEX') == 'M':
            print 'color=Blue, shape=box]'
        else:
            print 'color=Pink, shape=box]'
        f = r.getValue('FAMC')
        if f is not None:
            print '\t'+f.xref_id[1:-1],'->',r.xref_id[1:-1]
    else:
        print
        if r.getValue('HUSB') is not None:
            print '\t'+r.getValue('HUSB').xref_id[1:-1],'->',r.xref_id[1:-1]
        if r.getValue('WIFE') is not None:
            print '\t'+r.getValue('WIFE').xref_id[1:-1],'->',r.xref_id[1:-1]
    
        
print 'digraph g {'

if root is None:
    for k,v in llg.index.iteritems():
        print_record(v)
else:
    q = [root]
    seen = []
    while len(q):
        if not q[0] in seen:
            print_record(q[0])
            f = q[0].getValue('FAMC')
            if f is not None:
                if not f in seen:
                    q.append(f)
                    if f.getValue('HUSB') is not None:
                        if not f.getValue('HUSB') in seen:
                            q.append(f.getValue('HUSB'))
                    if f.getValue('WIFE') is not None:
                        if not f.getValue('WIFE') in seen:
                            q.append(f.getValue('WIFE'))
            seen.append(q[0])
        q = q[1:]
        
print '}'


