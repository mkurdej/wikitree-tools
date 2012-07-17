#!/usr/bin/env python

import gedcom
import sys

if len(sys.argv) != 2:
    print 'usage: wt_lint.py gedcom.ged'
    exit(1)
    
g = gedcom.Gedcom(sys.argv[1])
llg = gedcom.LineageLinkedGedcom(g)

for i in llg.individuals:
	
    if i.records.has_key('_URL'):
        problems = []
        if i.get('SEX') is None:
            problems.append('sex not defined')
        for obj in i.getAll('OBJE'):
            if obj.get('FORM').value == 'Message':
                if obj.get('TEXT').value.lower().find('todo') != -1:
                    problems.append('todo found in message')
        if i.get('_BIO').get('TEXT').value.lower().find('todo') != -1:
            problems.append('todo found in bio')
        if len(problems):
            print
            print '\n'.join(problems)
            print i
            for obj in i.getAll('OBJE'):
                if obj.get('FORM').value == 'Message':
                    print obj.get('TEXT').value
