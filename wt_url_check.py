#!/usr/bin/env python

import gedcom
import sys
import urllib2
import socket


def usage():
    print 'usage: wt_url_check.py gedcom.ged [check]'
    print '    defaults to only listing the urls, add check to actually check if they are valid'
    exit(1)

if len(sys.argv) not in [2,3]:
    usage()

check = False

if len(sys.argv) == 3:
    if sys.argv[2] == 'check':
        check = True
    else:
        usage()
    
g = gedcom.Gedcom(sys.argv[1])
llg = gedcom.LineageLinkedGedcom(g)

urls = {}

for i in llg.individuals:
    if i.get('NOTE') is not None:
        for l in i.get('NOTE').get('TEXT').value.splitlines():
            start = l.find('http')
            if start != -1:
                #print l
                url = l[start:].split()[0]
                if '<' in url:
                    url = url[:url.find('<')]
                if ']' in url:
                    url = url[:url.find(']')]
                #print url
                if not urls.has_key(url):
                    urls[url] = []
                urls[url].append(i)

opener = urllib2.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0')]

for u,individuals in urls.iteritems():
    ok = False
    error = '\n'
    print u
    if check:
        try:
            #data = urllib2.urlopen(u,None,20)
            opener.open(u,timeout=20)
            ok = True
        except socket.timeout:
            error += '!!!! timed out connecting to server !!!!'
        except urllib2.URLError as e:
            error += ' '.join(('!!!! urllib2 error:',str(e),'!!!!'))
        except socket.error as e:
            error += ' '.join(('!!!! socket error:',str(e),'!!!!'))

    if not ok:
        print error
        print u
        for i in individuals:
            print i
