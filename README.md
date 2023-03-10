# csvmanip
Simple file merging and csv creator

Input are multiple files with the following structure:
```
LABEL=VALUE
LABEL=VALUE
...
```
or they are csv's with headers.

CSV header is created from LABEL's.

Rows are sorted using digits extracted from file names (e.g., result.12.txt result.1555.txt -> extracted 12, 15).
Extracted digits are placed in Id column.
Filename is inserted into SourceFile column.
If a label occures several times, all occurences are relabeled to columns LABEL1, LABEL2 etc.

Typical usage to merge all files and files from given dirs into a single csv file:
```
csvmanip.py FILE1 FILE2 DIR1 DIR2 DIR3
```

Options
* -s - separator in output and -D/-d; the default is comma
* -d "LABEL=VALUE,LABEL=VALUE,..." - set default values for given labels
* -D FILE - default values from a file
* -f - rows are sorted based on input file order
* -i LABEL1,LABEL2,... - ignore LABELS (may include SourceFile, Id)
* -r [lm1aA_] - do not relabel multiple occurences of labels:
  *  l - preserve the last occurence of LABEL=VALUE from an input file
  *  m - merge all values into semicolon separated list 
  *  a - preserve all and add suffix to the column label using letters [a-z], instead of 1, 2, 3,... (default)
  *  A - as above but use [A-Z]
  *  _ - use underscore before relabelling suffix
