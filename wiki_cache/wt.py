#!/usr/bin/env python

import urllib2
import urllib
import cookielib
import getpass
import datetime
import os

class WikiTreeError(Exception):
    pass

class LoginError(WikiTreeError):
    def __init__(self, msg):
        self.msg = msg

def loginPrompt(email = ''):
    print 'WikiTree Login'
    email_in = raw_input('Email ['+email+']:')
    if len(email_in):
        email = email_in
    return email, getpass.getpass()


class Connection:
    def __init__(self, cookie_path=None, debug=False, login_prompt=loginPrompt):
        self.baseurl = 'http://www.wikitree.com'
        self.debug = debug
        self.login_prompt = login_prompt

        if cookie_path is None:
            cookie_path = os.path.expanduser('~/.wikitree/cookies.txt')
        self.jar = cookielib.MozillaCookieJar(cookie_path)
        try:
            self.jar.load()
        except IOError:
            if self.debug:
                print 'no cookies loaded'
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.jar))
        self.getUserInfo()

    def getPage(self,link):
        if '{UID}' in link or '{UNAME}' in link:
            if self.uid is None or self.uname is None:
                self.getPage('/wiki/Special:Home')
                self.getUserInfo()
            link = link.format(UID=self.uid,UNAME=self.uname)
                
        req = self.baseurl+link
        if self.debug:
            print 'req:',req
        ret = self.opener.open(req)
        if self.debug:
            print 'url:',ret.geturl()
            print 'code:',ret.getcode()
            print 'info:',ret.info()
        if ret.geturl() == self.baseurl+'/wiki/Special:Userlogin':
            self.login()
            return self.getPage(link)
        return ret

    def login(self, max_tries=3):
        tries = 0
        email = ''
        while tries < max_tries:
            email,pwd = self.login_prompt(email)
            if self.debug:
                print 'email:',email,'password:','*'*len(pwd)
                
            data = {'wpEmail':email,'wpPassword':pwd}
            data['wpRemember'] = 1

            req = self.baseurl+"/index.php?title=Special:Userlogin&action=submitlogin&type=login"
            ret = self.opener.open(req,urllib.urlencode(data))

            if ret.getcode() == 200 and ret.geturl() == self.baseurl+ '/wiki/Special:Home':
                cookie_dir = os.path.dirname(self.jar.filename)
                if not os.path.exists(cookie_dir):
                    os.makedirs(cookie_dir)
                self.jar.save()
                self.getUserInfo()
                return
            tries += 1
        raise LoginError("Login failed")

    def getUserInfo(self, response=None):
        self.uid = None
        self.uname = None
        for c in self.jar:
            if c.name == 'wikitree_wtb_UserName':
                self.uname = c.value
            if c.name == 'wikitree_wtb_UserID':
                self.uid = c.value

    def getWatchlist(self):
        watchlist = self.getPage('/index.php?title=Special:WatchedList&p={UID}&limit=20000&order=toucheddn')
        if watchlist is not None:
            lines = watchlist.readlines()
            open('watchlist.html','w').write(''.join(lines))
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
                            current_profile = None
            return profiles

if __name__ == '__main__':
    wt = Connection(debug=True)
    wl = wt.getWatchlist()
    if wl is not None:
        print len(wl),'watchlist items'
    else:
        print 'watchlist not retrieved'
        