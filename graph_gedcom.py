#!/usr/bin/env python

import gedcom
import sys

g = gedcom.Gedcom(sys.argv[1])
llg = gedcom.LineageLinkedGedcom(g)

target = sys.argv[2]
root = None
for i in llg.individuals:
    if i.isName(target):
        root = i
        break
        
q = [root]

seen = []

print 'digraph g {'
while len(q):
    if not q[0] in seen:
        f = q[0].getValue('FAMC')

        if f is not None:
            if f.getValue('HUSB') is not None:
                print '"','\\n'.join(q[0].label().split('\n')),'" -> "','\\n'.join(f.getValue('HUSB').label().split('\n')),'";'
                q.append(f.getValue('HUSB'))
            if f.getValue('WIFE') is not None:
                print '"','\\n'.join(q[0].label().split('\n')),'" -> "','\\n'.join(f.getValue('WIFE').label().split('\n')),'";'
                q.append(f.getValue('WIFE'))
        seen.append(q[0])
    q = q[1:]
print '}'

	