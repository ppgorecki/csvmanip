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

CSV header is created from LABEL's.

A dat file can be divided into multiple rows with option -N LABEL. Each occurence of LABEL
starts a new row.

Rows are sorted using digits extracted from file names (e.g., result.12.txt result.1555.txt -> extracted 12, 1555).
Extracted digits are placed in Id column.
Filename is inserted into Source column.
If a label occures several times, all occurences are relabeled to columns LABEL1, LABEL2 etc. (see relabelling rules)

Csv input files can be also given in input, where each row of csv is converted into a single dat-file record.

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
* -c - print warning if values are inequal when processing labels by -f/-l
* -e LABELLIST - extract given LABELS only
* -u [m|s] - merge columns from classes if equal [s-take shortest as label, m-merge labels]
* -N NEWDATFIELD - convert a single dat file into multiple dat files when a NEWDATFIELD is present
 
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

### Other
* -q - do not add quotations in strings
* -H - skip header


## Examples

```
> cat test/1.dat 
Edge=10
Edge=14
Tree=(a,b,c)
```

```
> cat test/2.dat 
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
```
> cat test/3.dat 
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
> cat test2/4.dat
Edge=10
A=40
Edge=12
A=1
Edge=14
A=123
```

### Basic usage:

```
> csvmanip.py test
Id,Source,a,Edge,A2:Edge,Edge1,A2:Edge1,Edge2,A2:Edge2,Tree,A1:Tree,Tree1,A1:Tree1,A1:Err
1,test/1.dat,,10,,14,,,,"(a,b,c)",,,,
2,test/2.dat,,10,100,16,103,12,105,,,,,False
3,test/3.dat,True,10,,11,,12,,"(a,b)","(e,f)","(c,d)","(a,(b,c))",False
```

### Ignore Err and merge Edge labels

```
> csvmanip.py  -i Err -m Edge test
Id,Source,a,Edge,A2:Edge,Tree,A1:Tree,Tree1,A1:Tree1
1,test/1.dat,,10;14,,"(a,b,c)",,,
2,test/2.dat,,10;16;12,100;103;105,,,,
3,test/3.dat,True,10;11;12,,"(a,b)","(e,f)","(c,d)","(a,(b,c))"
```

### Ignore Err and merge Edge labels in classes

```
> csvmanip.py  -i Err -m Edge test 
Id,Source,a,Edge,A2:Edge,Tree,A1:Tree,Tree1,A1:Tree1
1,test/1.dat,,10;14,,"(a,b,c)",,,
2,test/2.dat,,10;16;12,100;103;105,,,,
3,test/3.dat,True,10;11;12,,"(a,b)","(e,f)","(c,d)","(a,(b,c))"
```

### Ignore Err and merge all occurences of Edge labels (including classes)
```
> csvmanip.py  -i Err -m Edge -n Edge test
Id,Source,a,Edge,Tree,A1:Tree,Tree1,A1:Tree1
1,test/1.dat,,10;14,"(a,b,c)",,,
2,test/2.dat,,10;16;100;103;105;12,,,,
3,test/3.dat,True,10;11;12,"(a,b)","(e,f)","(c,d)","(a,(b,c))"
```

### Ignore Err and preserve the last occurence of Edge (including classes)
```
> csvmanip.py  -i Err -l Edge -n Edge test
Id,Source,a,Edge,Tree,A1:Tree,Tree1,A1:Tree1
1,test/1.dat,,14,"(a,b,c)",,,
2,test/2.dat,,12,,,,
3,test/3.dat,True,12,"(a,b)","(e,f)","(c,d)","(a,(b,c))"
```

### Ignore Err and Tree, set default for a, merge Edge, new column separator is ;, merging separator is ,
```
> csvmanip.py  -i Err,Tree -d "a=False" -m Edge -s';' -M',' test
Id;Source;a;Edge;A2:Edge
1;test/1.dat;False;10,14;
2;test/2.dat;False;10,16,12;100,103,105
3;test/3.dat;True;10,11,12;
```

### Ignore classes A1 and A2, take first values
```
> csvmanip.py  -i A1,A2 -f ALL test
Id,Source,a,Edge,Tree
1,test/1.dat,,10,"(a,b,c)"
2,test/2.dat,,10,
3,test/3.dat,True,10,"(a,b)"
```

### Take first values, but check if some values are lost
```
> csvmanip.py  -i A1 -f A2 -c test 
Warning: in test/2.dat lost value of A2:Edge=103 in the first rule (stored 100)
Warning: in test/2.dat lost value of A2:Edge=105 in the first rule (stored 100)
Id,Source,a,Edge,A2:Edge,Edge1,Edge2,Tree,Tree1
1,test/1.dat,,10,,14,,"(a,b,c)",
2,test/2.dat,,10,100,16,12,,
3,test/3.dat,True,10,,11,12,"(a,b)","(c,d)"
```

### Reading from stdin (-) dat format or (--) csv format.

```
> cat test/1.dat test/2.dat | csvmanip.py - 
Id,Source,Edge,A2:Edge,Edge1,A2:Edge1,Edge2,A2:Edge2,Edge3,Edge4,Tree,A1:Err
-,-,10,100,14,103,10,105,16,12,"(a,b,c)",False
```

### Multiple row from a single dat (-N FIELD); start a new row when Edge is assigned 

```
> csvmanip.py  -N Edge test2/4.dat
Id,Source,Edge,A
4:0,test2/4.dat,10,40
4:1,test2/4.dat,12,1
4:2,test2/4.dat,14,123
```

### Reading from stdin (-): dat file only
```
> cat test2/4.dat | csvmanip.py  -N Edge -
Id,Source,Edge,A
0,-,10,40
1,-,12,1
2,-,14,123
```

### Merge dat and csv files

Each row of csv is converted into a single dat-file record. Merging is performed using 
Id column/field, i.e., rows with the same Id will be merged. To avoid merging from two files use -I option, to create a new unique Id by attaching sourceid. Each row from a csv belong to a class whose label is basename of the csv file.

```
> csvmanip.py -N Edge test/1.dat  > a.csv && cat a.csv
Id,Source,Edge,Tree
1:0,test/1.dat,10,
1:1,test/1.dat,14,"(a,b,c)"
```

```
> csvmanip.py -N Edge a.csv test2/4.dat
Id,Source,a:Source,Edge,a:Edge,A,a:Tree
1:0,a,test/1.dat,,10,,
1:1,a,test/1.dat,,14,,"(a,b,c)"
4:0,test2/4.dat,,10,,40,
4:1,test2/4.dat,,12,,1,
4:2,test2/4.dat,,14,,123,
```

### Command generator (-X)

Use field command  and datfile (optional).

```
> cat test2/c1.csv

Id,Source,command,datfile,-a:,-B
0,-,partest.sh,1.dat,"abc def",1
1,-,partest.sh,2.dat,"",1
2,-,partest.sh,3.dat,,
```

Datfiles are generated by using -o (see -X o) from the command (here partest.sh).
```
> csvmanip.py -X o test2/c1.csv
datfile=1.dat && id=0 && partest.sh -o $DATFILE -a "abc def" -B 
datfile=2.dat && id=1 && partest.sh -o $DATFILE -a "" -B 
datfile=3.dat && id=2 && partest.sh -o $DATFILE 
```

If datfile is not present csvmanip will generate automatic name using id.

```
> cat test2/c2.csv
Id,Source,command,-a:,-b
0,-,partest.sh,"A U",1
1,-,partest.sh,,
```

Rows with the same Id are merged.

```
> csvmanip.py -X o test2/c1.csv test2/c2.csv

Assignment <-a:="abc def"> ignored. -a: already present in the input.
datfile=1.dat && id=0 && partest.sh -o $DATFILE -a "abc def" -B -b 
datfile=2.dat && id=1 && partest.sh -o $DATFILE -a "" -B 
datfile=3.dat && id=2 && partest.sh -o $DATFILE 
```

Use -I to avoid merging commands with the same Id.

```
> csvmanip.py -I -X o test2/c1.csv test2/c2.csv

datfile=1.dat && id=0.c1 && partest.sh -o $DATFILE -a "abc def" -B 
datfile=2.dat && id=1.c1 && partest.sh -o $DATFILE -a "" -B 
datfile=3.dat && id=2.c1 && partest.sh -o $DATFILE 
id=0.c2 && partest.sh -o $DATFILE -a "A U" -b 
id=1.c2 && partest.sh -o $DATFILE 
```


### Testing csvparallel.sh

Prepare some data

```
> partest.sh -g 3 -A: > c1.csv && cat c1.csv
Id,Source,command,-a:,-b:,-c,-d,-A:
0,-,partest.sh,"abc def",,1,,12
1,-,partest.sh,"abc def",,1,,3
2,-,partest.sh,"abc def",,1,,
```

```
> partest.sh -g 2 -Y > c2.csv && cat c2.csv
Id,Source,command,-a:,-b:,-c,-d,-Y
0,-,partest.sh,"abc def",,1,,
1,-,partest.sh,"abc def",,1,,
```

Run commands. Result in work dir (set workdir with -D) and with summary 
```
> csvparallel.sh c1.csv c2.csv 
Computers / CPU cores / Max jobs to run
1:local / 16 / 5

Results merged in work/all.csv
```

```
> ls work
0.c1.dat
0.c2.dat
1.c1.dat
1.c2.dat
2.c1.dat
3.c1.dat
all.csv
```

```
> cat work/all.csv
Id,Source,rnd,pid,opts
0.c1,work/0.c1.dat,18152,133418,"-o 0.c1.dat.tmp -a abc def -A 1 -c"
0.c2,work/0.c2.dat,32002,133440,"-o 0.c2.dat.tmp -a abc def -c"
1.c1,work/1.c1.dat,6996,133423,"-o 1.c1.dat.tmp -a abc def -A 11 -c"
1.c2,work/1.c2.dat,31515,133448,"-o 1.c2.dat.tmp -a abc def -X 14 -c -Y"
2.c1,work/2.c1.dat,20663,133429,"-o 2.c1.dat.tmp -a abc def -A 13 -c"
3.c1,work/3.c1.dat,4312,133436,"-o 3.c1.dat.tmp -a abc def -c"
```





