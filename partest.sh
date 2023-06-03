
if [[ $# -gt 1 ]] && [[ $1 == '-g' ]]
then
	# gen exemplary file 
	# $3 is a prefix
	CNT=$2
	PREF=$3
	shift 2
	for i in $( seq $CNT )
	do		
		cat << EOF
command=partest.sh
-a:="abc def"
-b:= 
-c=1
-d=
EOF
	
	for i in $*
	do
		(( r=$RANDOM % 2 ))		
		if [[ $r = 0 ]]
		then
			echo "$i="
		else
			echo "$i=$(( $RANDOM % 20 ))"
		fi
	done
	done  | csvmanip.py -L -N command =
	exit 0
fi

# run job that produces datfile
if [[ $1 == '-o' ]] 
then
	rm -f $2 
	touch $2
	sleep $(( $RANDOM % 4 ))
cat << EOF >> $2
rnd=$RANDOM
pid=$$
opts="$*"
EOF
	exit 0
fi

cat << EOF 
To generate exemplary dat file: 
	$0 -g ROWS_CNT OPT1 OPT2 ...
where OPTs are either -[a-zA-Z] or -[a-zA-Z]:
EOF



