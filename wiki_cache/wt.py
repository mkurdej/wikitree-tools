#!/usr/bin/env python

import ConfigParser
import urllib2
import urllib
import cookielib
import getpass

class Connection:
    def __init__(self):
        self.conf = ConfigParser.ConfigParser()
        self.conf.read('wt.conf')
        self.baseurl = 'http://www.wikitree.com'
        self.jar = cookielib.MozillaCookieJar('wt_cookies.txt')
        try:
            self.jar.load()
        except IOError:
            print 'no cookies loaded'
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.jar))

    def getPage(self,link):
        req = self.baseurl+link
        print 'req:',req
        ret = self.opener.open(req)
        print 'url:',ret.geturl()
        print 'code:',ret.getcode()
        print 'info:',ret.info()
        lines = ret.readlines()
        
        for l in lines:
            if l.strip() == '<title>Log in</title>':
                return self.login(link)
        return lines

    def login(self,link):
        print 'login required'
        print 'email:',self.conf.get('user','email')

        data = {'wpEmail':self.conf.get('user','email')}
        data['wpPassword'] = getpass.getpass()
        data['wpRemember'] = 1

        req = self.baseurl+"/index.php?title=Special:Userlogin&action=submitlogin&type=login"

        ret = self.opener.open(req,urllib.urlencode(data))
        print 'url:',ret.geturl()
        print 'code:',ret.getcode()
        print 'info:',ret.info()
        self.jar.save()
        

        if link is not None:
            return self.getPage(link)


    def getWatchlist(self):
        
        watchlist = self.getPage('/index.php?title=Special:WatchedList&p=3821472&limit=20000&order=toucheddn')
        if watchlist is not None:
            open('watchlist.html','w').write(''.join(watchlist))
            current_profile = None

            profiles = []

            for line in watchlist:
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
                            current_profile = None
            return profiles

if __name__ == '__main__':
    wt = Connection()
    wl = wt.getWatchlist()
    if wl is not None:
        print len(wl),'watchlist items'
    else:
        print 'watchlist not retrieved'
        