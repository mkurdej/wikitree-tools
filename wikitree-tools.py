#!/usr/bin/env python

import Tix
import ScrolledText
import os
import wt_lint
import ConfigParser

class WikiTreeApp(Tix.Frame):
    def __init__(self, master=None):
        Tix.Frame.__init__(self, master)

        self.conf = ConfigParser.ConfigParser()
        self.conf.add_section('Common')
        self.conf.add_section('Lint')
        self.conf.read((os.path.expanduser('~/.wikitree-tools.cfg'),))
        
        self.pack(expand=1,fill='both')
        self.createWidgets()
        self.master.title('WikiTree tools')

    def saveConfig(self):
        self.conf.write(open(os.path.expanduser('~/.wikitree-tools.cfg'),'w'))
        
    def createWidgets(self):
        
        self.infile_entry = Tix.FileEntry(self)
        self.infile_entry['dialogtype'] = 'tixExFileSelectDialog'
        self.infile_entry['label'] = 'GEDCOM:'
        self.infile_entry.pack(side='top',fill='x',expand=1)
        self.infile = Tix.StringVar()
        self.infile_entry['variable'] = self.infile
        self.infile_entry['command'] = self.inputChanged
        if self.conf.has_option('Common','input'):
            self.infile.set(self.conf.get('Common','input'))

        self.createLintWidgets()

        self.output = ScrolledText.ScrolledText(self)
        self.output['state'] = 'disabled'
        self.output.pack(side='bottom',fill='both',expand=1)

    def printOutput(self, data='', lf=True):
        self.output['state'] = 'normal'
        self.output.insert('end',data)
        if lf:
            self.output.insert('end','\n')
        self.output.see('end')
        self.output['state'] = 'disabled'
        
    def createLintWidgets(self):
        lf = Tix.LabelFrame(self)
        lf['label'] = 'Lint'
        lf.pack(side='top',fill='both',expand=1)

        oe = Tix.FileEntry(lf)
        oe['dialogtype'] = 'tixExFileSelectDialog'
        oe['label'] = 'Lint output: (.html)'
        oe.pack(side='top',fill='x',expand=1)
        self.lint_output = Tix.StringVar()
        oe['variable'] = self.lint_output
        oe['command'] = self.lintOutputChanged
        if self.conf.has_option('Lint','output'):
            self.lint_output.set(self.conf.get('Lint','output'))

        ma = Tix.LabelEntry(lf)
        ma['label'] = 'Maximum age:'
        self.max_age = Tix.DoubleVar()
        ma.entry['textvariable'] = self.max_age
        self.max_age.set(0.0)
        ma.pack(side='top')
        

        opts = Tix.Select(lf,allowzero=True)
        opts['label'] = 'Options'
        opts.add('birth',text='birth')
        opts.add('death',text='death')
        opts.pack(side='top',expand=1)
        self.lint_options = Tix.StringVar()
        opts['variable'] = self.lint_options
        
        
        lb = Tix.Button(lf)
        lb['text'] = 'Run Lint'
        lb['command'] = self.runLint
        lb.pack(side='right')

    def inputChanged(self,value):
        if os.path.exists(value):
            self.conf.set('Common','input',value)
            self.saveConfig()

    def lintOutputChanged(self,value):
        self.conf.set('Lint','output',value)
        self.saveConfig()
        

    def runLint(self):
        self.printOutput('Running wt_lint: '+self.infile.get())
        opts = []
        if self.max_age.get() > 0:
            opts.append('maxage='+str(self.max_age.get()))
        print self.lint_options.get()
        for o in self.lint_options.get()[1:-1].split(','):
            if o:
                opts.append(o[1:-1])
        if self.lint_output.get():
            opts.append('output='+self.lint_output.get())
        if not os.path.exists(self.infile.get()):
            self.printOutput('Missing GEDCOM file?')
        else:
            wt_lint.lint(self.infile.get(),opts,self.printOutput)
        self.printOutput('wt_lint done')
            
        
        

WikiTreeApp(Tix.Tk()).mainloop()

