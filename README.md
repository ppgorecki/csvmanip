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
If a label occures several times, all occurences are relabeled to columns LABEL1, LABEL2 etc. (see relabelling rules)

Typical usage to merge all files and files from given dirs into a single csv file:
```
csvmanip.py FILE1 FILE2 DIR1 DIR2 DIR3
```

## Command line options 

### General options
* -d "LABEL=VALUE,LABEL=VALUE,..." - set default values for given labels; forces sorting of columns
* -D FILE - default values from a file (see the input format); forces sorting of columns
* -F - rows are sorted based on input file order
* -i LABELLIST - ignore LABELS (may include SourceFile, Id)

Here, LABELLIST is a comma-separated list of LABELS or ALL (meanining all labels). Class names can be also present. 
  
### Relabelling rules
Relabelling rules to be applied when multiple occurences of LABEL assignments in a single file. Below, if LABEL in a LABELLIST is a class name, the rule applies to all labels assigned to the class. 

* -f LABELLIST - for each class preserve the first occurence of LABEL=VALUE from each input
* -l LABELLIST - as above but for the last occurence
* -m LABELLIST - for each class merge all values into semicolon (see -M) separated list
* -1 LABELLIST - preserve all occurences by creating new labels: LABEL, LABEL1, LABEL2, etc. (default)
* -a LABELLIST - as above but use letters a-z as suffixes
* -A LABELLIST - as above but use letters A-Z as suffixes
* -n LABELLIST - ignore classes for the given labels (labels moved to global class)

### Delimiters and separators:
* -s SEPARATOR - separator in output and -d; the default is comma
* -M MERGEDELIMITER - delimiter in merging values (def. is semicolon)
* -C CLASSDELIMITER - classname delimiter; the default is colon
* -R SUFFIXDELIMITER - suffix delimiter in relabelling; default is the empty string

### Verbose level
* -v LEVEL - verbose (0 lowest, default; 1 print basic info)

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

### Ignore Err and merge Edge labels in classes

```
$ csvmanip.py  -i Err -m Edge test 
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

### Ignore classes A1 and A2, take first values
```
$ csvmanip.py  -i A1,A2 -f ALL test
Id,SourceFile,a,Edge,Tree
1,test/1.dat,,10,"(a,b,c)"
2,test/2.dat,,10,
3,test/3.dat,True,10,"(a,b)"
```
