# csvmanip

Simple file merging and csv creator

## Input 
Input are multiple files with lines having the following structure:
```
LABEL=VALUE
```
Lines starting with # are ignored

Every label is prefixed with CLASSLABEL starting from every occurence of 
```
CLASSLABEL:
```
Class label may be empty.

Future: input csv's with headers (TODO).

CSV header is created from LABEL's.

Rows are sorted using digits extracted from file names (e.g., result.12.txt result.1555.txt -> extracted 12, 1555).
Extracted digits are placed in Id column.
Filename is inserted into SourceFile column.
If a label occures several times, all occurences are relabeled to columns LABEL1, LABEL2 etc. (see -r1)

Typical usage to merge all files and files from given dirs into a single csv file:
```
csvmanip.py FILE1 FILE2 DIR1 DIR2 DIR3
```

## Command line options 

General options:
* -d "LABEL=VALUE,LABEL=VALUE,..." - set default values for given labels; forces sorting of columns
* -D FILE - default values from a file (see the input format); forces sorting of columns
* -s SEPARATOR - separator in the output file; the default is comma
* -f - rows are sorted based on input file order
* -i LABEL1,LABEL2,... - ignore LABELS (may include SourceFile, Id)
* -v LEVEL - verbose (0 lowest, default; 1 print basic info)

Global relabelling options in case of conflicting names of columns:
* -r [lm1aA_] - in case of multiple occurences of labels in the input file:
  *  1 - preserve all add suffix to the column label using numbers (default);
  *  l - preserve the last occurence of LABEL=VALUE from an input file
  *  m - merge all values into semicolon separated list 
  *  A - as above but use [A-Z]
  *  a - as above but use [a-z]  
* -R SUFFIXDELIMITER - suffix delimiter in relabelling; default is the empty string
  
Relabelling options for a given set of labels:
* -l LABEL1,LABEL2,... - as -rl but for given labels
* -m LABEL1,LABEL2,... - as -rm
* -1 LABEL1,LABEL2,... - as -r1
* -a LABEL1,LABEL2,... - as -ra
* -A LABEL1,LABEL2,... - as -rA
* -n LABEL1,LABEL2,... - labels without a class prefix (global)

Delimiters:
* -C CLASSDELIMITER - classname delimiter; the default is colon
* -R SUFFIXDELIMITER - suffix delimiter in relabelling (in -raA1); default is the empty string
* -M MERGEDELIMITER - deliminter in merging values (def. is semicolon)


## Examples

```
$ cat test/1.dat 
Edge=10
Edge=14
Tree=(a,b,c)

$ cat test/2.dat 
Edge=10
Edge=16

A1:
Err=False

A2:
Edge=100
Edge=103
Edge=105
:
Edge=12


$ cat test/3.dat 
a=True
Edge=10
Edge=11
Edge=12
Tree="(a,b)"
Tree="(c,d)"

A1:

Tree="(e,f)"
Tree=(a,(b,c))
Err=False
```

### Basic usage:

```
$ csvmanip.py test
Id,SourceFile,a,Edge,Edge1,Edge2,Tree,Tree1,A1:Tree,A1:Tree1,A1:Err,A2:Edge,A2:Edge1,A2:Edge2
1,test/1.dat,,10,14,,"(a,b,c)",,,,,,,
2,test/2.dat,,10,16,12,,,,,False,100,103,105
3,test/3.dat,True,10,11,12,"(a,b)","(c,d)","(e,f)","(a,(b,c))",False,,,
```

### Ignore Err and merge Edge labels

```
$ csvmanip.py  -i Err -m Edge test
Id,SourceFile,a,Edge,Tree,Tree1,A1:Tree,A1:Tree1,A2:Edge
1,test/1.dat,,10;14,"(a,b,c)",,,,
2,test/2.dat,,10;16;12,,,,,100;103;105
3,test/3.dat,True,10;11;12,"(a,b)","(c,d)","(e,f)","(a,(b,c))",
```

### Ignore Err and merge Edge labels

```
$ csvmanip.py  -i Err -m Edge test (disjoint in classes)
Id,SourceFile,a,Edge,Tree,Tree1,A1:Tree,A1:Tree1,A2:Edge
1,test/1.dat,,10;14,"(a,b,c)",,,,
2,test/2.dat,,10;16;12,,,,,100;103;105
3,test/3.dat,True,10;11;12,"(a,b)","(c,d)","(e,f)","(a,(b,c))",
```

### Ignore Err and merge all occurences of Edge labels (including classes)
```
$ csvmanip.py  -i Err -m Edge -n Edge test
Id,SourceFile,a,Edge,Tree,Tree1,A1:Tree,A1:Tree1
1,test/1.dat,,10;14,"(a,b,c)",,,
2,test/2.dat,,10;16;100;103;105;12,,,,
3,test/3.dat,True,10;11;12,"(a,b)","(c,d)","(e,f)","(a,(b,c))"
```

### Ignore Err and preserve the last occurence of Edge (including classes)
```
$ csvmanip.py  -i Err -l Edge -n Edge test
Id,SourceFile,a,Edge,Tree,Tree1,A1:Tree,A1:Tree1
1,test/1.dat,,14,"(a,b,c)",,,
2,test/2.dat,,12,,,,
3,test/3.dat,True,12,"(a,b)","(c,d)","(e,f)","(a,(b,c))"
```

### Ignore Err and Tree, set default for a, merge Edge, new column separator is ;, merging separator is ,
```
$ csvmanip.py  -i Err,Tree -d "a=False" -m Edge -s';' -M',' test
Id;SourceFile;a;Edge;A2:Edge
1;test/1.dat;False;10,14;
2;test/2.dat;False;10,16,12;100,103,105
3;test/3.dat;True;10,11,12;
```

