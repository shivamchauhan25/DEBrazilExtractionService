#!/bin/bash
date_extract()
{
#passing the pdf_file as a parameter to the start_date(variable)
start_date="$1"
string_date=$(echo "$start_date"|grep -o -E "[0-9]*(/|-)*[a-zA-ZçÇ]+[[:space:]]*(/|-)+[[:space:]]*[0-9]{2,4}+")
if [ ! -z "$string_date" ]
then
start_date=$string_date
fi
#Replacing the actual month name with first three characters for all months
start_date=$(echo "$start_date"|sed "s/Janeiro/Jan/gI"|sed "s/Fevereiro/feb/gI"|sed "s/Março/mar/gI"|sed "s/Abril/apr/gI"|sed "s/Mai/may/gI"|sed "s/Maio/may/gI"|sed "s/Junho/jun/gI"|sed "s/Julho/jul/gI"|sed "s/Agosto/aug/gI"|sed "s/Setembro/sept/gI"|sed "s/Outubro/oct/gI"|sed "s/Novembro/nov/gI"|sed "s/Dezembro/dec/gI"|sed "s/Fev/feb/gI"|sed "s/Abr/apr/gI"|sed "s/Ago/aug/gI"|sed "s/Set/sept/gI"|sed "s/Out/oct/gI"|sed "s/Dez/dec/gI"|sed "s/January/Jan/gI"|sed "s/february/feb/gI"|sed "s/march/mar/gI"|sed "s/april/apr/gI"|sed "s/june/jun/gI"|sed "s/july/jul/gI"|sed "s/august/aug/gI"|sed "s/september/sep/gI"|sed "s/october/oct/gI"|sed "s/november/nov/gI"|sed "s/december/dec/gI"|sed "s/uk/unk/gI"|sed "s/^XX-//g"|sed "s/XXX-//g"|sed -r "s/_|\//-/g"|sed "s/ /-/g")
start_date=$(echo "$start_date"|sed "s/Jan/01/gI"|sed "s/feb/02/gI"|sed "s/mar/03/gI"|sed "s/apr/04/gI"|sed "s/may/05/gI"|sed "s/jun/06/gI"|sed "s/jul/07/gI"|sed "s/aug/08/gI"|sed "s/sept/09/gI"|sed "s/oct/10/gI"|sed "s/nov/11/gI"|sed "s/dec/12/gI")

#counting the '-' in a date
abc_check=$(echo "$start_date"|grep -o "-"|wc -l)
#loop to check if '-' is 0 then counting the "‐" in start_date
if [ "$abc_check" -eq 0 ]
then
abc_check=$(echo "$start_date"|grep -o "‐"|wc -l)
fi

#regex for year
pat_year="^[0-9]{4}"

#matching the regex pattern for year
abc_year=$(echo "$start_date"|grep -E -o "$pat_year")

#loop to check whether it matches the first pattern or second pattern if abc_check is 0
if [ "$abc_check" -eq 0 ]
then
pat="[0-9]+[0-9a-zA-Z]*[0-9]*"
pat1="^[a-zA-Z][0-9a-zA-Z]*[0-9]*"
abc=$(echo "$start_date"|grep -w -E "$pat")
abc1=$(echo "$start_date"|grep -w -E "$pat1")

#loop to convert the date if the date is partial then add ?? as a month or day or returning the actual date
#also replacing the un-\|^Un-\|unk-\|^UN-\|UNK-\|Unk-\|NR-/ in date with ??
if [ ! -z "$abc_year" ]
then
start_date=$(echo ??-???-"$start_date")
elif [ ! -z "$abc" ]
then
start_date=$(date -d "$start_date" +%d-%m-%Y)
elif [ ! -z "$abc1" ]
then
mon_val=${start_date:0:3}
mon_val=$(echo "$mon_val"|sed "s/[[:space:]]*//g")
year_val2=$(echo "$start_date"|awk -F"$mon_val" '{print $2}')
start_date=$(echo "??-""$mon_val""-"$year_val2)
else
start_date=""
fi
elif [ "$abc_check" -eq 1 ]
then
start_date=$(echo "$start_date"|sed 's/^un\|unk\|^UN\|^Un\|UNK\|Unk\|NR/???/gI')
start_date=$(echo ??-"$start_date")
elif [ "$abc_check" -eq 2 ]
then
start_date=$(echo "$start_date"|sed 's/-un\|-unk\|-Un\|-UN\|-UNK\|-Unk\|-NR/-???/gI')
start_date=$(echo "$start_date"|sed 's/^un-\|^Un-\|unk-\|^UN-\|UNK-\|Unk-\|NR-/??-/gI')

fi	

que_check="^??"
que_check1="??-???"
que_check2=$(echo "$start_date"|grep "$que_check")
que_check3=$(echo "$start_date"|grep "$que_check1")
que_check4="[0-9]"
if [ -z "$que_check3" ]
then
day=$(echo "$start_date"|awk -F'-' '{print $1}')
mon=$(echo "$start_date"|awk -F'-' '{print $2}')
year_val=$(echo "$start_date"|awk -F'-' '{print $3}')
mon_val=$(echo "$mon"|grep "$que_check4")
if [ ! -z "$mon_val" ]
then
if [ "$mon" -gt "12" ]
then
	if [ "$day" -le "12" ]
	then
start_date=$(echo "$mon""-""$day""-""$year_val")
else 
	start_date=""
fi

fi
fi
fi

###check if two digits in the year###
year_len=$(echo "$start_date"|awk -F'-' '{print $3}'|wc -c)
if [ "$year_len" -eq 3 ]
then
if [ "$year_val" -gt 25 ]
then
start_date=$(echo "$day""-""$mon""-19""$year_val")
else
start_date=$(echo "$day""-""$mon""-20""$year_val")
fi
fi


start_date=$(echo "$start_date"|grep -E -o "[0-9]{1,2}-[A-Za-z]{3}-[0-9]{4}|[?]{2}-[A-Za-z]{3}-[0-9]{4}|[?]{2}-[?]{3}-[0-9]{4}|[0-9]{2}-[A-Za-z]{3}-[0-9]{4}|[0-9]{2}-[?]{3}-[0-9]{4}|[0-9]{1}-[?]{3}-[0-9]{4}|[0-9]{1}-[0-9]{2}-[0-9]{4}|[0-9]{1}-[0-9]{1}-[0-9]{4}|[?]{2}-[0-9]{1}-[0-9]{4}|[?]{2}-[0-9]{2}-[0-9]{4}|[?]{2}-[?]{3}-[?]{4}|[0-9]{2}-[0-9]{1}-[0-9]{4}|[0-9]{2}-[0-9]{2}-[0-9]{4}" )
echo "$start_date"
}


date_res()
{
##passing the parameter to the date_res##
date_res="$1"

##counting the '-' in date and aslo check the ?? in the date and providing the daters as 5,7 0r 8 ##
abc_check=$(echo "$date_res"|sed "s/\//-/g"|sed "s/ /-/g"|grep -o "-"|wc -l)
if [ "$abc_check" -gt 0 ]
then
pat_7="^[?][?]-"
pat_8="^[?][?]-[?][?][?]"
abc_check_7=$(echo "$date_res"|grep -E "$pat_7")
abc_check_8=$(echo "$date_res"|grep -E "$pat_8")
if [ ! -z "$abc_check_7" ]
then
if [ ! -z "$abc_check_8" ]
then
res=5
else
res=7
fi
else
res=8
fi
else
res=""
fi
echo "$res"
}

# to change the format YYYY-MM-DD to YYYY-M-D in case of 01 to 09 DD and MM
date_non_partial(){
    input_nonPar_date="$1"
    day_non_par=$(echo "$input_nonPar_date"|awk -F'-' '{print $3}'|sed -r "s/^0//g")
    year_non_par=$(echo "$input_nonPar_date"|awk -F'-' '{print $1}')
    month_non_par=$(echo "$input_nonPar_date"|awk -F'-' '{print $2}'|sed -r "s/^0//g")
    date_non_par=$(echo "$year_non_par""-""$month_non_par""-""$day_non_par"|sed "s/--//g")
    echo "$date_non_par"
}

# to change the format DD-MM-YYYY to D-M-YYYY in case of 01 to 09 DD and MM
date_partial(){
    input_date=$1
    #day_par=`echo $input_date|sed -r "s/^0//g"| sed -r "s/-0/-/g"| sed -r "s/\/0/\//g"`
    day_par=$(echo "$input_date"|sed -r "s/^0//g")
    echo "$day_par"
}
