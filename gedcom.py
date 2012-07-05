#!/usr/bin/env python


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
                self.value = '\n'+parts[1][5:]
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
                self.value += rec.value
            elif rec.tag == 'CONT':
                self.value += '\n'
                if rec.value is not None:
                    self.value += rec.value
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

class LineageLinkedGedcom:
    def __init__(self,gedcom):
        self.gedcom = gedcom

        self.header = None
        self.submission_record = None
        self.individuals = []
        self.families = []
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
                fr = FamilyRecord(r)
                self.families.append(fr)
                #print fr
            elif r.tag == 'INDI':
                ir = IndividualRecord(r)
                self.individuals.append(ir)
            else:
                print r.tag
            
class LineageLinkedRecord:
    def __init__(self,rec,lint):
        tags = []
        for r in rec.sub_records:
            if not lint.has_key(r.tag):
                print rec
                raise Exception('unknown tag: '+r.tag+' in '+rec.tag)
            if lint[r.tag]['single'] and r.tag in tags:
                raise Exception('multiple instances of '+r.tag+' in '+rec.tag)
            if lint[r.tag]['no_sub_records'] and len(r.sub_records):
                print r
                raise Exception('subrecords found: '+r.tag+' in '+rec.tag)
            if not r.tag in tags:
                tags.append(r.tag)
            
        
class EventRecord (LineageLinkedRecord):
    lint = {'PLAC':{'single':True,'no_sub_records':True},
            'DATE':{'single':True,'no_sub_records':True}
           }
    def __init__(self,rec):
        LineageLinkedRecord.__init__(self,rec,EventRecord.lint)
        self.type = rec.tag
        self.date = None
        self.location = None
        
        for r in rec.sub_records:
            if r.tag == 'DATE':
                self.date = r.value
            elif r.tag == 'PLAC':
                self.location = r.value

    def __str__(self):
        return self.type + ' date: ' +str(self.date)+' location: ' +str(self.location)

class NameRecord (LineageLinkedRecord):
    lint = {'NPFX':{'single':True,'no_sub_records':True},
            '_MIDN':{'single':True,'no_sub_records':True},
            'GIVN':{'single':True,'no_sub_records':True},
            'NICK':{'single':True,'no_sub_records':True},
           }
    def __init__(self,rec):
        LineageLinkedRecord.__init__(self,rec,NameRecord.lint)
        self.value = rec.value
        self.given = None
        self.prefix = None
        self.middle = None
        self.nickname = None

        for r in rec.sub_records:
            if r.tag == 'NPFX':
                self.prefix = r.value
            elif r.tag == '_MIDN':
                self.middle = r.value
            elif r.tag == 'GIVN':
                self.given = r.value
            elif r.tag == 'NICK':
                self.nickname = r.value
            else:
                print r

    def __str__(self):
        return ''.join(self.value.split('/'))

class ReferenceRecord (LineageLinkedRecord):
    lint = {'TYPE':{'single':True,'no_sub_records':True},
           }
    def __init__(self,rec):
        LineageLinkedRecord.__init__(self,rec,ReferenceRecord.lint)
        self.value = rec.value
        self.type = None

        for r in rec.sub_records:
            if r.tag == 'TYPE':
                self.type = r.value
            else:
                print r

    def __str__(self):
        return str(self.type)+':'+self.value

class BioRecord (LineageLinkedRecord):
    lint = {'TEXT':{'single':True,'no_sub_records':True},
           }
    def __init__(self,rec):
        LineageLinkedRecord.__init__(self,rec,BioRecord.lint)
        self.text = None

        for r in rec.sub_records:
            if r.tag == 'TEXT':
                self.text = r.value
            else:
                print r
        
class ObjectRecord (LineageLinkedRecord):
    lint = {'FORM':{'single':True,'no_sub_records':True},
            'DATE':{'single':True,'no_sub_records':True},
            'PLAC':{'single':True,'no_sub_records':True},
            'AUTH':{'single':True,'no_sub_records':True},
            'TEXT':{'single':True,'no_sub_records':True},
            'FILE':{'single':True,'no_sub_records':True},
            'TITL':{'single':True,'no_sub_records':True},
           }
    def __init__(self,rec):
        LineageLinkedRecord.__init__(self,rec,ObjectRecord.lint)
        self.form = None
        self.date = None
        self.location = None
        self.author = None
        self.text = None
        self.file = None
        self.title = None

        for r in rec.sub_records:
            if r.tag == 'FORM':
                self.form = r.value
            elif r.tag == 'DATE':
                self.date = r.value
            elif r.tag == 'PLAC':
                self.location = r.value
            elif r.tag == 'AUTH':
                self.author = r.value
            elif r.tag == 'TEXT':
                self.text = r.value
            elif r.tag == 'FILE':
                self.file = r.value
            elif r.tag == 'TITL':
                self.title = r.value
            else:
                print r

    def __str__(self):
        return str(self.form)+': '+str(self.text)
        
class SurnameRecord(LineageLinkedRecord):
    lint = {'_MARN':{'single':True,'no_sub_records':True},
            'NSFX':{'single':True,'no_sub_records':True},
            '_AKA':{'single':True,'no_sub_records':True},
           }
    def __init__(self,rec):
        LineageLinkedRecord.__init__(self,rec,SurnameRecord.lint)
        self.value = rec.value
        self.married_name = None
        self.suffix = None
        self.aka = None

        for r in rec.sub_records:
            if r.tag == '_MARN':
                self.married_name = r.value
            elif r.tag == 'NSFX':
                self.suffix = r.value
            elif r.tag == '_AKA':
                self.aka = r.value
            else:
                print r

    def __str__(self):
        return ''.join(self.value.split('/'))
        
class FamilyRecord (LineageLinkedRecord):
    lint = {'HUSB':{'single':True,'no_sub_records':True},
            'WIFE':{'single':True,'no_sub_records':True},
            'MARR':{'single':True,'no_sub_records':False},
            'CHIL':{'single':False,'no_sub_records':True},
           }
    def __init__(self,rec):
        LineageLinkedRecord.__init__(self,rec,FamilyRecord.lint)
        self.husband = None
        self.wife = None
        self.marriage = None
        self.children = []

        for r in rec.sub_records:
            if r.tag == 'HUSB':
                self.husband = r.value
            elif r.tag == 'WIFE':
                self.wife = r.value
            elif r.tag == 'MARR':
                self.marriage = EventRecord(r)
            elif r.tag == 'CHIL':
                self.children.append(r.value)
            else:
                print r
        #print rec

    def __str__(self):
        return str(self.husband)+' and '+str(self.wife)+' (marriage: '+str(self.marriage)+')'

class IndividualRecord (LineageLinkedRecord):
    lint = {'NAME':{'single':True,'no_sub_records':False},
            'SURN':{'single':True,'no_sub_records':False},
            'SEX':{'single':True,'no_sub_records':True},
            'BIRT':{'single':True,'no_sub_records':False},
            'DEAT':{'single':True,'no_sub_records':False},
            'FAMC':{'single':True,'no_sub_records':True},
            'FAMS':{'single':False,'no_sub_records':True},
            '_BIO':{'single':True,'no_sub_records':False},
            '_URL':{'single':True,'no_sub_records':True},
            '_EMAIL':{'single':True,'no_sub_records':True},
            'REFN':{'single':False,'no_sub_records':False},
            'OBJE':{'single':False,'no_sub_records':False},
           }
            
    def __init__(self,rec):
        LineageLinkedRecord.__init__(self,rec,IndividualRecord.lint)
        self.name = None
        self.surname = None
        self.sex = None
        self.birth = None
        self.death = None
        self.child_to_family = None
        self.spouse_to_family = []
        self.references = []
        self.bio = None
        self.url = None
        self.email = None
        self.objects = []

        for r in rec.sub_records:
            if r.tag == 'NAME':
                self.name = NameRecord(r)
            elif r.tag == 'SURN':
                self.surname = SurnameRecord(r)
            elif r.tag == 'SEX':
                self.sex = r.value
            elif r.tag == 'BIRT':
                self.birth = EventRecord(r)
            elif r.tag == 'DEAT':
                self.death = EventRecord(r)
            elif r.tag == 'FAMC':
                self.child_to_family = r.value
            elif r.tag == 'FAMS':
                self.spouse_to_family.append(r.value)
            elif r.tag == 'REFN':
                self.references.append(ReferenceRecord(r))
            elif r.tag == '_BIO':
                self.bio = BioRecord(r)
            elif r.tag == '_URL':
                self.url = r.value
            elif r.tag == '_EMAIL':
                self.email = r.value
            elif r.tag == 'OBJE':
                self.objects.append(ObjectRecord(r))
            else:
                print r

    def surname_soundex(self):
        if self.surname is not None:
            return soundex(self.surname.value)
                
    def __str__(self):
        ret = []
        ret.append(' '.join(('('+str(self.surname)+')',str(self.name))))
        ret.append('  b. '+str(self.birth))
        ret.append('  d. '+str(self.death))
        ret.append('  '+str(self.url))
        return '\n'.join(ret)

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
        if len(i.objects):
            print i
            for o in i.objects:
                print o

    