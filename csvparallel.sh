#!/bin/bash
#

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

    datfile=$WORKDIR/dat/$datfile
    DATFILE=$datfile.tmp    

    if [[ $FORCE ]] || ! [[ -f $datfile ]]
    then
        # gen datfile by a command

        eval $*        

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

csvmanip.py -X $OPTDATFILE -I $* | parallel --progress --no-run-if-empty -j $JOBS runsingle

# csvmanip.py -H -e Id -i Source -I $*

csvmanip.py -I $* | csvmanip.py -- $WORKDIR/dat/*.dat > $WORKDIR/all.csv

echo Results merged in $WORKDIR/all.csv