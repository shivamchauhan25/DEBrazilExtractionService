#!/bin/bash
#xml file of the pdf
#pdftohtml -xml "$1" pdfxml.xml
source date_format_correct.sh
#creating combing file from xml
< pdfxml.xml grep "Exames laboratoriais realizados em decorrência dos eventos" -A1000|grep "From:" -B1000 -m1|grep -ive "family" -e "page" -e "/b" -e "alexion.com" -e ".png" -e "jpg" >tables

check=$(cat tables)

if [ -z "$check" ]
then
	< pdfxml.xml grep "Exames laboratoriais realizados em decorrência dos eventos" -A1000|grep -ive "family" -e "page" -e "/b" -e "alexion.com" -e ".png" -e "jpg" >tables
fi

< tables sed "s/<text top=/||/g"|sed "s/left=/||/g"|sed "s/width=/||/g"|sed "s/height=/||/g"|sed "s/font=/||/g"|sed "s/\"//g"|sed "s/<\/text>//g"|sed "s/<i>//g"|sed "s/<\/i>//g"|sed "s/&#34;//g">table_data

< table_data awk -F'[|][|]' 'BEGIN {OFS="||"} {print $1,$2,$3,$5,$6}' >lab_concomitant_data

sed -i "s/>/||/g" lab_concomitant_data

sort -n -k3 -t"|" lab_concomitant_data >table_data_sorted


echo "###############################      Exames laboratoriais realizados em decorrência dos eventos  #################"

< table_data_sorted grep "Exames laboratoriais realizados em decorrência dos eventos" -A100|grep "Medicamentos Concomitantes" -B100 |grep -ve "Medicamentos Concomitantes" -e "Exames laboratoriais realizados em decorrência dos eventos" -e "Não aplicável">labtest_data

  < labtest_data grep -e "Nome do exame" -e "Data de realização" -e "Resultado" -e "Valor de referência" >header


< labtest_data grep -ve "Nome do exame" -e "Data de realização" -e "Resultado" -e "Valor de referência" >test_data

awk -F'[|][|]' '$6!=" " {print}' test_data >processed_test_data

sort -n -k2 -t"|" processed_test_data >test_data_sorted

cnt=$(< test_data_sorted wc -l)
if [ "$cnt" -ge "4" ]
then
cnt=$((cnt / 4))
else
	cnt=1
fi
#labtest not applicablepr
labtest_applicable_check=$(< layout grep -i "Exames laboratoriais realizados em decorrência dos eventos"|grep -E -o ".{0,5}Não aplicável"|grep -i "✔\|X\|■")
labtest_applicable_check=$(bash checkbox_module.sh "$labtest_applicable_check")
echo "labtest section not applicable: $labtest_applicable_check"
if [ "$labtest_applicable_check" == 0 ]
then
	echo "[">RT_LABTEST.json
	for ((i=0;i<$cnt;i++))
	do
		< test_data_sorted head -4 >row_data
		cat header >>row_data
		sort -n -k5 -t"|" row_data >test_row_data
		#test name
		nome=$(< test_row_data grep "Nome do exame" -B1|grep -ve "Nome do exame"|awk -F'[|][|]' '{print $6}'|sed 's/\bNQ\b\|\bNq\b\|\bnq\b//g'|sed 's/Não informado//g'|sed 's/\bNÃO QUESTIONADO\b//g'|sed 's/\bnão questionado\b//g'|sed 's/\bNQ\b//g'|sed 's/\bNÃO\b//g'|sed 's/\bNão questionado\b//g'|sed 's/\bnão\b//g'|sed 's/\bNão\b//g'|sed 's/\bNI\b//gI'|sed 's/\bNSI\b//gI'|sed "s/^[[:space:]]//g"|sed "s/[[:space:]]$//g")
		if [ -z "$nome" ]
		then
		nome=""
		fi
		#date of test
		data_de=$(< test_row_data grep "Data de realização" -A1|grep -ve "Data de realização" -e "Nome do exame" -e "Resultado" -e "Valor de referência"|awk -F'[|][|]' '{print $6}'|sed 's/-/0/g'|sed 's./.-.g'|sed "s/^[[:space:]]//g"|sed "s/[[:space:]]$//g")
		#changing the date format
		data_de=$(date_extract "$data_de")
		##changing date and month -> DD-MM-YYYY to D-M-YYYY (removing '0's in day and month for 1-9)	
		data_de=$(date_partial "$data_de")
		if [ -z "$data_de" ]
		then
		data_de=null
		fi
		data_de_res=$(date_res "$data_de")
		if [ -z "$data_de_res" ]
		then
		data_de_res=null
		fi
		ct=$(< test_row_data grep "Data de realização" -A10|grep "Resultado" -B10| grep -ve "Resultado" -e "Data de realização"|wc -l)
		if [ "$ct" -eq "2" ]
		then
			#result information
			check=$(< test_row_data grep "Resultado" -B1|grep -ve "Resultado" -e "Data de realização" -e "Valor de referência"|awk -F'[|][|]' '{print $6}')
			if [[ "$check" =~ [0-9]+ ]]
			then
			result=$(< test_row_data grep "Resultado" -B1|grep -ve "Resultado" -e "Data de realização" -e "Valor de referência"|awk -F'[|][|]' '{print $6}'|tr -s ' ' '\n'|sed 's/[^0-9./]//g'|tr -s '\n' ' '|awk -F ' ' '{print $1}'|sed "s/^[[:space:]]//g"|sed "s/[[:space:]]$//g")
			if [ -z "$result" ]
			then
			result=null
			fi
			result_unit=$(< test_row_data grep "Resultado" -B1|grep -ve "Resultado" -e "Data de realização" -e "Valor de referência"|awk -F'[|][|]' '{print $6}'|sed 's/[0-9\.\,]*//g'|sed 's/\.//g'|awk -F ' ' '{print $1}'|sed 's/\bNÃO QUESTIONADO\b//g'|sed 's/\bnão questionado\b//g'|sed 's/\bNQ\b//g'|sed 's/\bNÃO\b//g'|sed 's/\bNão questionado\b//g'|sed 's/\bnão\b//g'|sed 's/\bNão\b//g'|sed 's/\bNI\b//g'|sed 's/vide campo eventos\|Vide eventos//gI'|sed 's/\bNSI\b//g'|sed 's/\bnq\b//g'|sed 's/\bNq\b//g'|sed 's/\bNQ\b//g'|tr '[:upper:]' '[:lower:]'|sed "s/^[[:space:]]//g"|sed "s/[[:space:]]$//g")
			if [ -z "$result_unit" ]
			then
			result_unit=null
			fi
			else
			result_unit=null
			result=$(< test_row_data grep "Resultado" -B1|grep -ve "Resultado" -e "Data de realização" -e "Valor de referência"|awk -F'[|][|]' '{print $6}'|sed 's/\.//g'|sed 's/\bNÃO QUESTIONADO\b//g'|sed 's/\bnão questionado\b//g'|sed 's/\bNQ\b//g'|sed 's/\bNÃO\b//g'|sed 's/\bNão questionado\b//g'|sed 's/\bnão\b//g'|sed 's/\bNão\b//g'|sed 's/\bNI\b//g'|sed 's/\bNSI\b//g'|sed 's/\bnq\b//g'|sed 's/\bNq\b//g'|sed 's/\bNQ\b//g'|sed "s/^[[:space:]]//g"|sed "s/[[:space:]]$//g")
			if [ -z "$result" ]
			then
			result=null
			fi
			fi
		else
			check=$(< test_row_data grep "Resultado" -A1|grep -ve "Resultado" -e "Data de realização" -e "Valor de referência"|awk -F'[|][|]' '{print $6}')
			if [[ "$check" =~ [0-9]+ ]]
			then
			result=$(< test_row_data grep "Resultado" -A1|grep -ve "Resultado" -e "Data de realização" -e "Valor de referência"|awk -F'[|][|]' '{print $6}'|tr -s ' ' '\n'|sed 's/[^0-9./]//g'|tr -s '\n' ' '|sed 's/[^0-9]*//g'|sed 's/+//g'|awk -F ' ' '{print $1}'|sed "s/^[[:space:]]//g"|sed "s/[[:space:]]$//g")
			if [ -z "$result" ]
			then
			result=null
			fi
			result_unit=$(< test_row_data grep "Resultado" -A1|grep -ve "Resultado" -e "Data de realização" -e "Valor de referência"|awk -F'[|][|]' '{print $6}'|sed 's/[0-9\.\,]*//g'|sed 's/\.//g'|awk -F ' ' '{print $1}'|sed 's/\bNÃO QUESTIONADO\b//g'|sed 's/\bnão questionado\b//g'|sed 's/\bNQ\b//g'|sed 's/\bNÃO\b//g'|sed 's/\bNão questionado\b//g'|sed 's/\bnão\b//g'|sed 's/\bNão\b//g'|sed 's/vide campo eventos\|Vide eventos//gI'|sed 's/\bNI\b//g'|sed 's/\bNSI\b//g'|sed 's/\bnq\b//g'|sed 's/\bNq\b//g'|sed 's/\bNQ\b//g'|sed 's/\bnq\b//g'|tr '[:upper:]' '[:lower:]'|sed "s/^[[:space:]]//g"|sed "s/[[:space:]]$//g")
			if [ -z "$result_unit" ]
			then
			result_unit=null
			fi
			else
			result_unit=null
			result=$(< test_row_data grep "Resultado" -A1|grep -ve "Resultado" -e "Data de realização" -e "Valor de referência"|awk -F'[|][|]' '{print $6}'|sed 's/\.//g'|sed 's/\bNÃO QUESTIONADO\b//g'|sed 's/\bnão questionado\b//g'|sed 's/\bNQ\b//g'|sed 's/\bNÃO\b//g'|sed 's/\bNão questionado\b//g'|sed 's/\bnão\b//g'|sed 's/\bNão\b//g'|sed 's/\bNI\b//g'|sed 's/\bNSI\b//g'|sed 's/\bnq\b//g'|sed 's/\bNq\b//g'|sed 's/\bNQ\b//g'|sed 's/\bnq\b//g'|sed "s/^[[:space:]]//g"|sed "s/[[:space:]]$//g")
			if [ -z "$result" ]
			then
			result=null
			fi
			fi
		fi

			#reference information
			valor=$(< test_row_data grep "Resultado" -A10|grep "Valor de referência" -B10|grep -ve "Valor de referência" -e "Resultado"|awk -F'[|][|]' '{print $6}'|sed 's/\bNÃO QUESTIONADO\b//g'|sed 's/\bnão questionado\b//g'|sed 's/\bNQ\b//g'|sed 's/\bnq\b//g'|sed 's/\bNq\b//g'|sed 's/\bNQ\b//g'|sed 's/\bNÃO\b//g'|sed 's/\bNão questionado\b//g'|sed 's/\bnão\b//g'|sed 's/\bNão\b//g'|sed 's/\bNI\b//g'|sed 's/\bNSI\b//g'|sed 's/vide campo eventos\|Vide eventos//gI'|sed "s/^[[:space:]]//g"|sed "s/[[:space:]]$//g")
			assess_notes=null
			if [[ "$valor" =~ ^[0-9.-]+$ || "$valor" == *"até"* ]]
			then
				if [[ "$valor" =~ .*"até".* || "$valor" =~ .*"-".* ]]
				then
					lowrange=$(echo "$valor"|awk -F 'até|-' '{print $1}')
					if [ -z "$lowrange" ]
					then
						lowrange=null
					fi
					highrange=$(echo "$valor"|awk -F 'até|-' '{print $2}')
					if [ -z "$highrange" ]
					then
						highrange=null
					fi
				else
					lowrange=$valor
					highrange=null
					if [ -z "$lowrange" ]
					then
						lowrange=null
					fi
				fi
			else
				if [ -z "$valor" ]
				then 
					valor=null
				fi
				assess_notes="$valor"
				if [ -z "$assess_notes" ]
				then
					assess_notes=null
				fi
			fi


		echo "Nome do exame : $nome"
		echo "Data de realização : $data_de"
		echo "DATE RES: $data_de_res"
		echo  "Resultado : $result"
		echo "Result unit: $result_unit"
		echo "Valor de referência : $valor"
		echo "low range: $lowrange"
		echo "high range: $highrange"
		echo "Assessment Note: $assess_notes"
		if [ ! -z "$nome" ]
		then
		{
		echo "{"
		echo  \"table_name\":\"RT_LABTEST\", 
		echo \"parent_tag\":\"Labtest_Information\", 
		echo \"seq_num\":null, 
		echo \"TESTNAME\":\"$nome\", 
		echo \"TESTRESULT\":\"$result\", 
		echo \"TESTRESULTUNIT\":\"$result_unit\", 
		echo \"TESTDATE\":\"$data_de\", 
		echo \"TESTDATERES\":\"$data_de_res\", 
		echo \"LOWTESTRANGE\":\"$lowrange\", 
		echo \"HIGHTESTRANGE\":\"$highrange\", 
		echo \"MOREINFORMATION\":\"$assess_notes\" 
		echo "},"
		} >>RT_LABTEST.json
		fi
		echo "======================================================================================="
		sed -i '1,4d' test_data_sorted
	done
	sed -i '$d' RT_LABTEST.json
	echo "}">>RT_LABTEST.json
	echo "]">>RT_LABTEST.json
else
	echo "lab data not applicable"
fi
echo "###################################        Medicamentos Concomitantes   ###########################################################"

#concomitant not applicable
concomitant_applicable_check=$(< layout grep -i "Medicamentos Concomitantes"|grep -E -o ".{0,5}Não aplicável"|grep -i "✔\|X\|■")
concomitant_applicable_check=$(bash checkbox_module.sh "$concomitant_applicable_check")
echo "concomitant section not applicable: $concomitant_applicable_check"
if [ "$concomitant_applicable_check" == 0 ]
then
	< table_data_sorted grep "Medicamentos Concomitantes" -A500|grep "Nome do medicamento" -A500|grep -ve "Nome do medicamento" -e "Dose/ frequência"> concomitant_data

	< concomitant_data awk -F'[|][|]' '{print $2}'|uniq >processed_concomitant
	sequence_num="$2"
	j=0
	for i in $(cat processed_concomitant)
	do
		j=$((j+1))
		if [[ $j == 1 ]]
		then
		   check_coord="||"$i" ||"
		   str_check=`cat concomitant_data | grep "$check_coord"|grep -ie "Data início" -ie "Nome do medicamento" -ie "Data término Dose/ frequência Indicação" -ie "Outros medicamentos utilizados"`
		  if [ ! -z "$str_check" ]
		  then
		    continue
		  fi
		fi
		< concomitant_data grep "$i"|sort -n -k5 -t"|" >sorted_concomitant
		cat con_header >>sorted_concomitant
		sort -n -k5 -t"|" sorted_concomitant >concomitant_rowdata
		#drug name
		nome=$(< concomitant_rowdata grep "Nome do medicamento" -B10|grep -ve "Nome do medicamento"|awk -F'[|][|]' '{print $6}'|sed 's/\bNÃO QUESTIONADO\b//g'|sed 's/\bnão questionado\b//g'|sed 's/\bNQ\b//g'|sed 's/\bNÃO\b//g'|sed 's/\bNão questionado\b//g'|sed 's/\bnão\b//g'|sed 's/\bNão\b//g'|sed 's/\bNI\b//g'|sed 's/\bnq\b//g'|sed 's/\bNq\b//g'|sed 's/\bNQ\b//g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g')
		#start date
		data_inc=$(< concomitant_rowdata grep "Nome do medicamento" -A10|grep "Data início" -B10|grep -ve "Data início" -e "Nome do medicamento"|awk -F'[|][|]' '{print $6}'| sed 's/^[[:space:]]*//g'| sed 's/[[:space:]]*$//g')
		#changing the date format
		data_inc=$(date_extract "$data_inc")
		##changing date and month -> DD-MM-YYYY to D-M-YYYY (removing '0's in day and month for 1-9)
		data_inc=$(date_partial "$data_inc")
		if [ -z "$data_inc" ]
		then
		data_inc=""
		fi
		data_inc_res=$(date_res "$data_inc")
		if [ -z "$data_inc_res" ]
		then
		data_inc_res=null
		fi
		#end date
		data_term=$(< concomitant_rowdata grep "Data término" -A10|grep "Dose/ frequência" -B10|grep -ve "Data término" -e "Dose/ frequência"|awk -F'[|][|]' '{print $6}')
		if [[ $(echo "$data_term"|grep -i -w "continua") || $(echo "$data_term"|grep -w -i "em uso") || $(echo "$data_term"|grep -w -i "conitnua") ]]
		then
		ongoing_con=Yes
		else
		ongoing_con=""
		fi 
		echo "Ongoing concomitant $ongoing_con"
		#changing the date format
		data_term=$(date_extract "$data_term")
		##changing date and month -> DD-MM-YYYY to D-M-YYYY (removing '0's in day and month for 1-9)
		data_term=$(date_partial "$data_term")
		if [ -z "$data_term" ]
		then
		data_term=""
		fi
		data_term_res=$(date_res "$data_term")
		if [ -z "$data_term_res" ]
		then
		data_term_res=null
		fi
		#dose information
		dose=$(< concomitant_rowdata grep "Dose/ frequência" -A10|grep "Indicação" -B10|grep -ve "Indicação" -e "Dose/ frequência"|awk -F'[|][|]' '{print $6}'|sed 's/\bcomp\b\|\bCOMP\b\|\bComp\b/Tablet/g'|sed 's/\bNÃO QUESTIONADO\b//g'|sed 's/\bnão questionado\b//g'|sed 's/comprido\|comprimido/tablet/g'|sed 's/\bNQ\b//g'|sed 's/\bNÃO\b//g'|sed 's/\bNão questionado\b//g'|sed 's/\bnão\b//g'|sed 's/\bNão\b//g'|sed 's/injeção/Injection/g'|sed 's/\bNI\b//g'|sed 's/\bNSI\b//g'|sed 's/\bnq\b//g'|sed 's/\bNq\b//g'|sed 's/\bNQ\b//g'|sed 's/\bNão soube informar a indicação\b//g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g'|sed '/^$/d')
		if [ -z "$dose" ]
		then
		dose=""
		fi
		dosage=$(echo "$dose"|tr -s ' ' '\n'|sed 's/[^0-9./]/ /g'|tr -s '\n' ' '|awk -F ' ' '{print $1}'|sed 's/1\/2/0.5/'|sed "s/^[[:space:]]*//g"|sed "s/[[:space:]]*$//g")
		if [ -z "$dosage" ]
		then
		dosage=null
		fi
		dose_unit=$(echo "$dose"|sed 's/[0-9/\.\,]/ /g'|sed 's/\.//g'|awk -F ' ' '{print $1}'|sed 's/NÃO QUESTIONADO//g'|sed 's/não questionado//g'|sed 's/\bNQ\b//g'|sed 's/\bNÃO\b//g'|sed 's/Não questionado//g'|sed 's/\bnão\b//g'|sed 's/\bNão\b//g'|sed 's/vide campo eventos\|Vide//gI'|sed 's/\bnq\b//g'|sed 's/\bNq\b//g'|sed 's/\bNQ\b//g'|sed 's/\bNSI\b//g'|sed -e 's/\bx\b\|\bX\b//g'|tr '[:upper:]' '[:lower:]'|sed "s/^[[:space:]]//g"|sed "s/[[:space:]]$//g")
		if [ -z "$dose_unit" ]
		then
		dose_unit=null
		fi
		#drug indication
		indi=$(< concomitant_rowdata grep "Indicação" -A10|grep -ve "Indicação"|awk -F'[|][|]' '{print $6}'|sed 's/\bNão soube informar a indicação\b//g'|sed 's/\b(não soube informar quais)\b//g'|sed 's/\bnão soube informar\b//g'|sed 's/\bnão informou qual\b//g'|sed 's/\ba indicação\b//g'|sed 's/\bnão infdrmou\b//g'|sed 's/\bNão houve\b//g'|sed 's/\bnão houve\b//g'|sed 's/\binfdrmou\b//g'|sed 's/\bnão informou\b//g'|sed 's/\bsoube informar\b//g'|sed 's/\binformou\b//g'|sed 's/\bmencionou\b//g'|sed 's/\bquestionada\b//g'|sed 's/\bnão possui\b//g'|sed 's/\baplicou\b//g'|sed 's/vide campo eventos//gI'|sed 's/NÃO QUESTIONADO//g'|sed 's/não questionado//g'|sed 's/\bNQ\b//g'|sed 's/\bNÃO\b//g'|sed 's/Não questionado//g'|sed 's/\bnão\b//g'|sed 's/\bNão\b//g'|sed 's/\bNI\b//g'|sed 's/\bnq\b//g'|sed 's/\bNq\b//g'|sed 's/\bNQ\b//g'|sed 's/\bNSI\b//g'|sed 's/Não soube informar a indicação//g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g'|sed '/^$/d')
		if [ -z "$indi" ]
		then
		indi=null
		fi
		echo "Nome do medicamento : $nome"
		echo "Data início : $data_inc"
		echo "Data inicio res: $data_inc_res"
		echo "Data término : $data_term"
		echo "Data termino res: $data_term_res"
		echo "Dose: $dosage"
		echo "Dose unit: $dose_unit"
		echo "Dose/ frequência : $dose"
		echo "Indicação : $indi"
		if [ ! -z "$nome" ]
		then
		if [[ -z "$dose" && -z "$data_inc" && -z "$data_term" && -z "$ongoing_con" ]]
		then
		sequence_num=$(expr $((sequence_num+1)))
		{
		echo "{"
		echo \"table_name\": \"RT_PRODUCT\", 
		echo \"parent_tag\": \"Product Information\", 
		echo \"seq_num\": \"$sequence_num\", 
		echo \"MEDICINALPRODUCT\": \"$nome\", 
		echo \"DRUGBATCHNUMB\": null, 
		echo \"EXPIRATIONDATE_EXTENSION\": null, 
		echo \"EXPIRATIONDATE_EXTENSIONRES\": null, 
		echo \"DRUGACTIONTAKEN_EXTENSION\": null, 
		echo \"LASTDOSEAE\": null, 
		echo \"LASTDOSEAERES\": null, 
		echo \"DRUGCHARACTERIZATION\": \"Concomitant\" 
		echo "},"
		} >>RT_PRODUCT.json
		if [ ! -z "$indi" ]
		then
		{
		echo "{"
		echo \"table_name\": \"RT_PRODUCT_INDICATION\", 
		echo \"parent_tag\": \"Product Indication\", 
		echo \"prod_seq_num\": \"$sequence_num\", 
		echo \"DRUGINDICATION\": \"$indi\" 
		echo "},"
		} >>RT_Indication.json
		fi
		else
		sequence_num=$(expr $((sequence_num+1)))
		{
		echo "{"
		echo \"table_name\": \"RT_PRODUCT\", 
		echo \"parent_tag\": \"Product Information\", 
		echo \"seq_num\": \"$sequence_num\", 
		echo \"MEDICINALPRODUCT\": \"$nome\", 
		echo \"DRUGBATCHNUMB\": null, 
		echo \"EXPIRATIONDATE_EXTENSION\": null, 
		echo \"EXPIRATIONDATE_EXTENSIONRES\": null, 
		echo \"DRUGACTIONTAKEN_EXTENSION\": null, 
		echo \"LASTDOSEAE\": null, 
		echo \"LASTDOSEAERES\": null, 
		echo \"DRUGCHARACTERIZATION\": \"Concomitant\" 
		echo "}," 
		} >>RT_PRODUCT.json
		if [ ! -z "$indi" ]
		then
		{
		echo "{"
		echo \"table_name\": \"RT_PRODUCT_INDICATION\", 
		echo \"parent_tag\": \"Product Indication\", 
		echo \"prod_seq_num\": \"$sequence_num\", 
		echo \"DRUGINDICATION\": \"$indi\" 
		echo "},"
		} >>RT_Indication.json
		fi
		{
		echo "{"
		echo \"table_name\": \"RT_Dose\", 
		echo \"parent_tag\": \"Dose Information\", 
		echo \"prod_seq_num\": \"$sequence_num\", 
		echo \"DOSEONGOING_EXTENSION\": \"$ongoing_con\", 
		echo \"DRUGSTARTDATE\": \"$data_inc\", 
		echo \"DRUGSTARTDATERES\": \"$data_inc_res\", 
		echo \"DRUGSTRUCTUREDOSAGENUMB\": \"$dosage\", 
		echo \"DRUGSTRUCTUREDOSAGEUNIT\": \"$dose_unit\", 
		echo \"DRUGDOSAGETEXT\": \"$dose\", 
		echo \"DRUGADMINISTRATIONROUTE\": null, 
		echo \"DRUGENDDATE\": \"$data_term\", 
		echo \"DRUGENDDATERES\": \"$data_term_res\" 
		echo "}," 
		} >>RT_DOSE.json
		fi
		else
		echo "No concomitant data"
		fi
		echo "======================================================================================="
	done
else
	echo "Concomitant data not applicable"
fi
