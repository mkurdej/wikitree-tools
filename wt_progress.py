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

www_missing = []

print '<html><body>'

while cur_gen < len(generations):
    for i in generations[cur_gen]:
        f = i.getValue('FAMC')
        if f is None:
            print cur_gen, 
            if i.get('WWW') is not None:
                print '<a href="'+i.get('WWW').value+'">'+i.get('WWW').value+'</a>',
            print '\t'+str(i.get('NAME')),'missing parents<br>'
        else:
            if len(generations) <= cur_gen+1:
                generations.append([])
            if f.getValue('HUSB') is None:
                print cur_gen, 
                if i.get('WWW') is not None:
                    print '<a href="'+i.get('WWW').value+'">'+i.get('WWW').value+'</a>',
                print '\t',i.get('NAME'),'missing father<br>'
            else:
                generations[cur_gen+1].append(f.getValue('HUSB'))
                if f.getValue('HUSB').get('WWW') is None and (i ,f) not in www_missing:
                    www_missing.append((i,f))
            if f.getValue('WIFE') is None:
                print cur_gen,
                if i.get('WWW') is not None:
                    print '<a href="'+i.get('WWW').value+'">'+i.get('WWW').value+'</a>',
                print '\t',i.get('NAME'),'missing mother<br>'
            else:
                generations[cur_gen+1].append(f.getValue('WIFE'))
                if f.getValue('WIFE').get('WWW') is None and (i,f) not in www_missing:
                    www_missing.append((i,f))
    cur_gen += 1

for i,f in www_missing:
    print 'WWW\t', 
    if i.get('WWW') is not None:
        print '<a href="'+i.get('WWW').value+'">'+i.get('WWW').value+'</a>',
    if f.getValue('HUSB') is not None and f.getValue('HUSB').get('WWW') is None:
        print '\t',i.get('NAME'),'father is missing WWW link<br>'
    if  f.getValue('WIFE') is not None and f.getValue('WIFE').get('WWW') is None:
        print '\t',i.get('NAME'),'mother is missing WWW link<br>'


for i in range (len(generations)):
    print 'generation',i,'-',len(generations[i]),'of',2**i,'(',len(generations[i])*100/float(2**i),'%)<br>'

print '</body></html>'
