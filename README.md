# csvmanip
Simple file merging and csv creator

Input are multiple files with the following structure:
LABEL=VALUE
LABEL=VALUE
...
or they are csv's with headers.

CSV header is created from LABEL's.

Rows are sorted using digits extracted from file names (e.g., result.12.txt result.1555.txt -> extracted 12, 15).
Extracted digits are placed in Id column.
Filename is inserted into SourceFile column.
If a label occures several times, all occurences are relabeled to columns LABEL1, LABEL2 etc.

Typical usage:
csvmanip.py list of FILES and DIRS  - merge all files into a single csv file

-s - rows are sorted based on input file order
-i COL1,COL2,... - ignore LABELS (may include SourceFile, Id)
-e VALUE - use VALUE for empty cells; default is the empty string
-r - do not relabel multiple occurences of labels; preserve the last only
-m - do not relabel multiple occurences of labels; instead merge into semicolon separated list 
