#!/usr/bin/env python

import gedcom
import datetime


def stdPrint(data=''):
    print data


def lint(fname, options, out=stdPrint):

    output = None
    opts = {}

    for o in options:
        out(o)
        if '=' in o:
            k, v = o.split('=', 1)
            opts[k] = v
        else:
            opts[o] = None

    if opts.has_key('output'):
        output = open(opts['output'], 'w')

    maxage = None
    if opts.has_key('maxage'):
        maxage = float(opts['maxage'])

    g = gedcom.Gedcom(fname)
    llg = gedcom.LineageLinkedGedcom(g)

    if output is not None:
        output.write('<html><body>\n')
        output.write(
            '<h1><a href="http://www.wikitree.com">WikiTree</a> Lint</h1>\n')
        output.write('<p>Report run at: ' +
                     str(datetime.datetime.now()) + '</p>\n')
        output.write('<p>input: ' + fname + '</p>\n')
        output.write('<el>Lint options\n')
        for k, v in opts.iteritems():
            output.write('<li>' + k)
            if v is not None:
                output.write(': ' + v)
            output.write('</li>\n')
        output.write('</el>\n')

    for i in llg.individuals:

        if i.records.has_key('WWW'):
            problems = []
            if maxage is not None and i.getAge() is not None and i.getAge() > maxage:
                problems.append(
                    'age {0} greater than maximum age {1}'.format(i.getAge(), maxage))

            if opts.has_key('birth') and i.get('BIRT').get('DATE') is None:
                problems.append('missing birth date')
            if opts.has_key('death') and i.get('DEAT') is None:
                problems.append('missing date of death')
            if i.get('SEX') is None:
                problems.append('sex not defined')
            for obj in i.getAll('OBJE'):
                if obj.get('FORM').value == 'Message':
                    if obj.get('TEXT').value.lower().find('todo') != -1:
                        problems.append('todo found in message')
            if i.get('NOTE').get('TEXT').value.lower().find('todo') != -1:
                problems.append('todo found in bio')
            if len(problems):
                if output is not None:
                    output.write(i.html() + '\n')
                    output.write('<h3>Problems:</h3>\n')
                    output.write('<e1>\n')
                    for p in problems:
                        output.write('<li>' + p + '</li>\n')
                    output.write('</e1>\n')
                out('')
                out('\n'.join(problems))
                out(i)
                for obj in i.getAll('OBJE'):
                    if obj.get('FORM').value == 'Message':
                        out(obj.get('TEXT').value)

    if output is not None:
        output.write('</body></html>\n')


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print 'usage: wt_lint.py gedcom.ged [options]'
        print '\toptions:'
        print '\t\toutput=report.html'
        exit(1)

    lint(sys.argv[1], sys.argv[2:])
