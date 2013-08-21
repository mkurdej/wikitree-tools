#!/usr/bin/env python

''' Classes for parsing a GEDCOM file.
More info on GEDCOM:  http://en.wikipedia.org/wiki/GEDCOM
V5.5 specs: http://homepages.rootsweb.ancestry.com/~pmcbride/gedcom/55gctoc.htm
V5.5.1 specs: http://www.phpgedview.net/ged551-5.pdf
'''

import datetime

class GedcomRecord:
    def __init__(self,line):
        parts = line.strip().split(' ',1)
        self.level = int(parts[0])

        parts = parts[1].split(' ',1)

        if parts[0][0] == '@' and parts[0][-1] == '@':
            self.xref_id = parts[0]
            parts = parts[1].split(' ',1)
        else:
            self.xref_id = None

        self.tag = parts[0]

        if len(parts) == 2:
            if parts[1].startswith('CONC '):
                self.value = parts[1][5:]
            elif parts[1].startswith('CONT '):
                #self.value = '\n'+parts[1][5:]
                self.value = parts[1][5:]+'\n'
            else:
                self.value = parts[1]
            
        else:
            self.value = None

        self.sub_records = []

    def addRecord(self,rec):
        if rec.level <= self.level:
            raise 'invalid record level'
        if rec.level == self.level+1:
            if rec.tag == 'CONC':
                if rec.value is not None:
                    self.value += rec.value
            elif rec.tag == 'CONT':
                if rec.value is not None:
                    self.value += rec.value
                self.value += '\n'
            else:
                self.sub_records.append(rec)
        else:
            self.sub_records[-1].addRecord(rec)
            
    def __str__(self):
        ret = []
        ret.append(('\t'*self.level)+'\t'.join((str(self.xref_id),self.tag,str(self.value))))
        for r in self.sub_records:
            ret.append(str(r))
        return '\n'.join(ret)

class Gedcom:
    def __init__(self,fname):
        self.xref_ids = {}
        self.records = []

        
        
        infile = open(fname,'r')
        for l in infile.readlines():
            rec = GedcomRecord(l)
            if rec.xref_id is not None:
                self.xref_ids[rec.xref_id]=rec
                
            if rec.level == 0:
                self.records.append(rec)
            else:
                self.records[-1].addRecord(rec)
        
            
    def __str__(self):
        ret = []
        for r in self.records:
            ret.append(str(r))
        return '\n'.join(ret)

handlers = {}
        
class LineageLinkedGedcom:
    def __init__(self,gedcom,h=handlers):
        self.gedcom = gedcom
        self.handlers = h

        self.header = None
        self.submission_record = None
        self.individuals = []
        self.families = []
        self.index = {}
        self.trailer = None

        for r in gedcom.records:
            if r.tag == 'HEAD':
                if self.header is not None:
                    raise 'multiple header records found'
                self.header = r
            elif r.tag == 'SUBN':
                if self.submission_record is not None:
                    raise 'multiple submission records found'
                self.submission_record = r
            elif r.tag == 'TRLR':
                if self.trailer is not None:
                    raise 'multiple trailer records found'
                self.trailer = r
            elif r.tag == 'FAM':
                fr = self.handlers[r.tag](r,h)
                self.families.append(fr)
                if r.xref_id is not None:
                    self.index[r.xref_id]=fr
            elif r.tag == 'INDI':
                ir = self.handlers[r.tag](r,h)
                self.individuals.append(ir)
                if r.xref_id is not None:
                    self.index[r.xref_id]=ir
            else:
                pass
                #print r.tag
        
        for i in self.individuals:
            for tag in ('FAMS','FAMC'):
                if i.records.has_key(tag):
                    for f in i.records[tag]:
                        if self.index.has_key(f.value):
                            f.value = self.index[f.value]
        for f in self.families:
            for tag in ('HUSB','WIFE','CHIL'):
                if f.records.has_key(tag):
                    for i in f.records[tag]:
                        if self.index.has_key(i.value):
                            i.value = self.index[i.value]
            
                        
        
class LineageLinkedRecord:
    def __init__(self,rec,h):
        self.handlers = h
        self.tag = rec.tag
        self.value = rec.value
        self.records = {}
        self.xref_id = rec.xref_id
        self.reference_numbers = {}

        for r in rec.sub_records:
            if not self.handleRecord(r):
                #print rec
                #raise Exception('record not handled: '+r.tag+' in '+rec.tag)
                print 'record not handled: '+r.tag+' in '+rec.tag
            
    def handleRecord(self,rec):
        try:
            self.append(rec.tag,self.handlers[rec.tag](rec,self.handlers))
        except KeyError:
            self.append(rec.tag,rec)
        return True

    def append(self,tag,value):
        if not self.records.has_key(tag):
            self.records[tag]=[]
        self.records[tag].append(value)
        if tag == 'REFN':
            self.reference_numbers[value.getType()]=value.value

    def get(self,tag):
        if self.records.has_key(tag):
            return self.records[tag][0]
            
    def getValue(self,tag):
        ret = self.get(tag)
        if ret is not None:
            return ret.value
            
    def getAll(self,tag):
        if self.records.has_key(tag):
            return self.records[tag][:]
        return []


class EventRecord (LineageLinkedRecord):
    def __init__(self,rec,h):
        LineageLinkedRecord.__init__(self,rec,h)

    def __str__(self):
        return str(self.getValue('DATE'))+' ' +str(self.getValue('PLAC'))

class DateRecord (LineageLinkedRecord):
    def __init__(self,rec,h):
        LineageLinkedRecord.__init__(self,rec,h)

    def asDate(self):
        parts = self.value.split()
        if parts[0] in ('ABT','BEF','AFT'):
            parts = parts[1:]
        fmt = ' '.join(('%d','%b','%Y')[-len(parts):])
        if fmt:
            return datetime.datetime.strptime(' '.join(parts),fmt).date()

class NameRecord (LineageLinkedRecord):
    def __init__(self,rec,h):
        LineageLinkedRecord.__init__(self,rec,h)

    def __str__(self):
        return ' '.join(''.join(self.value.split('/')).split())

class ReferenceRecord (LineageLinkedRecord):
    def __init__(self,rec,h):
        LineageLinkedRecord.__init__(self,rec,h)

    def __str__(self):
        return str(self.type)+':'+self.value

class NoteRecord (LineageLinkedRecord):
    def __init__(self,rec,h):
        LineageLinkedRecord.__init__(self,rec,h)
        
class ObjectRecord (LineageLinkedRecord):
    def __init__(self,rec,h):
        LineageLinkedRecord.__init__(self,rec,h)

    def form(self):
        ret = self.get('FORM')
        if ret is None:
            return self.value
        return ret

    def text(self):
        return self.get('TEXT')

    def __str__(self):
        return str(self.form())+': '+str(self.text())
        
class SurnameRecord(LineageLinkedRecord):
    def __init__(self,rec,h):
        LineageLinkedRecord.__init__(self,rec,h)

    def __str__(self):
        return ''.join(self.value.split('/'))
        
class FamilyRecord (LineageLinkedRecord):
    def __init__(self,rec,h):
        LineageLinkedRecord.__init__(self,rec,h)

    def __str__(self):
        ret = []
        ret.append(str(self.getValue('HUSB'))+' and '+str(self.getValue('WIFE'))+' (marriage: '+str(self.get('MARR'))+')')
        for c in self.getAll('CHIL'):
            ret.append('  '+str(c))
        return '\n'.join(ret)

class IndividualRecord (LineageLinkedRecord):
    def __init__(self,rec,h):
        LineageLinkedRecord.__init__(self,rec,h)


    def surname_soundex(self):
        if self.get('SURN') is not None:
            return soundex(self.get('SURN').value)

    def isName(self,n):
        return str(self.get('NAME')) == n

    def getAge(self):
        birth = None
        if self.get('BIRT') is not None and self.get('BIRT').get('DATE') is not None:
            birth = self.get('BIRT').get('DATE').asDate()

        death = None
        if self.get('DEAT') is not None and self.get('DEAT').get('DATE') is not None:
            death = self.get('DEAT').get('DATE').asDate()

        if birth is not None and death is not None:
            return (death - birth).days/365.25
        if birth is not None:
            return (datetime.date.today() - birth).days/365.25
        
    def label(self):
        ret = []

        ret.append(str(self.records['NAME'][0]))
        if self.get('BIRT') is not None and self.get('BIRT').get('DATE') is not None:
            ret.append('  b. '+str(self.get('BIRT').getValue('DATE')))
        if self.get('DEAT') is not None and self.get('DEAT').get('DATE') is not None:
            ret.append('  d. '+str(self.get('DEAT').getValue('DATE')))
        return '\n'.join(ret)

    def html(self):
        ret = []
        if self.get('WWW') is not None:
            ret.append('<h2><a href="'+str(self.getValue('WWW'))+'" target="_blank">'+str(self.records['NAME'][0])+'</a></h2>')
        else:
            ret.append('<h2>'+str(self.records['NAME'][0])+'</h2>')
        ret.append('<el>')
        ret.append('<li>b. '+str(self.get('BIRT'))+'</li>')
        ret.append('<li>d. '+str(self.get('DEAT'))+'</li>')
        ret.append('</el>')

        return '\n'.join(ret)
 

    def __str__(self):
        ret = []

        ret.append(str(self.records['NAME'][0]))
        if self.get('BIRT') is not None:
            ret.append('  b. '+str(self.get('BIRT')))
        if self.get('DEAT') is not None:
            ret.append('  d. '+str(self.get('DEAT')))
        if self.get('WWW') is not None:
            ret.append('  '+str(self.getValue('WWW')))
        return '\n'.join(ret)

class UserReferenceNumberRecord (LineageLinkedRecord):
    def __init__(self,rec,h):
        LineageLinkedRecord.__init__(self,rec,h)

    def getType(self):
        t = self.get('TYPE')
        if t is not None:
            return t.value
        

handlers['INDI'] = IndividualRecord
handlers['FAM']=FamilyRecord
handlers['NOTE']=NoteRecord
handlers['OBJE']=ObjectRecord
handlers['NAME']=NameRecord
handlers['SURN']=SurnameRecord
handlers['BIRT']=EventRecord
handlers['DEAT']=EventRecord
handlers['MARR']=EventRecord
handlers['REFN']=UserReferenceNumberRecord
handlers['DATE']=DateRecord


## {{{ http://code.activestate.com/recipes/52213/ (r1)
def soundex(name, len=4):
    """ soundex module conforming to Knuth's algorithm
        implementation 2000-12-24 by Gregory Jorgensen
        public domain
    """

    # digits holds the soundex values for the alphabet
    digits = '01230120022455012623010202'
    sndx = ''
    fc = ''

    # translate alpha chars in name to soundex digits
    for c in name.upper():
        if c.isalpha():
            if not fc: fc = c   # remember first letter
            d = digits[ord(c)-ord('A')]
            # duplicate consecutive soundex digits are skipped
            if not sndx or (d != sndx[-1]):
                sndx += d

    # replace first digit with first alpha character
    sndx = fc + sndx[1:]

    # remove all 0s from the soundex code
    sndx = sndx.replace('0','')

    # return soundex code padded to len characters
    return (sndx + (len * '0'))[:len]
## end of http://code.activestate.com/recipes/52213/ }}}
        
        
if __name__ == '__main__':
    import sys
    g = Gedcom(sys.argv[1])
    llg = LineageLinkedGedcom(g)
    for i in llg.individuals:
        print i.get('NAME')
        print i.getAge()
        if i.records.has_key('OBJE'):
            print i
            for o in i.records['OBJE']:
                print o
        #print i.reference_numbers

    
