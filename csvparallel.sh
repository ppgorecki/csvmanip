#!/bin/bash

OPTDATFILE=o
JOBS=10
WORKDIR=work

function Usage()
{

cat <<EOF
Usage: $0 [-o OPTDATFILE ] [-j JOBS] [-h] [-f] jobspec.csv
	-j JOBS - number of jobs for parallel (def. $JOBS)
	csv - list of commands with parameters; required fields are "command" and "datfile"
	-f - force (overwrite exisiting dat files)
    -D - working dir (def. work)
    -X OPTDATFILE - output option to generate datfile (def. $OPTDATFILE)
    -h - help
EOF

} 

if ! [[ $* ]]
then
    Usage     
    exit 20
fi

set -- $( getopt j:hfD:X: $* )

while [ "$1" != -- ]
do
    case $1 in
        -h)   HFLG=1;;
        -f)   export FORCE=1;;
        -D)   export WORKDIR=$2; shift;;
	    -j)   JOBS=$2; shift;;        
        -X)   export OPTDATFILE=$2; shift;;        
    esac
    shift   
done

shift   

runsingle()
{    

    dgs="([a-zA-Z0-9.$]+)"
    [[ $* =~ id=$dgs ]] && id=${BASH_REMATCH[1]}
    if ! [[ $id ]]
    then
        >&2 echo "No id defined in $*"
        exit -1
    fi

    [[ $* =~ datfile=$dgs ]] && datfile=${BASH_REMATCH[1]}
    [[ $datfile ]] || datfile=$id.dat    

    LOGFILE=$WORKDIR/log/$(basename $datfile .dat).log
    datfile=$WORKDIR/dat/$datfile
    DATFILE=$datfile.tmp    

    if [[ $FORCE ]] || ! [[ -f $datfile ]]
    then
        # gen datfile by a command

        eval $* > $LOGFILE         

        if ! [[ -f $DATFILE ]]
        then
            >&2 echo "No datfile generated from $*"
            exit -1  
        fi

        echo "Id=$id" > $datfile
        cat $DATFILE >> $datfile 
        rm $DATFILE
    fi
}

export -f runsingle
export JOBS
export PATH=$PATH:$PWD
export WORKDIR
mkdir -p $WORKDIR/dat
mkdir -p $WORKDIR/log

csvmanip.py -X $OPTDATFILE -I $* | parallel --progress --no-run-if-empty -j $JOBS runsingle

LST=$( csvmanip.py -H -e Id -i Source -I $* | sed s/$/.dat/g )
CURDIR=$PWD

cd $WORKDIR/dat  > /dev/null
csvmanip.py $LST > $CURDIR/$WORKDIR/res.csv 
cd - > /dev/null

csvmanip.py -V -I $* | csvmanip.py -V - $WORKDIR/res.csv > $WORKDIR/all.csv

echo Results merged in $WORKDIR/all.csv and $WORKDIR/res.csv