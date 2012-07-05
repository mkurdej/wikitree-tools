#!/usr/bin/env python

import gedcom
import sys

g = gedcom.Gedcom(sys.argv[1])
llg = gedcom.LineageLinkedGedcom(g)

for i in llg.individuals:
    if i.url is not None:
        problems = []
        if i.sex is None:
            problems.append('sex not defined')
        for obj in i.objects:
            if obj.form == 'Message':
                if obj.text.lower().find('todo') != -1:
                    problems.append('todo found in message')
        if i.bio.text.lower().find('todo') != -1:
            problems.append('todo found in bio')
        if len(problems):
            print
            print '\n'.join(problems)
            print i
            for obj in i.objects:
                if obj.form == 'Message':
                    print obj
