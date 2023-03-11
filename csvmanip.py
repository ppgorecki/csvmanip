#!/usr/bin/python3

import getopt
import sys
from pathlib import Path
import os
import re

def usage():
    print ("""
Clever merging multiple files into a single csv

csvmanip.py FILES... DIRS... 

 -s SEPARATOR - separator in output and -D/-d; the default is comma
 -d "LABEL=VALUE,LABEL=VALUE,..." - set default values for given labels
 -D FILE - default values from a file
 -f - rows are sorted based on input file order
 -i LABEL1,LABEL2,... - ignore LABELS (may include SourceFile, Id)
 -C CLASSDELIMITER - classname delimiter; the default is colon

 -r [lm1aA] - do not relabel multiple occurences of labels:
     l - preserve the last occurence of LABEL=VALUE from an input file
     m - merge all values into semicolon separated list 
     1 - preserve all add suffix to the column label using numbers (default)
     a - preserve all and add suffix to the column label using letters [a-z]
     A - as above but use [A-Z]
 -R SUFFIXDELIMITER - suffix delimiter in relabelling (in -raA1); default is the empty string

 -l LABEL1,LABEL2,... - as -rl but for given labels
 -m LABEL1,LABEL2,... - as -rm
 -1 LABEL1,LABEL2,... - as -r1
 -a LABEL1,LABEL2,... - as -ra
 -A LABEL1,LABEL2,... - as -rA
 -n LABEL1,LABEL2,... - labels without a class prefix (global)

 -v LEVEL - verbose (0 lowest, defailt; 1 print basic info)
""")

verbose = 0
idlabel = "Id"
sourcelabel = "SourceFile"

def getdigits(s):
    fdigits = re.search(r'\d+', s)
    if fdigits:
        return fdigits.group(0)
    return ''

class DataCollector:
    def __init__(self, defaults: [str], ignorelabels: [str] , separator: str, labseparator: str, relabelling: str, relabellingrules, classnamedelimiter: str):
        self.filecnt = 0
        self.relabelling = relabelling
        self.relabellingrules = relabellingrules
        self.separator = separator
        self.labseparator = labseparator
        self.classnamedelimiter = classnamedelimiter
        self.ignorelabels = ignorelabels 
        self.labels = [ [''] ]
        self.classname2labels = { '':self.labels[0] }        
        self.rows = []
        if idlabel not in ignorelabels: self.labels[0].append(idlabel)
        if sourcelabel not in ignorelabels: self.labels[0].append(sourcelabel)
        self.defaults = self.parse(defaults, '', '')        

    def parse(self, s: [str], idlab, srclab):
        labels = []
        res = {}
        relab = {}
        classname = ''
        destlabels = self.labels[0]

        if idlab and idlabel not in self.ignorelabels: 
            res[idlabel] = idlab

        if srclab and sourcelabel not in self.ignorelabels: 
            res[sourcelabel] = srclab

        for src in s:            
            l=src.strip()            
            
            if not l: continue

            if l and l[0]=='#': continue # comment

            if '=' not in l: 
                if l[-1]==':': # class name
                    classname = l[:-1]                    
                    if classname not in self.classname2labels:                    
                        # new class
                        self.labels.append([classname])
                        self.classname2labels[classname] = self.labels[-1]
                    continue
                raise Exception(f"LABEL=VALUE or ClassName: expected. Found {src}")
                
            lab,val = l.split('=',1)
            
            if lab in self.ignorelabels:
                continue            

            clab = lab
            print(lab,val,srclab)
            if lab in self.relabellingrules.get('noclass'):                
                destlabels = self.classname2labels['']
            else:
                if classname:
                    clab = classname + self.classnamedelimiter + clab                                                        
                destlabels = self.classname2labels[classname]
                

        
            original = clab 
            if clab in labels:
                # repeated label                

                # relabel rule
                if lab in self.relabellingrules['last'] or 'l' in self.relabelling:
                    res[clab] = val
                    continue
                elif lab in self.relabellingrules['merge'] or 'm' in self.relabelling:
                    res[clab] += ";" + val
                    continue
                digit = '1' in self.relabelling or lab in self.relabellingrules['digit']
                AZr = 'A' in self.relabelling or lab in self.relabellingrules['AZ']
                azr = 'a' in self.relabelling or lab in self.relabellingrules['az']
                if digit or AZr or azr:
                    if clab not in relab:                        
                        relab[clab] = 0
                    relab[clab]+=1

                    if digit:
                        suf = f"{relab[clab]}"
                    elif AZr:
                        suf = f"{chr(ord('A')+relab[clab])}"
                    elif azr:
                        suf = f"{chr(ord('a')+relab[clab])}"
                            
                    clab = clab+self.labseparator+suf                                        
            if clab not in labels: 
                labels.append(clab) 

            if clab not in res:                
                res[clab] = val
            else:
                raise Exception (f"label <{clab}> with suffix already present in the input")

            if clab not in destlabels:
                if original == clab:
                    destlabels.append(clab)                
                else:
                    pos = destlabels.index(original)                
                    while pos+1<len(destlabels):                                                
                        if original != destlabels[pos+1][:len(original)]:
                            break                   
                        pos += 1          

                    destlabels.insert(pos+1, clab)

        
        return res


    def readfile(self, path):
        
        if verbose>0:
            print(path)

        try:
            self.rows.append(self.parse(open(path),getdigits(str(path)),str(path)))        

        except Exception as e:
            print(f"Cannot read file {path}",file=sys.stderr)
            raise e
            exit(-1)

        pass

    # TODO: add recursive read via opt
    def readdir(self, dirpath):
        for path in os.scandir(dirpath):
            if path.is_file():
                self.readfile(Path(path))
            else:
                print(f"{p} should be a a file.",file=sys.stderr)            

    def readfiles(self, fnames):# get all files inside a specific folder        
        for f in fnames:
            p = Path(f)
            if p.is_file():
                self.readfile(p)
            elif p.is_dir():
                self.readdir(p)
            else:
                print(f"{p} should be a dir or a file.",sys.stderr)
                exit(-1)

    def csv(self, digitordering):
        #print ("defaults:",self.defaults)
        #print ("labels:",self.labels)
        
        # gen header        
        labs = sum((l[1:] for l in self.labels),[])
        # print(labs)
        print(self.separator.join(labs))

        if digitordering:
            s = sorted(self.rows,key=lambda r: int(r[idlabel]))
        else: s = self.rows
        for r in s:
            #print(r)
            for i,l in enumerate(labs):                
                sep=self.separator if i else ''                                
                if l in r: 
                    val=r[l]
                elif l in self.defaults:
                    val=self.defaults[l]
                else:
                    val=''
                
                if self.separator in val: # " forced 
                    if not (val[0]==val[-1] and val[0] in "\"'"):
                        val = '"' + val +'"'
                print(sep+val,end='')
            print()

        

def main():
    
    defaults = []
    digitordering = 1
    ignorelabels = []
    global verbose

    SEPARATOR=','
    SUFFIXSEPARATOR=''

    try:
        opts, args = getopt.getopt(sys.argv[1:], "s:d:D:fi:r:v:1:a:A:r:l:m:n:C:")
    except getopt.GetoptError as err:
        print(str(err))
        usage()
        sys.exit(2)

    if len(sys.argv) == 1:
        usage()
        sys.exit(1)

    separator = ','
    labseparator = ''
    relabelling = '1'
    classnamedelimiter = ':'

    rl = dict(az=[],AZ=[],merge=[],noclass=[],digit=[],last=[])
    
    for o, a in opts:

        if o == "-s":
            SEPARATOR = a
        elif o == "-d":
            defaults = a.split(",")      
        elif o == "-D":
            try:
                defaults = open(a).readlines()                   
            except:
                print(f"Cannot read file {a}",file=sys.stderr)
                exit(-1)
        elif o == "-f":
            digitordering = False
        elif o == "-i":
            ignorelabels = a.split(",")
        elif o == "-1":
            rl['digit'] = a.split(",")
        elif o == "-a":
            rl['az'] = a.split(",")
        elif o == "-A":
            rl['AZ'] = a.split(",")
        elif o == "-m":
            rl['merge'] = a.split(",")            
        elif o == "-l":
            rl['last'] = a.split(",")
        elif o == "-n":
            rl['noclass'] = a.split(",")
        elif o == "-r":
            relabelling = a
        elif o == "-v":
            verbose = int(a)
        elif o == "-R":
            labseparator = a          
        elif o == "-C":
            classnamedelimiter = a          
        else:
            assert False, "unhandled option %s %s " % (o, a)

    dc = DataCollector(defaults, ignorelabels, separator, labseparator, relabelling, rl, classnamedelimiter)

    dc.readfiles(args)

    dc.csv(digitordering)


if __name__ == "__main__":
    main()
