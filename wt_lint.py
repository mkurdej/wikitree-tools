#!/usr/bin/env python
# pylint: disable=C0111

import datetime
import gedcom


def print_to_console(data=''):
    print data


def parse_options(options, out):
    opts = {}

    for opt in options:
        out(opt)
        if '=' in opt:
            key, value = opt.split('=', 1)
            opts[key] = value
        else:
            opts[opt] = None

    return opts


def write_report_header(filename, opts, output):
    if output is None:
        return

    output.write('<html><body>\n')
    output.write(
        '<h1><a href="http://www.wikitree.com">WikiTree</a> Lint</h1>\n')
    output.write('<p>Report run at: ' +
                 str(datetime.datetime.now()) + '</p>\n')
    output.write('<p>input: ' + filename + '</p>\n')
    output.write('<el>Lint options\n')
    for key, value in opts.iteritems():
        output.write('<li>' + key)
        if value is not None:
            output.write(': ' + value)
        output.write('</li>\n')
    output.write('</el>\n')


def check_individual(individual, opts, maxage):
    if not individual.records.has_key('WWW'):
        return

    problems = []
    if maxage is not None and individual.getAge() is not None and individual.getAge() > maxage:
        problems.append(
            'age {0} greater than maximum age {1}'.format(individual.getAge(), maxage))

    if opts.has_key('birth') and individual.get('BIRT').get('DATE') is None:
        problems.append('missing birth date')
    if opts.has_key('death') and individual.get('DEAT') is None:
        problems.append('missing date of death')
    if individual.get('SEX') is None:
        problems.append('sex not defined')
    for obj in individual.getAll('OBJE'):
        if obj.get('FORM').value == 'Message':
            if obj.get('TEXT').value.lower().find('todo') != -1:
                problems.append('todo found in message')
    if individual.get('NOTE').get('TEXT').value.lower().find('todo') != -1:
        problems.append('todo found in bio')

    return problems

def write_problems(individual, problems, output, out):
    if not problems:
        return

    if output is not None:
        output.write(individual.html() + '\n')
        output.write('<h3>Problems:</h3>\n')
        output.write('<e1>\n')
        for problem in problems:
            output.write('<li>' + problem + '</li>\n')
        output.write('</e1>\n')

    out('')
    out('\n'.join(problems))
    out(individual)
    for obj in individual.getAll('OBJE'):
        if obj.get('FORM').value == 'Message':
            out(obj.get('TEXT').value)


def lint(filename, options, out=print_to_console):
    output = None
    opts = parse_options(options, out)

    if opts.has_key('output'):
        output = open(opts['output'], 'w')

    maxage = None
    if opts.has_key('maxage'):
        maxage = float(opts['maxage'])

    ged = gedcom.Gedcom(filename)
    llg = gedcom.LineageLinkedGedcom(ged)

    if output is not None:
        write_report_header(filename, opts, output)

    for individual in llg.individuals:
        problems = check_individual(individual, opts, maxage)
        write_problems(individual, problems, output, out)

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
