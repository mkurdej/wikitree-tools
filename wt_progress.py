#!/usr/bin/env python

import gedcom
import sys

if len(sys.argv) != 3:
    print 'usage: wt_progress.py in.ged name'
    exit(1)
    

g = gedcom.Gedcom(sys.argv[1])
llg = gedcom.LineageLinkedGedcom(g)


root = None

root_name = sys.argv[2]
for i in llg.individuals:
    if i.isName(root_name):
        root = i
        break
        
if root is None:
    print 'individual not found:',root_name
    exit(1)

generations = [[root]]
cur_gen = 0

while cur_gen < len(generations):
    for i in generations[cur_gen]:
        f = i.getValue('FAMC')
        if f is None:
            print cur_gen, 
            if i.get('_URL') is not None:
                print i.get('_URL').value,
            print '\t'+str(i.get('NAME')),'missing parents'
        else:
            if len(generations) <= cur_gen+1:
                generations.append([])
            if f.getValue('HUSB') is None:
                print cur_gen, 
                if i.get('_URL') is not None:
                    print i.get('_URL').value,
                print '\t',i.get('NAME'),'missing father'
            else:
                generations[cur_gen+1].append(f.getValue('HUSB'))
            if f.getValue('WIFE') is None:
                print cur_gen,
                if i.get('_URL') is not None:
                    print i.get('_URL').value,
                print '\t',i.get('NAME'),'missing mother'
            else:
                generations[cur_gen+1].append(f.getValue('WIFE'))
    cur_gen += 1

for i in range (len(generations)):
    print 'generation',i,'-',len(generations[i]),'of',2**i,'(',len(generations[i])*100/float(2**i),'%)'
