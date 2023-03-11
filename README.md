# csvmanip
Simple file merging and csv creator

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



