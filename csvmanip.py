#!/usr/bin/python3

import getopt
import sys
from pathlib import Path
import os
import re

def usage():
    print ("""
Clever merging multiple files into a single csv

csvmanip.py OPTIONS FILES... DIRS... 

- = stdin input file

Options:
 
 -d "LABEL=VALUE,LABEL=VALUE,..." - set default values for given labels
 -D FILE - default values from a file
 -F - rows are sorted based on input file order
 -i LABELLIST - ignore LABELS (may include SourceFile, Id)
 -e LABELLIST - extract given LABELS only
 -c - print warning if values are unequal when processing labels by -f/-l
 -u [m|s] - merge columns from classes if equal [s-take shortest as label, m-merge labels] 
 -L - keep original order of columns (labels)
 -X OPT - generate commands, -OPT is the option for generating dat file ion the command (see csvparallel.sh)
 
 -r [lm1aA] - do not relabel multiple occurences of labels:
     l - preserve the last occurence of LABEL=VALUE from an input file
     m - merge all values into semicolon separated list 
     1 - preserve all add suffix to the column label using numbers (default)
     a - preserve all and add suffix to the column label using letters [a-z]
     A - as above but use [A-Z]

Below, if LABEL in a LABELLIST is a class name, the rule applies to all labels assigned to the class.
In case of multiple occurences of LABEL assignments in a single file:
 -f LABELLIST - for each class preserve the first occurence of LABEL=VALUE from each input
 -l LABELLIST - as above but for the last occurence
 -m LABELLIST - for each class merge all values into semicolon (see -M) separated list
 -1 LABELLIST - preserve all occurences by creating new labels: LABEL, LABEL1, LABEL2, etc. (default)
 -a LABELLIST - as above but use letters a-z as suffixes
 -A LABELLIST - as above but use letters A-Z as suffixes
 -n LABELLIST - ignore classes for the given labels (labels moved to global class)

-V - ignore classes from csv

LABELLIST := LABEL[,LABEL]* or 'ALL' (meaning all labels)

Delimiters and separators:
 -s SEPARATOR - separator in output and -d; the default is comma
 -M MERGEDELIMITER - delimiter in merging values (def. is semicolon)
 -C CLASSDELIMITER - classname delimiter; the default is colon
 -R SUFFIXDELIMITER - suffix delimiter in relabelling; default is the empty string

 -v LEVEL - verbose (0 lowest, default; 1 print basic info)
 -q - do not add quotations in strings
 -H - skip header
""")

verbose = 0
idlabel = "Id"
sourcelabel = "Source"

def getid(s):
    return Path(s).stem
    # fdigits = re.search(r'\d+', s)
    # if fdigits:
    #     return fdigits.group(0)
    #return ''

class DataCollector:
    def __init__(self, defaults: [str], ignorelabels: [str] , separator: str, labseparator: str,  relabellingrules, classnamedelimiter: str, mergedelimiter: str, checkmerging: bool, extractlabels: [str], newdatfield: str, skipcsvclass: bool, 
        attachsourceid: bool,
        generatecommands: bool):
        self.filecnt = 0        
        self.skipcsvclass = skipcsvclass
        self.relabellingrules = relabellingrules
        self.attachsourceid = attachsourceid
        self.generatecommands = generatecommands
        self.separator = separator
        self.checkmerging = checkmerging
        self.labseparator = labseparator
        self.classnamedelimiter = classnamedelimiter
        self.mergedelimiter = mergedelimiter
        self.ignorelabels = ignorelabels 
        self.extractlabels = extractlabels
        self.labels = [ [''] ]
        self.classname2labels = { '':self.labels[0] }        
        self.rows = []
        self.srcdats = []
        self.sourceids = {}
        self.collector = {}
        self.newdatfield = newdatfield
        if 'ALL' not in self.ignorelabels:
            if idlabel not in ignorelabels: self.labels[0].append(idlabel)
            if sourcelabel not in ignorelabels: self.labels[0].append(sourcelabel)
        self.defaults = self.parsedat(defaults, '', '')        

    def parsedat(self, s: [str], idlab, srclab):        
        labels = []
        res = {}
        relab = {}
        classname = ''
        destlabels = self.labels[0]



        if 'ALL' not in self.ignorelabels: 
            if idlab and idlabel not in self.ignorelabels:
                res[idlabel] = idlab

            if srclab and sourcelabel not in self.ignorelabels:
                res[sourcelabel] = srclab            

        for src in s:                 
            l=src.strip()            
            
            if not l: continue

            if l and l[0]=='#': continue # comment
            if l==':': 
                classname = '' # reset classname
                continue


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
            
            if lab in self.ignorelabels or 'ALL' in self.ignorelabels:
                continue            

            if self.extractlabels and lab not in self.extractlabels:
                continue

            clab = lab
            curclassname = classname

            if lab in self.relabellingrules.get('noclass'):                
                destlabels = self.classname2labels['']
                curclassname = ''
            else:
                if classname:
                    clab = classname + self.classnamedelimiter + clab                                                        
                destlabels = self.classname2labels[classname]

            if curclassname in self.ignorelabels:
                continue            
        
            original = clab 
            if clab in labels:
                # repeated label          
                def checkrelabel(rule, lab, curclassname):
                    return lab in self.relabellingrules[rule] or "ALL" in self.relabellingrules[rule] or curclassname in self.relabellingrules[rule] or curclassname in self.relabellingrules[rule] 
                    
                #print("HER",lab,curclassname,checkrelabel('first',lab,curclassname),self.relabellingrules)
                # relabel rule
                if checkrelabel('last', lab, curclassname): 
                    if self.checkmerging and clab in res and res[clab]!=val:
                        print(f"Warning: in {srclab} lost value of {clab}={res[clab]} in the last rule (stored {val})",file=sys.stderr)
                    res[clab] = val
                    continue

                if checkrelabel('first', lab, curclassname): 
                    if self.checkmerging and clab in res and res[clab]!=val:
                        print(f"Warning: in {srclab} lost value of {clab}={val} in the first rule (stored {res[clab]})",file=sys.stderr)

                    if clab not in res: res[clab] = val
                    continue

                if checkrelabel('merge',lab, curclassname):                 
                    res[clab] += self.mergedelimiter + val
                    continue

                digit = checkrelabel('digit',lab, curclassname)                 
                AZr = checkrelabel('AZ',lab, curclassname)                 
                azr = checkrelabel('az',lab, curclassname)       

                if not AZr or not azr: digit=True # default 

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
                            
                    if not (self.generatecommands and clab[-1]==':'):
                        clab = clab+self.labseparator+suf                                        
            if clab not in labels: 
                labels.append(clab) 
                
            if clab not in res:                
                res[clab] = val
            else:
                if clab == sourcelabel or clab == idlabel:
                    res[clab+"Prev"] = clab # replace prev Source/Id 
                else:
                    if self.generatecommands:
                        print(f"Assignment <{clab}={res[clab]}> ignored. {clab} already present in the input.", file=sys.stderr)
                    else:
                        raise Exception (f"label <{clab}={res[clab]} with suffix already present in the input")

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

    def add2collector(self, dataid, s, sourceid=''):

        if self.attachsourceid: 
            dataid = dataid+"."+str(sourceid)

        if dataid not in self.srcdats:
            self.srcdats.append(dataid)
            self.collector[dataid] = ''            
            self.sourceids[dataid] = str(sourceid)        

        self.collector[dataid] += s + "\n:\n" # end class with :

    def readdatfile(self, f, path):

        def splitrows(p):
            if not self.newdatfield:
                yield p, getid(path)
            else:                        
                if not str(path): pref=''
                else: pref=getid(path)+":"                    
                sl = []
                cnt = 0
                for l in p.split("\n"):
                    l = l.strip()                        
                    if not l: continue
                    if l and l[0]=='#': 
                        continue # comment
                
                    if '=' not in l:
                        sl.append(l)
                        continue

                    lab,val = l.split('=',1)

                    if lab.strip() == self.newdatfield:
                        if sl:                        
                            yield "\n".join(sl), pref+str(cnt)
                            cnt += 1 
                            sl = []

                    sl.append(l)                    
                if sl:                                       
                    yield "\n".join(sl), pref+str(cnt)

        if verbose>0:
            print(path)
        try:            
            src = f.read()
            res = []
            for r, fid in splitrows(src):                            
                self.add2collector(fid, r, path)
            

        except Exception as e:
            print(f"Cannot read file {path}",file=sys.stderr)
            raise e
            exit(-1)

        

    def readcsvfile(self, f, path):
        
        if self.skipcsvclass or not str(path.stem):
            pref = ''
        else:
            pref = str(path.stem)+":\n"

        if verbose>0:
            print(path)

        try:
            
            r = f.readlines()
            header = r.pop(0).strip().split(",")                
            try:
                idHeader = header.index(idlabel) 
            except ValueError:
                print(f"{idlabel} column missing in {path}")
                exit(-1)

            for l in r:
                l = l.strip()
                curstr = ''
                splt = []
                ignorecomma = False
                for c in l:
                    if c==',' and not ignorecomma:
                        splt.append(curstr)                           
                        curstr=''
                        continue
                    curstr += c
                    if c=='"':
                        ignorecomma = not ignorecomma
                        continue
                splt.append(curstr)                    
                mrg = "\n".join(f"{a}={b}" for a,b in zip(header,splt) if a!=idlabel and b != '')                    


                self.add2collector(splt[idHeader],pref+mrg, getid(path))
                        

        except Exception as e:
            print(f"Cannot read file {path}",file=sys.stderr)
            raise e
            exit(-1)

        pass

    def _read(self, pth): 
        
        if pth.is_file():                
            if pth.suffix in ('.dat','.csv'):
                yield pth
        elif pth.is_dir():
            for path in os.scandir(pth):
                for p in self._read(Path(path)):
                    yield p                
        elif str(pth) in "-=":            
            yield pth        
        else:
            print(f"{pth} should be a .dat, .csv or - (stdin).",file=sys.stderr)


    def readfiles(self, fnames): 
        
        flist = [ p for f in fnames for p in self._read(Path(f)) ]        
        
        for p in flist:
                    
            if p.suffix == '.dat':                
                with open(p) as f:
                    self.readdatfile(f, p)                        
            elif p.suffix == '.csv':                
                with open(p) as f:                
                    self.readcsvfile(f, p)
            elif str(p) == "=":                
                self.readdatfile(sys.stdin, "")  
            elif str(p) == "-":                                
                self.readcsvfile(sys.stdin, "")

        for p in self.srcdats:            
            self.rows.append(self.parsedat(self.collector[p].split("\n"), p, 
                self.sourceids[p]))

    def mergeeqcolumns(self, labsmerge: int ):

        def eqcolumns(l1,l2):
            for r in self.rows:
                if l1 in r and l2 in r and r[l1]==r[l2]: 
                    continue
                if l1 not in r and l2 not in r: 
                    continue
                return False
            return True

        labs = sum((l[1:] for l in self.labels),[])        
        clust = []
        for l in labs:
            for cluster in clust:
                if eqcolumns(l,cluster[0]):
                    cluster.append(l)
                    break
            else:
                clust.append([l]) # new cluster
    
        # merge names

        def maxsuffixlen(cluster):
            cx = min(cluster, key=len)
            #print("AA",cluster,cx)
            i = len(cx)

            while True:                
                for c in cluster:
                    if cx != c[len(c)-i:]:
                        i-=1
                        cx=cx[1:]
                        break
                else:
                    return i
                    
        d={}

        if labsmerge == 'm':

            def skipcolon(s): return s[:-1] if s and s[-1]==':' else s
            
            for cluster in clust:

                if len(cluster)==1:
                    d[cluster[0]] = cluster[0]
                else:
                    q = maxsuffixlen(cluster)            
                    cs = cluster[0][len(cluster[0])-q:]                    
                    d[cluster[0]] = ''.join(skipcolon(c[:len(c)-q]) for c in cluster)+"-"+cs

        else:                    
            d = dict((cluster[0],(min(cluster, key=len),cluster)) for cluster in clust )

        for cluster in clust:
            for c in cluster[1:]:
                for lb in self.labels:
                    if c in lb: lb.remove(c)        
        return d


    def sortlabels(self, labs):

        dest = []
        for l in labs:
            if ':' in l:
                pref,suf = l.rsplit(':',1)
        
                for gr in dest:
                    if gr[0] == suf:
                        gr.append(l)
                        break
                else:
                    dest.append([suf,l])
            else:
                dest.append([l,l])
        
        return [ l for gr in dest for l in gr[1:] ]

    def csv(self, digitordering, skipheader, skipquotations, colnames,  originallabelorder):
                
        # gen header        
        labs = sum((l[1:] for l in self.labels),[])
        
        if not originallabelorder:           
            labs = self.sortlabels(labs)

        if not colnames:
            _labs = labs[:]
        else:
            _labs = [ colnames[l] for l in labs ]

        if not self.generatecommands and not skipheader:
            print(self.separator.join(_labs))            
            
        if digitordering:
            try:
                s = sorted(self.rows,key=lambda r: int(r[idlabel]))
            except:
                s = self.rows
        else: s = self.rows        
        
        for r in s:   

            resbody = ''
            resdt = ''                 
            datfilepresent = False

            for i,l in enumerate(labs):                                
            
                sep=self.separator if i else ''                                
                if l in r: 
                    val=r[l]
                elif l in self.defaults:
                    val=self.defaults[l]
                else:
                    val=''

                if skipquotations and len(val)>1 and val[0]=='"' and val[-1]=='"':
                    val=val[1:-1]
                
                if not skipquotations:
                    if self.separator in val: # " forced 
                        if not (val[0]==val[-1] and val[0] in "\"'"):
                            val = '"' + val +'"'

                if self.generatecommands:
                    if not val: 
                        continue # skip if val is empty
                    if _labs[i][0]=='-':                        
                        opt = _labs[i]                        
                        if opt[-1]==':':                    
                            # option + arg
                            resbody += f'{opt[:-1]} {val} '
                        else:                      
                            # just flag (val ignored)       
                            resbody += f'{_labs[i]} '
                    elif _labs[i] == 'command':
                        resbody = f'{val} -{self.generatecommands} $DATFILE {resbody}'
                    elif _labs[i] == 'datfile':                        
                        resdt = f"datfile={val} && " + resdt
                        datfilepresent = True
                    elif _labs[i] == idlabel:
                        resdt = f"id={val} && " + resdt
                        
                else: # smp csv 
                    resbody += sep+val
            
            print(resdt + resbody)



        

def main():
    
    defaults = []
    digitordering = 1
    ignorelabels = []
    checkmerging = False
    generatecommands = None
    global verbose

    try:
        opts, args = getopt.getopt(sys.argv[1:], "e:s:d:R:D:Ff:i:v:1:a:A:r:l:m:n:VC:M:cqHu:N:X:LI")
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
    mergedelimiter = ';'
    extractlabels = []
    skipquotations = False
    skipheader = False
    mergeeqcolumns = ''
    basenameSource = False
    ignorecsvclass = False
    originallabelorder = False
    attachsourceid = False

    rl = dict(az=[],AZ=[],merge=[],noclass=[],digit=[],last=[],first=[])
    newdatfield = ''

    for o, a in opts:
        if o == "-s":
            separator = a # assign first
    
    for o, a in opts:
    
        if o == "-s":
            pass
        elif o == "-d":
            defaults = a.split(separator)      
        elif o == "-X":
            generatecommands = a 
        elif o == "-L":
            originallabelorder = True
        elif o == "-V":
            ignorecsvclass = True
        elif o == "-D":
            try:
                defaults = open(a).readlines()                   
            except:
                print(f"Cannot read file {a}",file=sys.stderr)
                exit(-1)
        elif o == "-F":
            digitordering = False
        elif o == "-I":
            attachsourceid = True
        elif o == "-i":
            ignorelabels = a.split(",")
        elif o == "-e":
            extractlabels = a.split(",")
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
        elif o == "-f":
            rl['first'] = a.split(",")            
        elif o == "-n":
            rl['noclass'] = a.split(",")        
        elif o == "-v":
            verbose = int(a)
        elif o == "-R":
            labseparator = a          
        elif o == "-C":
            classnamedelimiter = a          
        elif o == "-c":
            checkmerging = True          
        elif o == "-H":
            skipheader = True                 
        elif o == "-q":
            skipquotations = True                 
        elif o == "-M":
            mergedelimiter = a
        elif o == "-N":
            newdatfield = a
        elif o == "-u":
            mergeeqcolumns = a        
        else:
            assert False, "unhandled option %s %s " % (o, a)

    if generatecommands: ignorecsvclass = True

    dc = DataCollector(defaults, ignorelabels, separator, labseparator, rl, classnamedelimiter, mergedelimiter, checkmerging, extractlabels, newdatfield, ignorecsvclass, attachsourceid, generatecommands)

    dc.readfiles(args)

    mergeeqcolumnsd = None
    colnames = {}
    if mergeeqcolumns: 
        colnames = dc.mergeeqcolumns(mergeeqcolumns)
    
    dc.csv(digitordering,skipheader,skipquotations,colnames, originallabelorder)




if __name__ == "__main__":
    main()
