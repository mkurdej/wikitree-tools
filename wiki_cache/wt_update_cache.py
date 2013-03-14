#!/usr/bin/env python

import sys
import datetime
import urllib2

watchlist = urllib2.urlopen('http://www.wikitree.com/index.php?title=Special:WatchedList&p=3821472&limit=20000&order=toucheddn')

lines = watchlist.readlines()

open('watchlist.html','w').write(''.join(lines))

ok = True

for line in lines:
    if line.strip() == '<title>Log in</title>':
        ok = False
        break

if not ok:
    print 'log in needed'
else:

    current_profile = None

    profiles = []

    for line in lines:
        if current_profile is None:
            if "<!-- it's a person -->" in line:
                current_profile = {}
                profiles.append(current_profile)
        else:
            if not 'href' in current_profile:
                if 'href' in line:
                    current_profile['href'] = line.split('"')[1]
                    current_profile['name'] = line.rsplit('<',1)[0].rsplit('>',1)[1]
            else:
                if 'title="Last Changes"' in line:
                    current_profile['modified_date'] = datetime.datetime.strptime(line.rsplit('<',2)[0].rsplit('>',1)[1],'%b %d, %Y')
                    print current_profile
                    current_profile = None

            