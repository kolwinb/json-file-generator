#!/bin/bash

#eg:
#api-json-split.sh oct 2017-oct-mobile.csv
#function split
#{
index=1
while read line
do
if [ "${line%%,*}" == "$index" ]
then
dayname=$1-$index.csv
#tdayname=tem-$index.csv
((index++))
else
echo $line >> $dayname
fi
done < $2
#}

#for fl in *.ods
#do
#soffice --headless --convert-to csv:"Text - txt - csv (StarCalc)":"44,ANSI,1" $fl #Text - txt - csv (StarCalc) is comma seperated,44->comma,59-->semicolon,comma-->44,doublequotes-->34
#sleep 10
#split ${fl%%.*}.csv
#split all-list.csv
#done

sed -i -- 's/-480p.mp4//g' $1-*.csv
#sed s/,/\:00,/ dharmavahini/nov-6.csv  change 19:00, to 19:00:00,
#sed -i -- s/,/\:00,/ nov-*.csv 
#sed -i -- s/^/00:/ nov-*.csv #place 00: to 06:00 like 00:06:00 begining of line

