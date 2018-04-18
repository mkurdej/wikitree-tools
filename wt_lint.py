#!/usr/bin/env python
# pylint: disable=C0111

import datetime
import gedcom


def print_to_console(data=''):
    print data


def lint(fname, options, out=print_to_console):

    output = None
    opts = {}

    for opt in options:
        out(opt)
        if '=' in opt:
            key, value = opt.split('=', 1)
            opts[key] = value
        else:
            opts[opt] = None

    if opts.has_key('output'):
        output = open(opts['output'], 'w')

    maxage = None
    if opts.has_key('maxage'):
        maxage = float(opts['maxage'])

    ged = gedcom.Gedcom(fname)
    llg = gedcom.LineageLinkedGedcom(ged)

    if output is not None:
        output.write('<html><body>\n')
        output.write(
            '<h1><a href="http://www.wikitree.com">WikiTree</a> Lint</h1>\n')
        output.write('<p>Report run at: ' +
                     str(datetime.datetime.now()) + '</p>\n')
        output.write('<p>input: ' + fname + '</p>\n')
        output.write('<el>Lint options\n')
        for key, value in opts.iteritems():
            output.write('<li>' + key)
            if value is not None:
                output.write(': ' + value)
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
            if problems:
                if output is not None:
                    output.write(i.html() + '\n')
                    output.write('<h3>Problems:</h3>\n')
                    output.write('<e1>\n')
                    for problem in problems:
                        output.write('<li>' + problem + '</li>\n')
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
