#!/bin/bash
#creating html combing file 
python3 htmlcombpython.py "$1"
#checkbox detection and extraction
#python3 CheckBox_Extraction_CL.py "$1" .
#layout file from checkbox marked pdf
pdftotext -layout "$1" layout
#xml file of the pdf
pdftohtml -xml "$1" pdfxml.xml
#date format script
source date_format_correct.sh

#product information field extraction
product_info_extract(){
if [[ -z $(< pdfxml.xml grep -i "Fase Inicial") ]]
then
< pdfxml.xml grep -i "Data de término:" -A1000|grep -i "</page>" -B1000 -m1>product_alexion
else
< pdfxml.xml grep -i "Fase Inicial" -A1000 -m1|grep -i "</page>" -B1000 -m1|grep -i "Fase Inicial" -A15 -m1>product_alexion
fi
line_count=$(< product_alexion wc -l)
for((i=1;i<="$line_count";i++))
do
	line=$(< product_alexion head -1)
	top=$(echo "$line"|awk -F 'left' '{print $1}'|awk -F 'top=' '{print $2}'|sed 's/\"//g')
	left=$(echo "$line"|awk -F 'width' '{print $1}'|awk -F 'left=' '{print $2}'|sed 's/\"//g')
	if [[ $top -le "$1" && $top -ge "$2" && $left -lt "$3" ]]
	then
		result="$line"
		#echo "Result:" $result
	fi
	sed -i "1d" product_alexion
done
value=$(echo "$result"|awk -F '>' '{print $2}'|awk -F '<' '{print $1}')
echo "$value"
}

#get heading coordinates
get_coordinate(){
< pdfxml.xml grep -i "Detalhar os eventos apresentados, data de início, data de término e a evolução (recuperado, não recuperado, etc) de " -m1 -A10000|grep -i "</page>" -m1 -B10000>page_number3
awk -F'[|][|]' '$6!=" " {print}' page_number3 >drugresult_reference_data
sort -n -k2 -t"|" drugresult_reference_data >sorted_drugresult_reference_data
line_count=$(< sorted_drugresult_reference_data wc -l)
for((i=1;i<="$line_count";i++))
do
line=$(< sorted_drugresult_reference_data head -1)
if [[ ! -z $(echo "$line"|grep -i -w "$3") ]]
then
top=$(echo "$line"|awk -F 'left' '{print $1}'|awk -F 'top=' '{print $2}'|sed 's/\"//g')
if [[ $top -ge "$1" && $top -lt "$2" ]]
then
result="$line"
fi
fi
sed -i "1d" sorted_drugresult_reference_data
done
value=$(echo "$result"|awk -F 'width' '{print $1}'| awk -F 'left=' '{print $2}'|sed 's/\"//g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g')
echo "$value"
}

#lot expiration field extraction
lot_expiry_info_extract(){
< pdfxml.xml grep -i "A Farmacovigilância pode entrar em contato com o médico?" -A10000|grep -i "</page>" -m1 -B100>lot_expiry_info
line_count=$(< lot_expiry_info wc -l)
for((i=1;i<="$line_count";i++))
do
line=$(< lot_expiry_info head -1)
top=$(echo "$line"|awk -F 'left' '{print $1}'|awk -F 'top=' '{print $2}'|sed 's/\"//g')
left=$(echo "$line"|awk -F 'width' '{print $1}'|awk -F 'left=' '{print $2}'|sed 's/\"//g')
if [[ $top -ge "$1" && $top -lt "$2" && $left -gt "$3" && $left -lt "$4" ]]
then
result="$line"
fi
sed -i "1d" lot_expiry_info
done
value=$(echo "$result"|awk -F '>' '{print $2}'|awk -F '<' '{print $1}'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g')
echo "$value"
}

#reason of hospitalization 
get_hospitalization_reason(){
< pdfxml.xml grep -i "Motivo da hospitalização:" -A10000|grep -i "</page>" -m1 -B100>hospitalization_info
line_count=$(< hospitalization_info wc -l)
for((i=1;i<="$line_count";i++))
do
line=$(< hospitalization_info head -1)
top=$(echo "$line"|awk -F 'left' '{print $1}'|awk -F 'top=' '{print $2}'|sed 's/\"//g')
left=$(echo "$line"|awk -F 'width' '{print $1}'|awk -F 'left=' '{print $2}'|sed 's/\"//g')
if [[ $top -ge "$1" && $top -lt "$2" && $left -gt "$3" && $left -lt "$4" ]]
then
result="$line"
fi
sed -i "1d" hospitalization_info
done
value=$(echo "$result"|awk -F '>' '{print $2}'|awk -F '<' '{print $1}'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g')
echo "$value"
}

echo "[">finaljson.json

#reporter information
#rt reporter
#alexion reporter
alx_rep=$(< layout grep -i "Nome do Relator Alexion"|awk -F 'Nome do Relator Alexion' '{print $2}'|sed 's/\"//g'|sed 's/\bNI\b//g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g'|sed '/^$/d')
if [ -z "$alx_rep" ]
then
alx_rep=null
fi 
echo "Alexion reporter:" $alx_rep
#reporter
rep_name=$(< layout grep -i "Relator" -A1000|grep  -i "Nome do relator:" |awk -F 'Nome do relator' '{print $2}'|sed 's/://g'|sed 's/\bNI\b//g'|sed 's/\bNQ\b//g'|sed 's/\bnq\b//g'|sed 's/\bNq\b//g'|sed 's/\"//g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g'|sed '/^$/d')
#splitting name into first,middle,last name
len=$(echo "$rep_name"|wc -w)
if [ "$len" == 2 ]
then
rep_fn=$(echo "$rep_name"|awk -F ' ' '{print $1}'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g')
if [ -z "$rep_fn" ]
then
rep_fn=null
fi
rep_mn=null
rep_ln=$(echo "$rep_name"|awk -F ' ' '{print $2}'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g')
if [ -z "$rep_ln" ]
then
rep_ln=null
fi
else
rep_fn=$(echo "$rep_name"|awk -F ' ' '{print $1}'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g')
if [ -z "$rep_fn" ]
then
rep_fn=null
fi
rep_mn=$(echo "$rep_name"|awk -F ' ' '{print $2}'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g')
if [ -z "$rep_mn" ]
then
rep_mn=null
fi
rep_ln=$(echo "$rep_name"|awk -F ' ' '{print $3, $4, $5, $6, $7}'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g')
if [ -z "$rep_ln" ]
then
rep_ln=null
fi
fi
echo "reporter first name:" $rep_fn
echo "reporter middle name:" $rep_mn
echo "reporter last name:" $rep_ln
#reporter type
relationship=$(< layout grep -i "Relator" -A1000|grep -i "Grau de relacionamento:"|awk -F 'Grau de relacionamento' '{print $2}'|sed 's/NÃO QUESTIONADO//g'|sed 's/não questionado//g'|sed 's/\bNQ\b//g'|sed 's/\bNÃO\b//g'|sed 's/Não questionado//g'|sed 's/\bnão\b//g'|sed 's/\bNão\b//g'|sed 's/\bNI\b//g'|sed 's/\bNQ\b//g'|sed 's/Não Questionado//g'|sed 's/conhecido//g'|sed 's/o próprio paciente/Paciente/g'|sed 's/\bnq\b//g'|sed 's/\bNq\b//g'|sed 's/://g'|sed 's/\"//g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g'|sed '/^$/d')
check=$(echo "$relationship"|tr '[:upper:]' '[:lower:]')
if [[ "$check" == "filha" || "$check" == "família/ cuidador" ]]
then
relationship="Family / Caregiver"
elif [[ "$check" == "médico" ]]
then
relationship="Physician"
elif [[ "$check" == "outro profissional da saúde" ]]
then
relationship="Other health professional"
fi
if [ -z "$relationship" ]
then
relationship=null
fi
echo "Relationship:" $relationship
#reporter profession
occupation=$(< layout grep -i "Relator" -A1000|grep -i "Profissão:"|awk -F 'Profissão' '{print $2}'|sed 's/NÃO QUESTIONADO//g'|sed 's/não questionado//g'|sed 's/\bNQ\b//g'|sed 's/\bNÃO\b//g'|sed 's/Não questionado//g'|sed 's/\bnão\b//g'|sed 's/\bNão\b//g'|sed 's/\bNI\b//g'|sed 's/\bnq\b//g'|sed 's/\bNq\b//g'|sed 's/\bNQ\b//g'|sed 's/Não Questionado//g'|sed 's/\bNI\b//g'|sed 's/://g'|sed 's/\"//g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g'|sed '/^$/d')
if [ -z "$occupation" ]
then
occupation=null
fi
echo "Occupation:" $occupation
#reporter email
rep_mail=$(< layout grep -i "Relator" -A1000|grep -i "E-mail:" -m1|awk -F 'E-mail' '{print $2}'|sed 's/\bNI\b//g'|sed 's/\bNQ\b//g'|sed 's/\bnq\b//g'|sed 's/\bNq\b//g'|sed 's/://g'|sed 's/\"//g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g'|sed '/^$/d')
if [ -z "$rep_mail" ]
then
rep_mail=null
fi
echo "Reporter Email:" $rep_mail
#reporter phone number
rep_phone=$(< layout grep -i "Relator" -A1000|grep -i "Telefone:" -m1|awk -F 'Telefone' '{print $2}'|sed 's/\bNI\b//g'|sed 's/\bnq\b//g'|sed 's/\bNq\b//g'|sed 's/\bNQ\b//g'|sed 's/://g'|sed 's/\"//g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g'|sed '/^$/d')
if [ -z "$rep_phone" ]
then
rep_phone=null
fi
echo "Reporter Phone no:" $rep_phone
#communication correspondance
inbound_co=$(< layout grep -i "Tipo de contato" -A10 -m1|grep -i "Efetuado" -B10 -m1|grep -iaob "Efetuado"|awk -F ':' '{print $1}')
outbound_co=$(< layout grep -i "Tipo de contato" -A10 -m1|grep -i "Recebido" -B10 -m1|grep -iaob "Recebido"|awk -F ':' '{print $1}')
inbound=$(< layout grep -i "Tipo de contato" -A10 -m1|grep -i "Efetuado" -B10 -m1|awk '{val=substr($0,0,'"$((inbound_co-30))"');print val}'|grep -i "✔\|X\|■")
done=$(bash checkbox_module.sh "$inbound")
echo "Communication inbound: $done"
outbound=$(< layout grep -i "Tipo de contato" -A10 -m1|grep -i "Relator" -B100 -m1|awk '{val=substr($0,'"$((inbound_co+10))"','"$((outbound_co-20))"');print val}'|grep -i "✔\|X\|■")
received=$(bash checkbox_module.sh "$outbound")
echo "Communication outbound: $received"
if [ "$done" == 1 ]
then
contact_type="I"
elif [ "$received" == 1 ]
then
contact_type="O"
else
contact_type=null
fi
echo "Contact Type:" $contact_type

echo "{">RT_REPORTER.json
{

echo \"table_name\": \"RT_REPORTER\",
echo \"parent_tag\": \"Reporter\",
echo \"seq_num\": null,
echo \"REPORTSENTBYHCP_EXTENSION\": null,
echo \"REPORTERTYPE\": \"$relationship\",
echo \"QUALIFICATION\": \"$occupation\",
echo \"PRIMARYFLG\":\"Yes\",
echo \"REPORTERGIVENAME\": \"$rep_fn\",
echo \"REPORTERMIDDLENAME\": \"$rep_mn\",
echo \"REPORTERFAMILYNAME\": \"$rep_ln\",
echo \"REPORTERSTREET\":null,
echo \"REPORTERPHONE_EXTENSION\": \"$rep_phone\",
echo \"REPORTERFAX_EXTENSION\":null,
echo \"REPORTEREMAIL_EXTENSION\": \"$rep_mail\",
echo \"INTERMEDIARYNAME\" : \"$alx_rep\",
echo \"COMMUNICATIONCORRESPONDENCE\" :\"$contact_type\"
echo "}"
} >>RT_REPORTER.json
jsonlint-php RT_REPORTER.json
if [ $? -eq 0 ]
then
cat RT_REPORTER.json >>finaljson.json
echo "," >>finaljson.json
else
echo "{">RT_REPORTER.json
{
echo \"table_name\": \"RT_REPORTER\",
echo \"parent_tag\": \"Reporter\",
echo \"seq_num\": null,
echo \"REPORTSENTBYHCP_EXTENSION\": null,
echo \"REPORTERTYPE\": null,
echo \"QUALIFICATION\": null,
echo \"PRIMARYFLG\":null,
echo \"REPORTERGIVENAME\": null,
echo \"REPORTERMIDDLENAME\": null,
echo \"REPORTERFAMILYNAME\": null,
echo \"REPORTERSTREET\":null,
echo \"REPORTERPHONE_EXTENSION\": null,
echo \"REPORTERFAX_EXTENSION\":null,
echo \"REPORTEREMAIL_EXTENSION\": null,
echo \"INTERMEDIARYNAME\" : null,
echo \"COMMUNICATIONCORRESPONDENCE\" :null
echo "},"
} >>RT_REPORTER.json
cat RT_REPORTER.json>>finaljson.json
fi

#Patient Information
#RT Patient
#patient name
patient_name=$(< layout grep -i "Paciente" -A1000|grep -i "Nome do paciente:"|awk -F 'Nome do paciente' '{print $2}'|sed 's/NÃO QUESTIONADO//g'|sed 's/não questionado//g'|sed 's/\bNQ\b//g'|sed 's/\bnq\b//g'|sed 's/\bNq\b//g'|sed 's/\bNQ\b//g'|sed 's/\bNÃO\b//g'|sed 's/Não questionado//g'|sed 's/\bnão\b//g'|sed 's/\bNão\b//g'|sed 's/\bNI\b//g'|sed 's/\bNQ\b//g'|sed 's/Não Questionado//g'|sed 's/://g'|sed 's/\"//g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g'|sed '/^$/d')
#splitting name into first,middle,last name
len=$(echo "$patient_name"|wc -w)
if [ "$len" == 2 ]
then
pat_fn=$(echo "$patient_name"|awk -F ' ' '{print $1}'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g')
if [ -z "$pat_fn" ]
then
pat_fn=null
fi
pat_mn=null
pat_ln=$(echo "$patient_name"|awk -F ' ' '{print $2}'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g')
if [ -z "$pat_ln" ]
then
pat_ln=null
fi
else
pat_fn=$(echo "$patient_name"|awk -F ' ' '{print $1}'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g')
if [ -z "$pat_fn" ]
then
pat_fn=null
fi
pat_mn=$(echo "$patient_name"|awk -F ' ' '{print $2}'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g')
if [ -z "$pat_mn" ]
then
pat_mn=null
fi
pat_ln=$(echo "$patient_name"|awk -F ' ' '{print $3, $4, $5, $6, $7}'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g')
if [ -z "$pat_ln" ]
then
pat_ln=null
fi
fi
echo "patient first name:" $pat_fn
echo "patient middle name:" $pat_mn
echo "patient last name:" $pat_ln
#gender
male_co=$(< layout grep -i "Paciente" -A100 -m1 |grep -i "Masculino" -m1|grep -iaob "Masculino"|awk -F ':' '{print $1}')
female_co=$(< layout grep -i "Paciente" -A100 -m1 |grep -i "Feminino" -m1|grep -iaob "Feminino"|awk -F ':' '{print $1}')
unknown=$(< layout grep -i "Paciente" -A100 -m1 |grep -i "Desconhecido" -m1|grep -iaob "Desconhecido"|awk -F ':' '{print $1}')
male=$(< layout grep -i "Paciente" -m1 -A100|grep -i "Masculino" -m1 -B100|grep -i "Alexion:" -A100|awk '{val=substr($0,0,'"$male_co"');print val}'|grep -i "✔\|X\|■")
male=$(bash checkbox_module.sh "$male")
female=$(< layout grep -i "Paciente" -m1 -A100|grep -i "Feminino" -m1 -B100|grep -i "Alexion:" -A100|awk '{val=substr($0,'"$male_co"','"$female_co"');print val}'|sed 's/Masculino//g'|grep -i "✔\|X\|■")
female=$(bash checkbox_module.sh "$female")
unknown=$(< layout grep -i "Paciente" -m1 -A100|grep -i "Desconhecido" -m1 -B100|grep -i "Alexion:" -A100|awk '{val=substr($0,'"$female_co"',1000);print val}'|sed 's/Feminino//g'|grep -iv "Alexion:"|grep -i "✔\|X\|■")
unknown=$(bash checkbox_module.sh "$unknown")
if [ "$male" == 1 ]
then
gender=Male
elif [ "$female" == 1 ]
then
gender=Female
elif [ "$unknown" == 1 ]
then
gender=UNK
else
gender=null
fi
echo "Gender:" $gender
#patient weight
pat_weight=$(< layout grep -i "Paciente" -A1000|grep -i "Peso:"|awk -F 'Altura' '{print $1}'|awk -F 'Peso' '{print $2}'|grep -iv "Binary file (standard input) matches"|sed 's/://g'|sed 's/\"//g'|sed 's/[A-Za-z]*//g'|sed 's/\,/\./g'|sed 's/ã//g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g'|sed '/^$/d')
if [[ "$pat_weight" =~ \  ]]
then
pat_weight=""
fi
if [ -z "$pat_weight" ]
then
pat_weight=null
fi
echo "Patient Weight:" $pat_weight
#patient height
height_co=$(< layout grep -i "Altura:"|grep -iaob "Altura:"|awk -F ':' '{print $1}')
height_co2=$(< layout grep -i "Paciente" -A1000|grep -i "Alexion:" -m1|grep -aiob "Alexion"|awk -F ':' '{print $1}')
pat_height=$(< layout grep -i "Paciente" -A1000|grep -i "Idade:" -B1000 -m1|grep -i "Altura:" -A1000|awk '{val=substr($0,'"$height_co"','$((height_co2-50))');print val}'|grep -iv "altura"|grep -iv "idade"|grep -iv "Binary file (standard input) matches"|sed 's/[A-Za-z]*//g'|sed 's/\"//g'|sed 's/ã//g'|sed 's/\,//g'|sed 's/\.//g'|sed 's/✔\|X\|■//g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g'|sed '/^$/d')
if [[ "$pat_height" =~ \  ]]
then
pat_height=""
fi
if [ -z "$pat_height" ]
then
pat_height=null
fi
echo "Patient Height:" $pat_height
#patient dob
pat_dob=$(< layout grep -i "Paciente" -A1000|grep -i "data de" -m1|awk -F 'Idade' '{print $1}'|awk -F 'Data de' '{print $2}'|sed 's/\"//g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g'|sed 's./.-.g'|sed '/^$/d')
#changing date format
pat_dob=$(date_extract "$pat_dob")
##changing date and month -> DD-MM-YYYY to D-M-YYYY(removing '0's in day and month for 1-9)
pat_dob=$(date_partial "$pat_dob")
if [ -z "$pat_dob" ]
then
pat_dob=null
fi
echo "Date of Birth:" $pat_dob
dob_res=$(date_res "$pat_dob")
if [ -z "$dob_res" ]
then
dob_res=null
fi
echo "DOB res:" $dob_res
#patient age
pat_age=$(< layout grep -i "Paciente" -A1000|grep -i "idade:" -m1|awk '{val=substr($0,'"$height_co"','$((height_co2-50))');print val}'|awk -F 'Idade' '{print $2}'|grep -iv "Binary file (standard input) matches"|sed 's/://g'|sed 's/\"//g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g'|sed '/^$/d'|tr -dc '[0-9]')
if [[ "$pat_age" =~ \  ]]
then
pat_age=""
fi
if [ -z "$pat_age" ]
then
pat_age=""
fi
echo "Patient Age:" "$pat_age"
age_unit=$(< layout grep -i "Paciente" -A1000|grep -i "idade:" -m1|awk '{val=substr($0,'"$height_co"','$((height_co2-50))');print val}'|awk -F 'Idade' '{print $2}'|sed 's/\bNI\b//g'|sed 's/://g'|sed 's/\"//g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g'|sed '/^$/d'|grep -io -E "semana|semanas|dias|meses|mês")
if [ "$(echo "$age_unit"|grep -w -i "semana")" ]
then
age_unit=Week
elif [ "$(echo "$age_unit"|grep -w -i "semanas")" ]
then
age_unit=Weeks
elif [ "$(echo "$age_unit"|grep -w -i "dias")" ]
then
age_unit=Days
elif [ "$(echo "$age_unit"|grep -w -i "meses")" ]
then
age_unit=Months
elif [ "$(echo "$age_unit"|grep -w -i "mês")" ]
then
age_unit=Month
else
age_unit=""
fi
if [ -z "$age_unit" ]
then
if [ ! -z "$pat_age" ]
then
age_unit=Years
else
age_unit=null
fi
fi
echo "Age unit:" $age_unit
#member of psp
yes=$(< layout grep -i " Paciente é membro do PSP?" -m1 -A10|grep -i "Gestação / Lactação" -m1 -B100|grep -iv "Paciente é membro do PSP?"|grep -iv "Gestação / Lactação"|awk '{val=substr($0,0,'"$male_co"');print val}'|grep -i "✔\|X\|■")
yes=$(bash checkbox_module.sh "$yes")
no=$(< layout grep -i " Paciente é membro do PSP?" -m1 -A10|grep -i "Gestação / Lactação" -m1 -B100|grep -iv "Paciente é membro do PSP?"|grep -iv "Gestação / Lactação"|grep -i "Não" -m1|grep -E -o ".{0,5}Não"|grep -i "✔\|X\|■")
no=$(bash checkbox_module.sh "$no")
if [ "$no" -eq 0 ]
then
no=$(< layout grep -i " Paciente é membro do PSP?" -m1 -A10|grep -i "Gestação / Lactação" -m1 -B100|grep -iv "Paciente é membro do PSP?"|grep -iv "Gestação / Lactação"|grep -i "Não" -m1|grep -E -o ".{0,5}Não"|grep -i "✔\|X\|■")
no=$(bash checkbox_module.sh "$no")
fi
if [ "$yes" == 1 ]
then
member="Yes"
elif [ "$no" == 1 ]
then
member="No"
else
member=null
fi
echo "Is the patient a member of the PSP?:" $member
#patient id
pm_no=$(< layout grep -i "Paciente" -A1000|grep -i "Número do PM:"|awk -F 'Número do PM' '{print $2}'|sed 's/\bNA\b//g'|sed 's/://g'|sed 's/\"//g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g'|sed '/^$/d')
if [ -z "$pm_no" ]
then
pm_no=null
fi
echo "PM Number:" $pm_no
#Gestação / Lactação 
gestation_not_applicable=$(< layout grep -i "Gestação / Lactação" -A100|grep -i "Paciente está gestante?" -B1000|grep -iv "Paciente está gestante?"|grep -E -o ".{0,10}Não aplicável"|grep -i "✔\|X\|■")
gestation_not_applicable=$(bash checkbox_module.sh "$gestation_not_applicable")
echo "Gestation not applicable: $gestation_not_applicable"
if [ "$gestation_not_applicable" == 1 ]
then
#is patient prgenant
patient_preg=null
echo "Is patient pregnant:" $patient_preg
#lmp date
last_date=null
echo "last menstruation date:" $last_date
#pregnancy duration
preg_dur=null
preg_unit=null
echo "Duration of pregnancy:" $preg_dur
echo "Preg unit:" $preg_unit
#is patient lactating
patient_lact=null
echo "Is patient lactating?:" $patient_lact
#expected delivery date
expected_delivery_date=null
echo "Expected delivery date:" $expected_delivery_date
#paternal exposure
paternal_exposure=null
echo "Paternal exposure:" $paternal_exposure
else
#is patient pregnant
preg_sim_co=$(< layout grep -i "Gestação / Lactação" -A1000|grep -i "Paciente está gestante?" -A100|grep -i "Sim" -m1|grep -iaob "Sim"|awk -F ':' '{print $1}')
preg_sim_co=$((preg_sim_co+10))
#
sim=$(< layout grep -i "Gestação / Lactação" -A1000|grep -i "Paciente está gestante?" -A100|grep -i "Sim" -m1 -B10|awk '{val=substr($0,0,'"$preg_sim_co"');print val}'|grep -i "✔\|X\|■")
sim=$(bash checkbox_module.sh "$sim")
no=$(< layout grep -i "Gestação / Lactação" -A1000|grep -i "Paciente está gestante?" -A100|grep -i "Não" -m1|awk -F 'Não' '{print $1}'|awk -F 'Sim' '{print $2}'|grep -i "✔\|X\|■")
no=$(bash checkbox_module.sh "$no")
preg_not_applicable=$(< layout grep -i "Gestação / Lactação" -A1000|grep -i "Paciente está gestante?" -A100|grep -i "Não aplicável" -m1|grep -E -o ".{0,10}Não aplicável"|grep -i "✔\|X\|■")
preg_not_applicable=$(bash checkbox_module.sh "$preg_not_applicable")
questionado=$(< layout grep -i "Gestação / Lactação" -A1000|grep -i "Paciente está gestante?" -A100|grep -i "Não questionado" -m1|awk -F 'Não questionado' '{print $1}'|awk -F 'Não aplicável' '{print $2}'|grep -i "✔\|X\|■")
questionado=$(bash checkbox_module.sh "$questionado")
if [ "$sim" == 1 ]
then
patient_preg=1
elif [ "$no" == 1 ]
then
patient_preg=0
elif [ "$preg_not_applicable" == 1 ]
then
patient_preg=3
elif [ "$questionado" == 1 ]
then
patient_preg=""
else
patient_preg=null
fi
echo "Is patient pregnant:" $patient_preg
#LMP date
last_date=$(< layout grep -i "Gestação / Lactação" -A1000|grep -i "Data da última menstruação"|awk -F 'DD/MM/AAAA' '{print $2}'|sed 's/(\|)//g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g'|sed '/^$/d')
#changing the date format
last_date=$(date_extract "$last_date")
##changing date and month -> DD-MM-YYYY to D-M-YYYY(removing '0's in day and month for 1-9)
last_date=$(date_partial "$last_date")
if [ -z "$last_date" ]
then
last_date=null
fi
echo "last menstruation date:" $last_date
#lmp date res
lmp_res=$(date_res "$last_date")
if [ -z "$lmp_res" ]
then
lmp_res=null
fi
echo "lmp res:" $lmp_res
#pregnancy duration
preg_dur=$(< layout grep -i "Gestação / Lactação" -A1000|grep -i "Semanas de gestação na data do relato:" -A1000|grep -i "Semanas de gestação na data do relato:"|awk -F 'na data do relato' '{print $2}'|sed 's/://g'|sed 's/\"//g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g'|sed '/^$/d'|tr -dc "[0-9]")
if [ -z "$preg_dur" ]
then
preg_dur=null
fi
echo "Duration of pregnancy:" $preg_dur
preg_unit=$(< layout grep -i "Gestação / Lactação" -A1000|grep -i "Semanas de gestação na data do relato:" -A1000|grep -i "Semanas de gestação na data do relato:"|awk -F 'na data do relato' '{print $2}'|sed 's/://g'|sed 's/\"//g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g'|sed '/^$/d'|grep -io -E "weeks|week|days|months|month"|tr '[:upper:]' '[:lower:]')
preg_unit="${preg_unit^}"
if [ -z "$preg_unit" ]
then
if [ "$preg_dur" != null ]
then
preg_unit=Weeks
else
preg_unit=null
fi
fi
echo "Preg unit:" $preg_unit

#is patient lactating
lact_sim_co=$(< layout grep -i "Gestação / Lactação" -A1000|grep -i "Paciente está lactante?" -A100|grep -i "Sim" -m1|grep -iaob "Sim"|awk -F ':' '{print $1}')
lact_sim_co=$((lact_sim_co+10))
#
sim=$(< layout grep -i "Paciente está lactante?" -A100|grep -i "Sim" -m1 -B10|awk '{val=substr($0,0,'"$lact_sim_co"');print val}'|grep -i "✔\|X\|■")
sim=$(bash checkbox_module.sh "$sim")
no=$(< layout grep -i "Paciente está lactante?" -A100|grep -i "Não" -m1|awk -F 'Não' '{print $1}'|awk -F 'Sim' '{print $2}'|grep -i "✔\|X\|■")
no=$(bash checkbox_module.sh "$no")
aplica=$(< layout grep -i "Paciente está lactante?" -A100|grep -i "Não aplicável" -m1|grep -E -o ".{0,5}Não aplicável"|grep -i "✔\|X\|■")
aplica=$(bash checkbox_module.sh "$aplica")
questionado=$(< layout grep -i "Paciente está lactante?" -A100|grep -i "Não questionado" -m1|grep -E -o ".{0,5}Não questionado"|grep -i "✔\|X\|■")
questionado=$(bash checkbox_module.sh "$questionado")
if [ "$sim" == 1 ]
then
patient_lact=1
elif [ "$no" == 1 ]
then
patient_lact=0
elif [ "$questionado" == 1 ]
then
patient_lact=""
elif [ "$aplica" == 1 ]
then
patient_lact=""
else
patient_lact=null
fi
echo "Is patient lactating?:" $patient_lact
#expected delivery date
expected_delivery_date=$(< layout grep -i "Gestação / Lactação" -A1000|grep -i "Data estimada do parto" -A1000|grep -i "Data estimada do parto"|awk -F 'DD/MM/AAAA' '{print $2}'|sed 's/(\|)//g'|sed 's/\./-/g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g'|sed '/^$/d')
#changing the date format
expected_delivery_date=$(date_extract "$expected_delivery_date")
##changing date and month -> DD-MM-YYYY to D-M-YYYY(removing '0's in day and month for 1-9)
expected_delivery_date=$(date_partial "$expected_delivery_date")
echo "Expected delivery date:" "$expected_delivery_date"
#paternal exposure
sim=$(< layout grep -i "Exposição paterna?" -A100|grep -i "sim" -m1|grep -E -o ".{0,5}Sim"|grep -i "✔\|X\|■")
sim=$(bash checkbox_module.sh "$sim")
no=$(< layout grep -i "Exposição paterna?" -A100|grep -i "Não" -m1|awk -F 'Não' '{print $1}'|awk -F 'Sim' '{print $2}'|grep -i "✔\|X\|■")
no=$(bash checkbox_module.sh "$no")
aplicavel=$(< layout grep -i "Exposição paterna?" -A100|grep -i "Não aplicável" -m1|grep -E -o ".{0,10}Não aplicável"|grep -i "✔\|X\|■")
aplicavel=$(bash checkbox_module.sh "$aplicavel")
not_questionado=$(< layout grep -i "Exposição paterna?" -A100|grep -i "Não questionado" -m1|grep -E -o ".{0,10}Não questionado"|grep -i "✔\|X\|■")
not_questionado=$(bash checkbox_module.sh "$not_questionado")
if [ "$sim" == 1 ]
then
paternal_exposure="Yes"
elif [ "$no" == 1 ]
then
paternal_exposure="No"
elif [ "$aplicavel" == 1 ]
then
paternal_exposure="Not applicable"
elif [ "$not_questionado" == 1 ]
then
paternal_exposure="Unquestioned"
else
paternal_exposure=null
fi
echo "Paternal exposure:" $paternal_exposure
fi

#patient HCP consent
reference_top_co=$(< pdfxml.xml grep -i "O médico está ciente dos eventos apresentados pelo paciente?"|awk -F 'left' '{print $1}'|awk -F 'top=' '{print $2}'|sed 's/\"//g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g')
reference_top_co=$((reference_top_co+40))
reference_bottom_co=$(< pdfxml.xml grep -i "A Farmacovigilância pode entrar em contato com o médico?"|awk -F 'left' '{print $1}'|awk -F 'top=' '{print $2}'|sed 's/\"//g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g')

physician_yes_co=$(get_coordinate "$reference_top_co" "$reference_bottom_co" "Sim")
physician_no_co=$((physician_yes_co+110))
physician_unknown_co=$(get_coordinate "$reference_top_co" "$reference_bottom_co" "Não Questionado")

physician_yes_checkbox=$(lot_expiry_info_extract "$reference_top_co" "$reference_bottom_co" "0" "$physician_yes_co")
physician_yes_checkbox=$(bash checkbox_module.sh "$physician_yes_checkbox")
physician_no_checkbox=$(lot_expiry_info_extract "$reference_top_co" "$reference_bottom_co" "$physician_yes_co" "$physician_no_co")
physician_no_checkbox=$(bash checkbox_module.sh "$physician_no_checkbox")
physician_unknown_checkbox=$(lot_expiry_info_extract "$reference_top_co" "$reference_bottom_co" "$physician_no_co" "$physician_unknown_co")
physician_unknown_checkbox=$(bash checkbox_module.sh "$physician_unknown_checkbox")
if [ "$physician_yes_checkbox" == 1 ]
then
hcp_consent="Yes"
elif [ "$physician_no_checkbox" == 1 ]
then
hcp_consent="No"
elif [ "$physician_unknown_checkbox" == 1 ]
then
hcp_consent="Unknown"
else
hcp_consent=null
fi
echo "Patient HCP consent:" $hcp_consent

echo "{">RT_PATIENT.json
{
echo \"table_name\": \"RT_PATIENT\", 
echo \"parent_tag\": \"Patient\", 
echo \"PATIENTINITIAL\": null, 
echo \"PATIENTFIRSTNAME\": \"$pat_fn\", 
echo \"PATIENTMIDDLENAME\": \"$pat_mn\", 
echo \"PATIENTLASTNAME\": \"$pat_ln\", 
echo \"PATIENTONSETAGE\": \"$pat_age\", 
echo \"PATIENTONSETAGEUNIT\": \"$age_unit\", 
echo \"PATIENTSEX\": \"$gender\", 
echo \"PATIENTBIRTHDATE\": \"$pat_dob\", 
echo \"PATIENTBIRTHDATERES\": \"$dob_res\", 
echo \"PATIENTWEIGHT\": \"$pat_weight\", 
echo \"PATIENTHEIGHT\": \"$pat_height\", 
echo \"PATIENTAGEGROUP\": null, 
echo \"PATIENTID\": \"$pm_no\", 
echo \"ISPSPMEMBER\": \"$member\", 
echo \"HCPCONSENT\": \"$hcp_consent\", 
echo \"PREGNANT_EXTENSION\": \"$patient_preg\", 
echo \"PATIENTLASTMENSTRUALDATE\": \"$last_date\", 
echo \"PATIENTLASTMENSTRUALDATERES\": \"$lmp_res\", 
echo \"GESTATIONPERIOD\": \"$preg_dur\", 
echo \"GESTATIONPERIODUNIT\": \"$preg_unit\", 
echo \"BREASTFEEDING_EXTENSION\": \"$patient_lact\", 
echo \"ESTIMATEDDELIVERYDATE\": \"$expected_delivery_date\",  
echo \"PATERNALEXPOSURE\": \"$paternal_exposure\" 
echo "}"
} >>RT_PATIENT.json

jsonlint-php RT_PATIENT.json
if [ $? -eq 0 ]
then
cat RT_PATIENT.json>>finaljson.json
echo ",">>finaljson.json
else
echo "{">RT_PATIENT.json
{
echo \"table_name\": \"RT_PATIENT\", 
echo \"parent_tag\": \"Patient\", 
echo \"PATIENTINITIAL\": null, 
echo \"PATIENTFIRSTNAME\": null, 
echo \"PATIENTMIDDLENAME\": null, 
echo \"PATIENTLASTNAME\": null, 
echo \"PATIENTONSETAGE\": null, 
echo \"PATIENTONSETAGEUNIT\": null, 
echo \"PATIENTSEX\": null, 
echo \"PATIENTBIRTHDATE\": null, 
echo \"PATIENTBIRTHDATERES\": null, 
echo \"PATIENTWEIGHT\": null, 
echo \"PATIENTHEIGHT\": null, 
echo \"PATIENTAGEGROUP\": null, 
echo \"PATIENTID\": null, 
echo \"ISPSPMEMBER\": null, 
echo \"HCPCONSENT\": null, 
echo \"PREGNANT_EXTENSION\": null, 
echo \"PATIENTLASTMENSTRUALDATE\": null, 
echo \"PATIENTLASTMENSTRUALDATERES\": null, 
echo \"GESTATIONPERIOD\": null, 
echo \"GESTATIONPERIODUNIT\": null, 
echo \"BREASTFEEDING_EXTENSION\": null, 
echo \"ESTIMATEDDELIVERYDATE\": null,  
echo \"PATERNALEXPOSURE\": null 
echo "},"
} >>RT_PATIENT.json
cat RT_PATIENT.json>>finaljson.json
fi

#Death information
#RT death
sim=$(< layout grep -i "Óbito" -A1000|grep -i "Paciente foi a óbito?"|grep -i "sim" -m1|grep -E -o ".{0,10}Sim"|grep -i "✔\|X\|■")
sim=$(bash checkbox_module.sh "$sim")
no=$(< layout grep -i "Óbito" -A1000|grep -i "Paciente foi a óbito?"|grep -i "Não" -m1|awk -F 'Não' '{print $1}'|awk -F 'Sim' '{print $2}'|grep -i "✔\|X\|■")
no=$(bash checkbox_module.sh "$no")
if [ "$sim" == 1 ]
then
dead="Sim"
elif [ "$no" == 1 ]
then
dead="Não"
else
dead=null
fi
echo "Did the patient die?" $dead
if [ "$dead" == "Sim" ]
then
#death date
death_date=$(< layout grep -i "Óbito" -A1000|grep -i "Data do óbito:"|awk -F 'Causa do óbito' '{print $1}'|awk -F 'Data do óbito' '{print $2}'|sed 's/://g'|sed 's./.-.g'|sed 's/\"//g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g'|sed '/^$/d')
#changing date format
death_date=$(date_extract "$death_date")
##changing date and month -> DD-MM-YYYY to D-M-YYYY(removing '0's in day and month for 1-9)
death_date=$(date_partial "$death_date")
if [ -z "$death_date" ]
then
death_date=null
fi
echo "Date of Death:" $death_date
death_res=$(date_res "$death_date")
if [ -z "$death_res" ]
then
death_res=null
fi
echo "Death date res:" $death_res
#cause of death
cause_of_death=$(< layout grep -i "Óbito" -A1000|grep -i "Data do óbito:"|awk -F 'Causa do óbito' '{print $2}'|sed 's/\bNI\b//g'|sed 's/\bnq\b//g'|sed 's/\bNq\b//g'|sed 's/\bNQ\b//g'|sed 's/://g'|sed 's/\"//g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g'|sed '/^$/d')
if [ -z "$cause_of_death" ]
then
cause_of_death=null
fi
echo "Cause of death:" $cause_of_death
#autopsy report
sim_co=$(< layout grep -i "Óbito" -A100|grep -i "Possui relatório de autópsia?" -A100|grep -i "sim" -m1 -B100|grep -iaob "sim"|awk -F ':' '{print $1}')
sim=$(< layout grep -i "Óbito" -A100|grep -i "Possui relatório de autópsia?" -A100|grep -i "sim" -m1 -B100|awk '{val=substr($0,0,'$((sim_co-20))');print val}'|grep -i "✔\|X\|■")
sim=$(bash checkbox_module.sh "$sim")
no_co=$(< layout grep -i "Óbito" -A100|grep -i "Possui relatório de autópsia?" -A100|grep -i "Não" -m1 -B100|grep -iaob "Não"|awk -F ':' '{print $1}'|sed -n "1p" )
no=$( < layout grep -i "Óbito" -A100|grep -i "Possui relatório de autópsia?" -A100|grep -i "Não" -m1 -B100|awk '{val=substr($0,'$((no_co))-10', 20);print val}'|grep -i "✔\|X\|■")
no=$(bash checkbox_module.sh "$no")
desconhecido=$(< layout grep -i "Óbito" -A100|grep -i "Possui relatório de autópsia?"|grep -i "Desconhecido" -m1|grep -E -o ".{0,10}Desconhecido"|grep -i "✔\|X\|■")
desconhecido=$(bash checkbox_module.sh "$desconhecido")
questionado=$(< layout grep -i "Óbito" -A100|grep -i "Possui relatório de autópsia?"|grep -i "Não Questionado" -m1|grep -E -o ".{0,10}Não Questionado"|grep -i "✔\|X\|■")
questionado=$(bash checkbox_module.sh "$questionado")

#desconhecido_co=$(< layout grep -i "Óbito" -A100|grep -i "Possui relatório de autópsia?" -A100|grep -i "Desconhecido" -m1 -B100|grep -iaob "Desconhecido"|awk -F ':' '{print $1}')
#desconhecido=$(< layout grep -i "Óbito" -A100|grep -i "Possui relatório de autópsia?" -A100|grep -i "Desconhecido" -m1 -B100|awk '{val=substr($0,'$((desconhecido_co))-10', 20);print val}'|grep -i "✔\|X\|■")
#desconhecido=$(bash checkbox_module.sh "$desconhecido")
#questionado_co=$(< layout grep -i "Óbito" -A100|grep -i "Possui relatório de autópsia?" -A100|grep -i "Não Questionado" -m1 -B100|grep -iaob "Não Questionado"|awk -F ':' '{print $1}')
#questionado=$(< layout grep -i "Óbito" -A100|grep -i "Possui relatório de autópsia?" -A100|grep -i "Não Questionado" -m1 -B100|awk '{val=substr($0,'$((questionado_co))-10', 20);print val}'|grep -i "✔\|X\|■")
#questionado=$(bash checkbox_module.sh "$questionado")
if [ "$sim" == 1 ]
then
autopsy="Yes"
elif [ "$no" == 1 ]
then
autopsy="No"
elif [ "$desconhecido" == 1 ]
then
autopsy=""
elif [ "$questionado" == 1 ]
then
autopsy=""
else
autopsy=null
fi
echo "Has autopsy report?:" $autopsy

echo "{">RT_DEATH.json
{
echo \"table_name\": \"RT_DEATH\",
echo \"parent_tag\": \"Death\", 
echo \"PATIENTDEATHDATE\": \"$death_date\", 
echo \"PATIENTDEATHDATERES\": \"$death_res\", 
echo \"PATIENTAUTOPSYYESNO\": \"$autopsy\", 
echo \"PATIENTDEATHREPORT\": null 
echo "}" 
} >>RT_DEATH.json
echo "{">RT_DEATH_detail.json
{
echo \"table_name\": \"RT_DEATH_DTL\",
echo \"parent_tag\": \"Death detail\", 
echo \"seq_num\": null, 
echo \"PATIENTDEATHCAUSE\": \"$cause_of_death\" 
echo "}" 
} >>RT_DEATH_detail.json
else
echo "{">RT_DEATH.json
{
echo \"table_name\": \"RT_DEATH\", 
echo \"parent_tag\": \"Death\", 
echo \"PATIENTDEATHDATE\": null, 
echo \"PATIENTDEATHDATERES\": null, 
echo \"PATIENTAUTOPSYYESNO\": null, 
echo \"PATIENTDEATHREPORT\": null 
echo "}" 
} >>RT_DEATH.json
echo "{">RT_DEATH_detail.json
{
echo \"table_name\": \"RT_DEATH_DTL\",
echo \"parent_tag\": \"Death detail\", 
echo \"seq_num\": null, 
echo \"PATIENTDEATHCAUSE\": null 
echo "}"
} >>RT_DEATH_detail.json
fi
jsonlint-php RT_DEATH.json
if [ $? -eq 0 ]
then
cat RT_DEATH.json>>finaljson.json
echo ",">>finaljson.json
else
echo "{">RT_DEATH.json
{
echo \"table_name\": \"RT_DEATH\",
echo \"parent_tag\": \"Death\", 
echo \"PATIENTDEATHCAUSE\": null, 
echo \"PATIENTDEATHDATE\": null, 
echo \"PATIENTDEATHDATERES\": null, 
echo \"PATIENTDEATHCAUSE\": null, 
echo \"PATIENTAUTOPSYYESNO\": null 
echo "}," 
} >>RT_DEATH.json
cat RT_DEATH.json>>finaljson.json
fi

jsonlint-php RT_DEATH_detail.json
if [ $? -eq 0 ]
then
cat RT_DEATH_detail.json>>finaljson.json
echo ",">>finaljson.json
else
echo "{">RT_DEATH_detail.json
{
echo \"table_name\": \"RT_DEATH_DTL\",
echo \"parent_tag\": \"Death detail\", 
echo \"seq_num\": null, 
echo \"PATIENTDEATHCAUSE\": null 
echo "},"
} >>RT_DEATH_detail.json
cat RT_DEATH_detail.json>>finaljson.json
fi
#meningococcal vaccination
#applicable check box
checkbox_co=$(< layout grep -i "Vacinação Meningocócica" -A1000|grep -i "Não aplicável" -B100 -m1|grep -aiob "Não aplicável"|awk -F ':' '{print $1}')
applicable_check=$(< layout grep -i "Vacinação Meningocócica" -A1000|grep -i "Não aplicável" -B10 -m1|awk '{val=substr($0,'$((checkbox_co-130))',10000);print val}'|grep -i "✔\|X\|■")
applicable_check=$(bash checkbox_module.sh "$applicable_check")
echo "Applicable check: $applicable_check"
if [ "$applicable_check" == 0 ]
then
#vaccine name
vacc_name=$(< layout grep -i "Vacinação Meningocócica" -A1000|grep -i "Nome da Vacina:"|awk -F 'Dose' '{print $1}'|awk -F 'Nome da Vacina' '{print $2}'|sed 's/NÃO QUESTIONADO//g'|sed 's/não questionado//g'|sed 's/Não realizou//g'|sed 's/\bNQ\b//g'|sed 's/\bnq\b//g'|sed 's/\bNq\b//g'|sed 's/\bNQ\b//g'|sed 's/\bNÃO\b//g'|sed 's/Não questionado//g'|sed 's/\bnão\b//g'|sed 's/\bNão\b//g'|sed 's/\bNI\b//g'|sed 's/Não informado//gI'|sed 's/://g'|sed 's/\"//g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g'|sed '/^$/d')
if [ -z "$vacc_name" ]
then
vacc_name=null
fi
echo "Vaccination Name:" $vacc_name
#serotype information
serotype=$(< layout grep -i "Vacinação Meningocócica" -A1000|grep -i "Sorotipos:"|awk -F 'Sorotipos' '{print $2}'|sed 's/NÃO QUESTIONADO//g'|sed 's/\bnq\b//g'|sed 's/\bNq\b//g'|sed 's/\bNQ\b//g'|sed 's/não questionado//g'|sed 's/\bNQ\b//g'|sed 's/\bNÃO\b//g'|sed 's/Não questionado//g'|sed 's/\bnão\b//g'|sed 's/\bNão\b//g'|sed 's/\bNI\b//g'|sed 's/://g'|sed 's/\"//g'|sed 's/\"//g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g'|sed '/^$/d')
if [ -z "$serotype" ]
then
serotype=null
fi
echo "Serotype:" $serotype
#date of vaccination
vacc_date=$(< layout grep -i "Vacinação Meningocócica" -A1000|grep -i "Data da vacinação:"|awk -F 'Data da vacinação' '{print $2}'|sed 's/://g'|sed 's/\"//g'|sed 's./.-.g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g'|sed '/^$/d')
#changing the date format
vacc_date=$(date_extract "$vacc_date")
##changing date and month -> DD-MM-YYYY to D-M-YYYY(removing '0's in day and month for 1-9)
vacc_date=$(date_partial "$vacc_date")
if [ -z "$vacc_date" ]
then
vacc_date=null
fi
echo "Vaccination date:" $vacc_date
vacc_res=$(date_res "$vacc_date")
if [ -z "$vacc_res" ]
then
vacc_res=null
fi
echo "Vaccination Date res:" $vacc_res

##new field
#vaccine dose text
vaccine_dose_text=$(< layout grep -i "Vacinação Meningocócica" -A1000|grep -i "Dose:" -m1|awk -F 'Dose' '{print $2}'|sed 's/://g'|sed 's/\"//g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g'|sed '/^$/d')
echo "vaccine dose text:" "$vaccine_dose_text"
##vaccine dose
vaccine_dose=$(< layout grep -i "Vacinação Meningocócica" -A1000|grep -i "Dose:" -m1|awk -F 'Dose' '{print $2}'|sed 's/://g'|tr -s ' ' '\n'|sed 's/[^0-9./]/ /g'|tr -s '\n' ' '|awk -F ' ' '{print $1}'|sed 's/\"//g'|sed 's/1\/2/0.5/'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g'|sed '/^$/d')
echo "Vaccine dose:" "$vaccine_dose"
##vaccine dose unit
vaccine_dose_unit=$(< layout grep -i "Vacinação Meningocócica" -A1000|grep -i "Dose:" -m1|awk -F 'Dose' '{print $2}'|sed 's/vide campo eventos\|Vide eventos//gI'|sed 's/\bcomp\b\|\bCOMP\b\|\bComp\b/Tablet/g'|sed 's/NÃO QUESTIONADO//g'|sed 's/Não soube informar//g'|sed 's/não questionado//g'|sed 's/\bNQ\b//g'|sed 's/comprido\|comprimido/tablet/g'|sed 's/\bNÃO\b//g'|sed 's/\bnq\b//g'|sed 's/\bNq\b//g'|sed 's/\bNQ\b//g'|sed 's/Não questionado//g'|sed 's/injeção/Injection/g'|sed 's/\bnão\b//g'|sed 's/\bNão\b//g'|sed 's/\bNI\b//g'|sed 's/\bNSI\b//g'|sed 's/://g'|sed 's/[0-9/\.]/ /g'|awk -F ' ' '{print $1}'|sed 's/\"//g'|sed -e 's/\bx\b\|\bX\b//g'|tr '[:upper:]' '[:lower:]'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g'|sed '/^$/d')
echo "Vaccine dose:" "$vaccine_dose_unit"

echo "{">RT_VACCINE.json
{
echo \"table_name\": \"RT_VACCINE\",
echo \"parent_tag\": \"vaccine\", 
echo \"seq_num\": null, 
echo \"PATIENTDRUGNAME\": \"$vacc_name\", 
echo \"SEROTYPE_EXTENSION\": \"$serotype\", 
echo \"PATIENTDRUGSTARTDATE\": \"$vacc_date\", 
echo \"PATIENTDRUGSTARTDATERES\":\"$vacc_res\", 
echo \"PATIENTDRUGDOSE\": \"$vaccine_dose\", 
echo \"PATIENTDRUGDOSEUNIT\": \"$vaccine_dose_unit\" 
echo "}"
} >>RT_VACCINE.json
else
echo "{">RT_VACCINE.json
{
echo \"table_name\": \"RT_VACCINE\", 
echo \"parent_tag\": \"vaccine\", 
echo \"seq_num\": null, 
echo \"PATIENTDRUGNAME\": null, 
echo \"SEROTYPE_EXTENSION\": null, 
echo \"PATIENTDRUGSTARTDATE\": null, 
echo \"PATIENTDRUGSTARTDATERES\":null, 
echo \"PATIENTDRUGDOSE\": null, 
echo \"PATIENTDRUGDOSEUNIT\": null 
echo "}"
} >>RT_VACCINE.json
fi

jsonlint-php RT_VACCINE.json
if [ $? -eq 0 ]
then
cat RT_VACCINE.json>>finaljson.json
echo ",">>finaljson.json
else
echo "{">RT_VACCINE.json
{
echo \"table_name\": \"RT_VACCINE\", 
echo \"parent_tag\": \"vaccine\", 
echo \"seq_num\": null, 
echo \"PATIENTDRUGNAME\": null, 
echo \"SEROTYPE_EXTENSION\": null, 
echo \"PATIENTDRUGSTARTDATE\": null, 
echo \"PATIENTDRUGSTARTDATERES\":null, 
echo \"PATIENTDRUGDOSE\": null, 
echo \"PATIENTDRUGDOSEUNIT\": null 
echo "},"
} >>RT_VACCINE.json
cat RT_VACCINE.json>>finaljson.json
fi

#Suspect product information
#product information coordinates
product_name_top_co=$(< pdfxml.xml grep -i "Page 2 of 4" -A1000|grep -i "Nome do produto:" -m1|awk -F 'left' '{print $1}'|awk -F 'top=' '{print $2}'|sed 's/\"//g')
indication_top_co=$(< pdfxml.xml grep -i "Page 2 of 4" -A1000|grep -i "Indicação:" -m1|awk -F 'left' '{print $1}'|awk -F 'top=' '{print $2}'|sed 's/\"//g')
route_top_co=$(< pdfxml.xml grep -i "Page 2 of 4" -A1000|grep -i "Via de administração:" -m1|awk -F 'left' '{print $1}'|awk -F 'top=' '{print $2}'|sed 's/\"//g')
# lot_top_co=$(< pdfxml.xml grep -i "Page 2 of 4" -A1000|grep -i "Lote:" -m1|awk -F 'left' '{print $1}'|awk -F 'top=' '{print $2}'|sed 's/\"//g')
last_dose_date_co=$(< pdfxml.xml grep -i "Page 2 of 4" -A1000|grep -i "Data da última dose:" -m1|awk -F 'left' '{print $1}'|awk -F 'top=' '{print $2}'|sed 's/\"//g')
face_inicial_top_co=$(< pdfxml.xml grep -i "Page 2 of 4" -A1000|grep -i "Fase Inicial" -m1|awk -F 'left' '{print $1}'|awk -F 'top=' '{print $2}'|sed 's/\"//g')
face_inicial_top_co=$((face_inicial_top_co-10))
frequency_left_co=$(< pdfxml.xml grep -i "Page 2 of 4" -A1000|grep -i "Frequência atual:"|awk -F 'width' '{print $1}'|awk -F 'left=' '{print $2}'|sed 's/\"//g')

#product name
product_name=$(product_info_extract "$indication_top_co" "$product_name_top_co" "$frequency_left_co")
product_name=$(echo "$product_name"|sed 's/NÃO QUESTIONADO//g'|sed 's/não questionado//g'|sed 's/Não realizou//g'|sed 's/\bNQ\b//g'|sed 's/\bnq\b//g'|sed 's/\bNq\b//g'|sed 's/\bNQ\b//g'|sed 's/\bNÃO\b//g'|sed 's/Não questionado//g'|sed 's/\bnão\b//g'|sed 's/\bNão\b//g'|sed 's/\bNI\b//g'|sed 's/Não informado//gI'|sed 's/://g'|sed 's/\"//g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g'|sed '/^$/d')
echo "Product Name: $product_name"
#indication
drug_indication=$(product_info_extract "$route_top_co" "$indication_top_co" "$frequency_left_co")
drug_indication=$(echo "$drug_indication"|sed 's/NÃO QUESTIONADO//g'|sed 's/não questionado//g'|sed 's/Não realizou//g'|sed 's/\bNQ\b//g'|sed 's/\bnq\b//g'|sed 's/\bNq\b//g'|sed 's/\bNQ\b//g'|sed 's/\bNÃO\b//g'|sed 's/Não questionado//g'|sed 's/\bnão\b//g'|sed 's/\bNão\b//g'|sed 's/\bNI\b//g'|sed 's/Não informado//gI'|sed 's/://g'|sed 's/\"//g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g'|sed '/^$/d')
echo "Indication: $drug_indication"
#route
route_of_administration=$(product_info_extract "$last_dose_date_co" "$route_top_co" "$frequency_left_co")
route_of_administration=$(echo "$route_of_administration"|sed 's/Endovenoso\|Endovenosa\|Intravenosa/Intravenous/g'|sed 's/NÃO QUESTIONADO//g'|sed 's/não questionado//g'|sed 's/Não realizou//g'|sed 's/\bNQ\b//g'|sed 's/\bnq\b//g'|sed 's/\bNq\b//g'|sed 's/\bNQ\b//g'|sed 's/\bNÃO\b//g'|sed 's/Não questionado//g'|sed 's/\bnão\b//g'|sed 's/\bNão\b//g'|sed 's/\bNI\b//g'|sed 's/Não informado//gI'|sed 's/://g'|sed 's/\"//g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g'|sed '/^$/d')
echo "Route of administration: $route_of_administration"
#last dose date
last_dose_date=$(product_info_extract "$face_inicial_top_co" "$last_dose_date_co" "$frequency_left_co")
last_dose_date=$(echo "$last_dose_date"|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g'|sed 's/\"//g'|sed 's./.-.g'|sed 's/\./-/g'|sed '/^$/d')
#changing the date format
#DD-MM-YYYY
last_dose_date=$(date_extract "$last_dose_date")
##changing date and month -> DD-MM-YYYY to D-M-YYYY(removing '0's in day and month for 1-9)
last_dose_date=$(date_partial "$last_dose_date")
if [[ "$last_dose_date" == "--" ]]
then 
last_dose_date=""
fi
echo "Last dose date: $last_dose_date"
last_dose_res=$(date_res "$last_dose_date")
if [ -z "$last_dose_res" ]
then
last_dose_res=null
fi
echo "Last Dose Date res:" $last_dose_res

#reporter didnt know how to inform lot and expiry date
relator_checkbox_top_co=$(< pdfxml.xml grep -i "Relator não soube informar lote e validade"|awk -F 'left' '{print $1}'|awk -F 'top=' '{print $2}'|sed 's/\"//g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g')
relator_checkbox_left_co=$(< pdfxml.xml grep -i "Relator não soube informar lote e validade"|awk -F 'width' '{print $1}'|awk -F 'left=' '{print $2}'|sed 's/\"//g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g')
causalidade_top_co=$(< pdfxml.xml grep -i "Causalidade"|awk -F 'left' '{print $1}'|awk -F 'top=' '{print $2}'|sed 's/\"//g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g')
rep_checkbox=$(lot_expiry_info_extract "$relator_checkbox_top_co" "$causalidade_top_co" "$relator_checkbox_left_co" "1000")
rep_checkbox=$(bash checkbox_module.sh "$rep_checkbox")
echo "Reporter checkbox:" "$rep_checkbox"
if [ "$rep_checkbox" == 1 ]
then
lot_number=UNK
expiration_date=""
else
top_coordinate=$(< pdfxml.xml grep -i "A Farmacovigilância pode entrar em contato com o médico?" -A100|grep -i "Lote:"|awk -F 'left' '{print $1}'|awk -F 'top=' '{print $2}'|sed 's/\"//g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g')
bottom_coordinate=$(< pdfxml.xml grep -i "Causalidade"|awk -F 'left' '{print $1}'|awk -F 'top=' '{print $2}'|sed 's/\"//g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g')
lot_left_co=$(< pdfxml.xml grep -i "A Farmacovigilância pode entrar em contato com o médico?" -A100|grep -i "Lote:"|awk -F 'width' '{print $1}'|awk -F 'left=' '{print $2}'|sed 's/\"//g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g')
expiry_left_co=$(< pdfxml.xml grep -i "A Farmacovigilância pode entrar em contato com o médico?" -A100|grep -i "Validade:"|awk -F 'width' '{print $1}'|awk -F 'left=' '{print $2}'|sed 's/\"//g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g')
expiry_right_co=$(< pdfxml.xml grep -i "A Farmacovigilância pode entrar em contato com o médico?" -A100|grep -i "Relator não soube informar lote e validade"|awk -F 'width' '{print $1}'|awk -F 'left=' '{print $2}'|sed 's/\"//g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g')
echo "expiry right coordinate: " "$expiry_right_co"
#lot batch number
lot_number=$(lot_expiry_info_extract "$top_coordinate" "$bottom_coordinate" "$lot_left_co" "expiry_left_co")
lot_number=$(echo "$lot_number"|sed 's/NÃO QUESTIONADO//g'|sed 's/não questionado//g'|sed 's/Não realizou//g'|sed 's/\bNQ\b//g'|sed 's/\bnq\b//g'|sed 's/\bNq\b//g'|sed 's/\bNQ\b//g'|sed 's/\bNÃO\b//g'|sed 's/Não questionado//g'|sed 's/\bnão\b//g'|sed 's/\bNão\b//g'|sed 's/\bNI\b//g'|sed 's/Não informado//gI'|sed 's/://g'|sed 's/\"//g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g'|sed '/^$/d')
#Expiration date
expiration_date=$(lot_expiry_info_extract "$top_coordinate" "$bottom_coordinate" "$expiry_left_co" "expiry_right_co")
expiration_date=$(echo "$expiration_date"|sed 's/NÃO QUESTIONADO//g'|sed 's/não questionado//g'|sed 's/Não realizou//g'|sed 's/\bNQ\b//g'|sed 's/\bnq\b//g'|sed 's/\bNq\b//g'|sed 's/\bNQ\b//g'|sed 's/\bNÃO\b//g'|sed 's/Não questionado//g'|sed 's/\bnão\b//g'|sed 's/\bNão\b//g'|sed 's/\bNI\b//g'|sed 's/\"//g'|sed 's./.-.g'|sed 's/\./-/g'|sed 's/Não informado//gI'|sed 's/://g'|sed 's/\"//g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g'|sed '/^$/d')
#changing the date format
expiration_date=$(date_extract "$expiration_date")
##changing date and month -> DD-MM-YYYY to D-M-YYYY (removing '0's in day and month for 1-9)
expiration_date=$(date_partial "$expiration_date")
fi
echo "Lot: $lot_number"
echo "Expiration date: $expiration_date"
#expiration date res
exp_date_res=$(date_res "$expiration_date")
echo "expiration date res: $exp_date_res"


#Action taken
#drug action taken not applicable
actiontaken_top_co=$(< pdfxml.xml grep -i "Descrever o tratamento adotado para os eventos, tais como medicamentos utilizados (prescritos ou auto-medicação)," -A10000|grep -i "</page>" -m1 -B10000|grep -i "Ação tomada com o produto Alexion em decorrência dos eventos"|awk -F 'left' '{print $1}'|awk -F 'top=' '{print $2}'|sed 's/\"//g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g')
actiontaken_bottom_co=$(< pdfxml.xml grep -i "Descrever o tratamento adotado para os eventos, tais como medicamentos utilizados (prescritos ou auto-medicação)," -A10000|grep -i "</page>" -m1 -B10000|grep -i "Informar se houve alteração com o medicamento Alexion devido aos eventos, tais como: suspensão definitiva ou"|awk -F 'left' '{print $1}'|awk -F 'top=' '{print $2}'|sed 's/\"//g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g')
actiontaken_left_co=$(< pdfxml.xml grep -i "Descrever o tratamento adotado para os eventos, tais como medicamentos utilizados (prescritos ou auto-medicação)," -A10000|grep -i "</page>" -m1 -B10000|grep -i "Ação tomada com o produto Alexion em decorrência dos eventos"|awk -F 'width' '{print $1}'|awk -F 'left=' '{print $2}'|sed 's/\"//g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g')
actiontaken_right_co=$(get_coordinate "$actiontaken_top_co" "$actiontaken_bottom_co" "Não aplicável")
actiontaken_applicable_check=$(lot_expiry_info_extract "$actiontaken_top_co" "$actiontaken_bottom_co" "$actiontaken_left_co" "$actiontaken_right_co")
actiontaken_applicable_check=$(bash checkbox_module.sh "$actiontaken_applicable_check")
echo "Action taken section not applicable:" "$actiontaken_applicable_check"
if [ "$actiontaken_applicable_check" == 0 ]
then
echo "######## Action Taken #########"
after_data=$(< htmlcomb.comb grep -i "Ação tomada com o produto Alexion em decorrência dos eventos" -A100)
echo "after_data Action taken:" "$after_data"
< htmlcomb.comb grep -i "Ação tomada com o produto Alexion em decorrência dos eventos" -A100|grep -i "Page" -m1 -B100|grep -v "Page"|grep -i "quência, etc." -m1 -A100|grep -v "quência, etc.">action_text
lines=$(< action_text wc -l)
for((i=1;i<=$lines;i++))
do 
value=$(< action_text head -1)
echo "Action Taken Value:" "$value"
if [[ "$value" =~ [A-Za-z] ]]
then
action_data="$value"
fi
sed -i "1d" action_text
done
echo "Action Taken before splittext:" "$action_data"
#action_data=$(python3 -c "from splittextarea import split_combdata; print (split_combdata('$action_data'))")
action_data=`echo "$action_data"|awk -F'[|][|]' '{$1="";$2="";$3="";$4="";print}'`
echo "Action Taken after splittext:" "$action_data"
action_data=$(echo "$action_data"|sed 's/\.//g'|sed 's/\"//g'|sed 's/\bNQ\b//g'|sed 's/\bnq\b//g'|sed 's/\bNq\b//g'|sed 's/\bNSI\b//g'|sed 's/\bnsi\b//g'|sed 's/\bNA\b//g'|sed 's/\bna\b//g'|sed 's/&#34//g'|sed 's/\"//g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g')
check=$(echo "$action_data"|tr '[:upper:]' '[:lower:]')
echo "Action Taken check:" "$check"
if [[ "$check" == "não" || "$check" == "nÃo" || "$check" == "nenhuma" || "$check" == "nenhuma ação tomada" || "$check" == "não houve alteração" ]]
then
action_data="Unchanged"
elif [[ "$check" =~ .*"mudança".* || "$check" =~ .*"alteração".* || "$check" =~ .*"troco".* || "$check" =~ .*"câmbio".* || "$check" =~ .*"conversão".* || "$check" =~ .*"modulação".* || "$check" =~ .*"modificação".* || "$check" =~ .*"variedade".* || "$check" =~ .*"variação".* || "$check" =~ .*"variante".* || "$check" =~ .*"diferença".* || "$check" =~ .*"oscilação".* || "$check" =~ .*"inflexão".* ]]
then
action_data="Dose or regimen changed"
elif [[ "$check" =~ .*"suspensão".* || "$check" =~ .*"interrupção".* || "$check" =~ .*"pausa".* || "$check" =~ .*"intervalo".* || "$check" =~ .*"parada".* || "$check" =~ .*"paragem".* || "$check" =~ .*"batente".* || "$check" =~ .*"ponto".* || "$check" =~ .*"fim".* || "$check" =~ .*"expectativa".* || "$check" =~ .*"incerteza".* || "$check" =~ .*"ansiedade".* || "$check" =~ .*"dúvida".* || "$check" =~ .*"indecisão".* || "$check" =~ .*"intermissão".* ]]
then
action_data="Withdrawn"
fi
echo "Action Taken before empty check:" "$action_data"
if [ -z "$action_data" ]
then
action_data=null
fi
else
echo "Action taken not applicable"
action_data=null
fi
echo "Action Taken:" "$action_data"

#Initial phase
#dose information
dose1=$(< layout grep -i "Fase Inicial" -A100 -m1|grep -i "Dose:" -m1|awk -F 'Data de início' '{print $1}'|awk -F 'Dose' '{print $2}'|sed 's/://g'|tr -s ' ' '\n'|sed 's/[^0-9./]/ /g'|tr -s '\n' ' '|awk -F ' ' '{print $1}'|sed 's/\"//g'|sed 's/1\/2/0.5/'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g'|sed '/^$/d')
if [ -z "$dose1" ]
then
dose1=null
fi
echo "Dose:" $dose1
dose_unit1=$(< layout grep -i "Fase Inicial" -A100 -m1|grep -i "Dose:" -m1|awk -F 'Data de início' '{print $1}'|awk -F 'Dose' '{print $2}'|sed 's/\bcomp\b\|\bCOMP\b\|\bComp\b/Tablet/g'|sed 's/injeção/Injection/g'|sed 's/NÃO QUESTIONADO//g'|sed 's/não questionado//g'|sed 's/\bNQ\b//g'|sed 's/comprido\|comprimido/tablet/g'|sed 's/injeção/Injection/g'|sed 's/\bNÃO\b//g'|sed 's/\bnq\b//g'|sed 's/\bNq\b//g'|sed 's/\bNQ\b//g'|sed 's/Não questionado//g'|sed 's/\bnão\b//g'|sed 's/\bNão\b//g'|sed 's/\bNI\b//g'|sed 's/\bNSI\b//g'|sed 's/vide campo eventos\|Vide eventos//gI'|sed 's/://g'|sed 's/[0-9/\.\,]/ /g'|awk -F ' ' '{print $1}'|sed 's/\"//g'|sed -e 's/\bx\b\|\bX\b//g'|tr '[:upper:]' '[:lower:]'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g'|sed '/^$/d')
if [ -z "$dose_unit1" ]
then
dose_unit1=null
fi
echo "DOSE1 unit:" $dose_unit1

#start date
start_date1=$(< layout grep -i "Fase Inicial" -A100 -m1|grep -i "Dose:" -m1|awk -F 'Data de início' '{print $2}'|sed 's/://g'|sed 's/\"//g'|sed 's./.-.g'|sed 's/\./-/g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g'|sed '/^$/d')
#changing the date format
start_date1=$(date_extract "$start_date1")
##changing date and month -> DD-MM-YYYY to D-M-YYYY (removing '0's in day and month for 1-9)
start_date1=$(date_partial "$start_date1")
if [ -z "$start_date1" ]
then
start_date1=""
fi
echo "Start Date:" "$start_date1"
start_date_res1=$(date_res "$start_date1")
if [ -z "$start_date_res1" ]
then
start_date_res1=null
fi
echo "Start Date res:" $start_date_res1
freq1=$(< layout grep -i "Fase Inicial" -A100 -m1|grep -i "Frequência:" -m1|awk -F 'Data de término' '{print $1}'|awk -F 'Frequência' '{print $2}'|sed 's/NÃO QUESTIONADO//g'|sed 's/não questionado//g'|sed 's/\bNQ\b//g'|sed 's/\bNÃO\b//g'|sed 's/\bnq\b//g'|sed 's/\bNq\b//g'|sed 's/\bNQ\b//g'|sed 's/Não questionado//g'|sed 's/\bnão\b//g'|sed 's/\bNão\b//g'|sed 's/\bNI\b//g'|sed 's/\bNSI\b//g'|sed 's/://g'|sed 's/\"//g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g'|sed '/^$/d')
frequency1=$(< frequency_config grep -i -E -o "^$freq1=")
if [ -z "$frequency1" ]
then
frequency1=$freq1
else
frequency1=$(< frequency_config grep -i "$freq1"|awk -F '=' '{print $2}'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g')
fi
echo "Frequency:" "$frequency1"
dosetext1=$(< layout grep -i "Fase Inicial" -A100 -m1|grep -i "Dose:" -m1|awk -F 'Data de início' '{print $1}'|awk -F 'Dose' '{print $2}'|sed 's/\bcomp\b\|\bCOMP\b\|\bComp\b/Tablet/g'|sed 's/injeção/Injection/g'|sed 's/NÃO QUESTIONADO//g'|sed 's/não questionado//g'|sed 's/\bNQ\b//g'|sed 's/comprido\|comprimido/tablet/g'|sed 's/\bnq\b//g'|sed 's/\bNq\b//g'|sed 's/\bNQ\b//g'|sed 's/\bNÃO\b//g'|sed 's/Não questionado//g'|sed 's/\bnão\b//g'|sed 's/\bNão\b//g'|sed 's/\bNI\b//g'|sed 's/\bNSI\b//g'|sed 's/://g'|sed 's/\"//g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g'|sed '/^$/d')
dosetext1=$(echo "$dosetext1 $frequency1")
if [ -z "$dosetext1" ]
then
dosetext1=""
fi
echo "Dose text:" "$dosetext1"

#drug stop date
end_date1=$(< layout grep -i "Fase Inicial" -A100 -m1|grep -i "Frequência:" -m1|awk -F 'Data de término' '{print $2}'|sed 's/://g'|sed 's/\"//g'|sed 's./.-.g'|sed 's/\./-/g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g'|sed '/^$/d')
if [[ $(echo "$end_date1"|grep -i -w "continua") || $(echo "$end_date1"|grep -w -i "em uso") || $(echo "$end_date1"|grep -w -i "conitnua") ]]
then
ongoing1=Yes
else
ongoing1=""
fi 
echo "Ongoing 1" "$ongoing1"
#changing the date format
end_date1=$(date_extract "$end_date1")
##changing date and month -> DD-MM-YYYY to D-M-YYYY (removing '0's in day and month for 1-9)
end_date1=$(date_partial "$end_date1")
if [ -z "$end_date1" ]
then
end_date1=""
fi
echo "End date:" "$end_date1"
end_date_res1=$(date_res "$end_date1")
if [ -z "$end_date_res1" ]
then
end_date_res1=null
fi
echo "End Date res:" $end_date_res1
echo "[">RT_PRODUCT.json
echo "[">RT_DOSE.json
echo "[">RT_Indication.json
sequence_num=0
if [ ! -z "$product_name" ]
then
if [[ -z "$start_date1" && -z "$end_date1" && -z "$dosetext1" && -z "$route_of_administration" && -z "$ongoing1" ]]
then
sequence_num=$((sequence_num+1))
{
echo "{"
echo \"table_name\": \"RT_PRODUCT\", 
echo \"parent_tag\": \"Product Information\", 
echo \"seq_num\": \"$sequence_num\", 
echo \"MEDICINALPRODUCT\": \"$product_name\", 
echo \"DRUGBATCHNUMB\": \"$lot_number\", 
echo \"EXPIRATIONDATE_EXTENSION\": \"$expiration_date\", 
echo \"EXPIRATIONDATE_EXTENSIONRES\": \"$exp_date_res\", 
echo \"DRUGACTIONTAKEN_EXTENSION\": \"$action_data\", 
echo \"LASTDOSEAE\":\"$last_dose_date\", 
echo \"LASTDOSEAERES\":\"$last_dose_res\", 
echo \"DRUGCHARACTERIZATION\": \"Suspect\" 
echo "},"
} >>RT_PRODUCT.json
#product indication
if [ ! -z "$drug_indication" ]
then
{
echo "{"
echo \"table_name\": \"RT_PRODUCT_INDICATION\", 
echo \"parent_tag\": \"Product Indication\", 
echo \"prod_seq_num\": \"$sequence_num\", 
echo \"DRUGINDICATION\": \"$drug_indication\" 
echo "},"
} >>RT_Indication.json
fi
else
sequence_num=$((sequence_num+1))
{
echo "{"
echo \"table_name\": \"RT_PRODUCT\", 
echo \"parent_tag\": \"Product Information\", 
echo \"seq_num\": \"$sequence_num\", 
echo \"MEDICINALPRODUCT\": \"$product_name\", 
echo \"DRUGBATCHNUMB\": \"$lot_number\", 
echo \"EXPIRATIONDATE_EXTENSION\": \"$expiration_date\", 
echo \"EXPIRATIONDATE_EXTENSIONRES\": \"$exp_date_res\", 
echo \"DRUGACTIONTAKEN_EXTENSION\": \"$action_data\", 
echo \"LASTDOSEAE\":\"$last_dose_date\", 
echo \"LASTDOSEAERES\":\"$last_dose_res\", 
echo \"DRUGCHARACTERIZATION\": \"Suspect\" 
echo "},"
} >>RT_PRODUCT.json
#product indication
if [ ! -z "$drug_indication" ]
then
{
echo "{"
echo \"table_name\": \"RT_PRODUCT_INDICATION\", 
echo \"parent_tag\": \"Product Indication\", 
echo \"prod_seq_num\": \"$sequence_num\", 
echo \"DRUGINDICATION\": \"$drug_indication\" 
echo "},"
} >>RT_Indication.json
fi
#dose information(json)
{
echo "{"
echo \"table_name\": \"RT_Dose\", 
echo \"parent_tag\": \"Dose Information\", 
echo \"prod_seq_num\": \"$sequence_num\", 
echo \"DOSEONGOING_EXTENSION\": \"$ongoing1\", 
echo \"DRUGSTARTDATE\": \"$start_date1\", 
echo \"DRUGSTARTDATERES\": \"$start_date_res1\", 
echo \"DRUGSTRUCTUREDOSAGENUMB\": \"$dose1\", 
echo \"DRUGSTRUCTUREDOSAGEUNIT\": \"$dose_unit1\", 
echo \"RX_FREQUENCY\": \"$frequency1\", 
echo \"DRUGDOSAGETEXT\": \"$dosetext1\", 
echo \"DRUGADMINISTRATIONROUTE\": \"$route_of_administration\", 
echo \"DRUGENDDATE\": \"$end_date1\", 
echo \"DRUGENDDATERES\": \"$end_date_res1\" 
echo "},"
} >>RT_DOSE.json
fi
fi
#maintanance phase
applicable_check=$(< layout grep -i "Fase de Manutenção"|grep -E -o ".{0,5}Não aplicável"|grep -i "✔\|X\|■")
applicable_check=$(bash checkbox_module.sh "$applicable_check")
echo "Applicable check maintanance dose: $applicable_check"
if [ "$applicable_check" == 0 ]
then
#product dose information
dose2=$(< layout grep -i "Fase de Manutenção" -A100|grep -i "Dose:" -m1|awk -F 'Data de início' '{print $1}'|awk -F 'Dose' '{print $2}'|sed 's/://g'|sed 's/\"//g'|tr -s ' ' '\n'|sed 's/[^0-9./]/ /g'|tr -s '\n' ' '|awk -F ' ' '{print $1}'|sed 's/1\/2/0.5/'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g'|sed '/^$/d')
if [ -z "$dose2" ]
then
dose2=""
fi
echo "Dose:" "$dose2"
dose_unit2=$(< layout grep -i "Fase de Manutenção" -A100|grep -i "Dose:" -m1|awk -F 'Data de início' '{print $1}'|awk -F 'Dose' '{print $2}'|sed 's/\bcomp\b|\bCOMP\b|\bComp\b/Tablet/g'|sed 's/injeção/Injection/g'|sed 's/NÃO QUESTIONADO//g'|sed 's/não questionado//g'|sed 's/comprido\|comprimido/tablet/g'|sed 's/\bNQ\b//g'|sed 's/\bnq\b//g'|sed 's/\bNq\b//g'|sed 's/\bNQ\b//g'|sed 's/\bNÃO\b//g'|sed 's/injeção/Injection/g'|sed 's/Não questionado//g'|sed 's/\bnão\b//g'|sed 's/\bNão\b//g'|sed 's/\bNI\b//g'|sed 's/\bNSI\b//g'|sed 's/vide campo eventos\|Vide eventos//gI'|sed 's/://g'|sed 's/\"//g'|sed 's/[0-9/\.\,]/ /g'|sed 's/\.//g'|sed -e 's/\bx\b\|\bX\b//g'|awk -F ' ' '{print $1}'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g'|sed '/^$/d')
if [ -z "$dose_unit2" ]
then
dose_unit2=""
fi
echo "DOSE unit 2:" "$dose_unit2"
dosetext2=$(< layout grep -i "Fase de Manutenção" -A100|grep -i "Dose:" -m1|awk -F 'Data de início' '{print $1}'|awk -F 'Dose' '{print $2}'|sed 's/\bcomp\b\|\bCOMP\b\|\bComp\b/Tablet/g'|sed 's/injeção/Injection/g'|sed 's/NÃO QUESTIONADO//g'|sed 's/não questionado//g'|sed 's/\bNQ\b//g'|sed 's/comprido\|comprimido/tablet/g'|sed 's/\bNÃO\b//g'|sed 's/\bnq\b//g'|sed 's/\bNq\b//g'|sed 's/\bNQ\b//g'|sed 's/Não questionado//g'|sed 's/\bnão\b//g'|sed 's/\bNão\b//g'|sed 's/\bNI\b//g'|sed 's/\bNSI\b//g'|tr '[:upper:]' '[:lower:]'|sed 's/://g'|sed 's/\"//g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g'|sed '/^$/d')
if [ -z "$dosetext2" ]
then
dosetext2=""
fi
#start date
start_date2=$(< layout grep -i "Fase de Manutenção" -A100|grep -i "Dose:" -m1|awk -F 'Data de início' '{print $2}'|sed 's/://g'|sed 's/\"//g'|sed 's./.-.g'|sed 's/\./-/g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g'|sed '/^$/d')
#changing the date format
start_date2=$(date_extract "$start_date2")
##changing date and month -> DD-MM-YYYY to D-M-YYYY (removing '0's in day and month for 1-9)
start_date2=$(date_partial "$start_date2")
if [ -z "$start_date2" ]
then
start_date2=""
fi
echo "Start Date:" "$start_date2"
start_date_res2=$(date_res "$start_date2")
if [ -z "$start_date_res2" ]
then
start_date_res2=null
fi
echo "Start Date res:" $start_date_res2
freq2=$(< layout grep -i "Fase de Manutenção" -A100|grep -i "Frequência:" -m1|awk -F 'Data de término' '{print $1}'|awk -F 'Frequência' '{print $2}'|sed 's/NÃO QUESTIONADO//g'|sed 's/não questionado//g'|sed 's/\bNQ\b//g'|sed 's/\bNÃO\b//g'|sed 's/\bnq\b//g'|sed 's/\bNq\b//g'|sed 's/\bNQ\b//g'|sed 's/Não questionado//g'|sed 's/\bnão\b//g'|sed 's/\bNão\b//g'|sed 's/\bNI\b//g'|sed 's/\bNSI\b//g'|sed 's/://g'|sed 's/\"//g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g'|sed '/^$/d')
frequency2=$(< frequency_config grep -i -E -o "^$freq2=")
if [ -z "$frequency2" ]
then
frequency2=$freq2
else
frequency2=$(< frequency_config grep -i "$freq2"|awk -F '=' '{print $2}'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g')
fi
echo "Frequency:" "$frequency2"
dosetext2=$(echo "$dosetext2 $frequency2")
if [ -z "$dosetext2" ]
then
dosetext2=""
fi
echo "dose text 2: $dosetext2"
#end date
end_date2=$(< layout grep -i "Fase de Manutenção" -A100|grep -i "Frequência:" -m1|awk -F 'Data de término' '{print $2}'|sed 's/://g'|sed 's/\"//g'|sed 's./.-.g'|sed 's/\./-/g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g'|sed '/^$/d')
if [[ $(echo "$end_date2"|grep -i -w "continua") || $(echo "$end_date2"|grep -w -i "em uso") || $(echo "$end_date2"|grep -w -i "conitnua") ]]
then
ongoing2=Yes
else
ongoing2=""
fi 
echo "Ongoing 2 $ongoing2"
#changing date format
end_date2=$(date_extract "$end_date2")
##changing date and month -> DD-MM-YYYY to D-M-YYYY (removing '0's in day and month for 1-9)
end_date2=$(date_partial "$end_date2")
if [ -z "$end_date2" ]
then
end_date2=""
fi
echo "End date: $end_date2"
end_date_res2=$(date_res "$end_date2")
if [ -z "$end_date_res2" ]
then
end_date_res2=null
fi
echo "End Date res: $end_date_res2"

if [ ! -z "$product_name" ]
then
if [[ -z "$start_date2" && -z "$end_date2" && -z "$dosetext2" && -z "$route_of_administration" && -z "$ongoing2" ]]
then
echo "No maintanance dose information"
else
{
echo "{" 
echo \"table_name\": \"RT_Dose\", 
echo \"parent_tag\": \"Dose Information\", 
echo \"prod_seq_num\": \"$sequence_num\", 
echo \"DOSEONGOING_EXTENSION\": \"$ongoing2\", 
echo \"DRUGSTARTDATE\": \"$start_date2\", 
echo \"DRUGSTARTDATERES\": \"$start_date_res2\", 
echo \"DRUGSTRUCTUREDOSAGENUMB\": \"$dose2\", 
echo \"DRUGSTRUCTUREDOSAGEUNIT\": \"$dose_unit2\", 
echo \"RX_FREQUENCY\": \"$frequency2\", 
echo \"DRUGDOSAGETEXT\": \"$dosetext2\", 
echo \"DRUGADMINISTRATIONROUTE\": \"$route_of_administration\", 
echo \"DRUGENDDATE\": \"$end_date2\", 
echo \"DRUGENDDATERES\": \"$end_date_res2\" 
echo "},"
} >>RT_DOSE.json
fi
fi
fi
#Antibiotics
applicable_check=$(< layout grep -i "Antibioticoprofilaxia"|grep -E -o ".{0,5}Não aplicável"|grep -i "✔\|X\|■")
applicable_check=$(bash checkbox_module.sh "$applicable_check")
echo "Antibotics Applicable check:" "$applicable_check"

if [ "$applicable_check" == 0 ]
then
#antibiotics name
anti_name=$(< layout grep -i "Antibioticoprofilaxia" -A1000|grep -i "Nome do Antibiótico:"|awk -F 'Nome do Antibiótico' '{print $2}'|sed 's/NÃO QUESTIONADO//g'|sed 's/não questionado//g'|sed 's/\bNQ\b//g'|sed 's/\bNÃO\b//g'|sed 's/\bnq\b//g'|sed 's/\bNq\b//g'|sed 's/\bNQ\b//g'|sed 's/Não questionado//g'|sed 's/\bnão\b//g'|sed 's/\bNão\b//g'|sed 's/\bNI\b//g'|sed 's/\bNSI\b//g'|sed 's/://g'|sed 's/\"//g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g'|sed '/^$/d')
if [ -z "$anti_name" ]
then
anti_name=""
fi
echo "Antibiotics Name: $anti_name"
#dose information
freq=$(< layout grep -i "Antibioticoprofilaxia" -A1000|grep -i "Dose/Frequência:"|awk -F 'Dose/Frequência' '{print $2}'|sed 's/\bcomp\b\|\bCOMP\b\|\bComp\b/Tablet/g'|sed 's/injeção/Injection/g'|sed 's/NÃO QUESTIONADO//g'|sed 's/não questionado//g'|sed 's/\bNQ\b//g'|sed 's/\bNÃO\b//g'|sed 's/\bnq\b//g'|sed 's/comprido\|comprimido/tablet/g'|sed 's/\bNq\b//g'|sed 's/\bNQ\b//g'|sed 's/Não questionado//g'|sed 's/\bnão\b//g'|sed 's/\bNão\b//g'|sed 's/\bNI\b//g'|sed 's/\bNSI\b//g'|sed 's/://g'|sed 's/\"//g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g'|sed '/^$/d')
anti_dose=$(echo "$freq"|tr -s ' ' '\n'|sed 's/[^0-9\.]/ /g'|tr -s '\n' ' '|awk -F ' ' '{print $1}'|sed 's/NÃO QUESTIONADO//g'|sed 's/não questionado//g'|sed 's/\bNQ\b//g'|sed 's/\bNÃO\b//g'|sed 's/Não questionado//g'|sed 's/\bnão\b//g'|sed 's/\bnq\b//g'|sed 's/\bNq\b//g'|sed 's/\bNQ\b//g'|sed 's/\bNão\b//g'|sed 's/\bNI\b//g'|sed 's/\bNSI\b//g'|sed 's/vide campo eventos//gI'|sed 's/://g'|sed 's/\"//g'|sed 's/1\/2/0.5/'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g'|sed '/^$/d')
if [ -z "$anti_dose" ]
then
anti_dose=""
fi
anti_dunit=$(echo "$freq"|sed 's/[0-9/\.\,]/ /g'|sed 's/\.//g'|awk -F ' ' '{print $1}'|sed 's/\bcomp\b|\bCOMP\b|\bComp\b/Tablet/g'|sed 's/injeção/Injection/g'|sed 's/NÃO QUESTIONADO//g'|sed 's/não questionado//g'|sed 's/\bNQ\b//g'|sed 's/\bNÃO\b//g'|sed 's/Não questionado//g'|sed 's/\bnão\b//g'|sed 's/comprido\|comprimido/tablet/g'|sed 's/\bNão\b//g'|sed 's/\bNSI\b//g'|sed 's/\bnq\b//g'|sed 's/\bNq\b//g'|sed 's/\bNQ\b//g'|sed 's/\bnq\b//g'|sed 's/\bNq\b//g'|sed 's/\bNQ\b//g'|sed 's/vide campo eventos\|Vide//gI'|sed -e 's/\bx\b\|\bX\b//g'|tr '[:upper:]' '[:lower:]'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g'|sed '/^$/d')
if [ -z "$anti_dunit" ]
then
anti_dunit=""
fi
echo "Dose:" "$anti_dose"
echo "Dose unit:" "$anti_dunit"
echo "Dose/Frequency:" "$freq"
#start date
start_date=$(< layout grep -i "Antibioticoprofilaxia" -A1000|grep -i "Data de início"|awk -F 'Data de início' '{print $2}'|sed 's/://g'|sed 's/\./-/g'|sed 's/\"//g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g'|sed '/^$/d')
#changing the date format
start_date=$(date_extract "$start_date")
##changing date and month -> DD-MM-YYYY to D-M-YYYY (removing '0's in day and month for 1-9)
start_date=$(date_partial "$start_date")
if [ -z "$start_date" ]
then
start_date=""
fi
echo "Start Date: $start_date"
start_date_res=$(date_res "$start_date")
if [ -z "$start_date_res" ]
then
start_date_res=null
fi
echo "Start date res: $start_date_res"
#stop date
end_date=$(< layout grep -i "Antibioticoprofilaxia" -A1000|grep -i " Data de término:"|awk -F ' Data de término' '{print $2}'|sed 's/://g'|sed 's/\"//g'|sed 's/\./-/g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g'|sed '/^$/d')
if [[ $(echo "$end_date"|grep -i -w "continua") || $(echo "$end_date"|grep -w -i "em uso") ||$(echo "$end_date"|grep -w -i "conitnua") ]]
then
ongoing_anti=Yes
else
ongoing_anti=""
fi 
echo "Ongoing Antibiotics $ongoing_anti"
#changing the date format
end_date=$(date_extract "$end_date")
##changing date and month -> DD-MM-YYYY to D-M-YYYY (removing '0's in day and month for 1-9)
end_date=$(date_partial "$end_date")
if [ -z "$end_date" ]
then
end_date=""
fi
echo "End Date: $end_date"
end_date_res=$(date_res "$end_date")
if [ -z "$end_date_res" ]
then
end_date_res=null
fi
echo "end date res:" $end_date_res
if [ ! -z "$anti_name" ]
then
if [[ -z "$start_date" && -z "$freq" && -z "$end_date" && -z "$ongoing_anti" ]]
then
sequence_num=$((sequence_num+1))
{
echo "{"
echo \"table_name\": \"RT_PRODUCT\", 
echo \"parent_tag\": \"Product Information\", 
echo \"seq_num\": \"$sequence_num\", 
echo \"MEDICINALPRODUCT\": \"$anti_name\", 
echo \"DRUGBATCHNUMB\": null, 
echo \"DRUGINDICATION\": null, 
echo \"EXPIRATIONDATE_EXTENSION\": null, 
echo \"EXPIRATIONDATE_EXTENSIONRES\": null, 
echo \"DRUGACTIONTAKEN_EXTENSION\": null, 
echo \"LASTDOSEAE\": null, 
echo \"LASTDOSEAERES\": null, 
echo \"DRUGCHARACTERIZATION\": \"Concomitant\" 
echo "},"
} >>RT_PRODUCT.json
else
sequence_num=$((sequence_num+1))
{
echo "{" 
echo \"table_name\": \"RT_PRODUCT\", 
echo \"parent_tag\": \"Product Information\", 
echo \"seq_num\": \"$sequence_num\", 
echo \"MEDICINALPRODUCT\": \"$anti_name\", 
echo \"DRUGBATCHNUMB\": null, 
echo \"DRUGINDICATION\": null, 
echo \"EXPIRATIONDATE_EXTENSION\": null, 
echo \"EXPIRATIONDATE_EXTENSIONRES\": null, 
echo \"DRUGACTIONTAKEN_EXTENSION\": null, 
echo \"LASTDOSEAE\": null, 
echo \"LASTDOSEAERES\": null, 
echo \"DRUGCHARACTERIZATION\": \"Concomitant\" 
echo "},"
} >>RT_PRODUCT.json
{
echo "{"
echo \"table_name\": \"RT_Dose\", 
echo \"parent_tag\": \"Dose Information\", 
echo \"prod_seq_num\": \"$sequence_num\", 
echo \"DOSEONGOING_EXTENSION\": \"$ongoing_anti\", 
echo \"DRUGSTARTDATE\": \"$start_date\", 
echo \"DRUGSTARTDATERES\": \"$start_date_res\", 
echo \"DRUGSTRUCTUREDOSAGENUMB\": \"$anti_dose\", 
echo \"DRUGSTRUCTUREDOSAGEUNIT\": \"$anti_dunit\", 
echo \"DRUGDOSAGETEXT\": \"$freq\", 
echo \"DRUGADMINISTRATIONROUTE\": null, 
echo \"DRUGENDDATE\": \"$end_date\", 
echo \"DRUGENDDATERES\": \"$end_date_res\" 
echo "},"
} >>RT_DOSE.json
fi
else
echo "No antibiotics"
fi
echo "Not applicable checked (Antibiotics)"
fi
bash table_extraction.sh "$1" "$sequence_num"
sed -i '$d' RT_PRODUCT.json
echo "}">>RT_PRODUCT.json
sed -i '$d' RT_Indication.json
echo "}">>RT_Indication.json
sed -i '$d' RT_DOSE.json
echo "}">>RT_DOSE.json
echo "]">>RT_PRODUCT.json
echo "]">>RT_Indication.json
echo "]">>RT_DOSE.json

jsonlint-php RT_PRODUCT.json
if [ $? -eq 0 ]
then
cat RT_PRODUCT.json>>finaljson.json
echo ",">>finaljson.json
else
echo "[">RT_PRODUCT.json
{
echo "{"
echo \"table_name\": \"RT_PRODUCT\", 
echo \"parent_tag\": \"Product Information\", 
echo \"seq_num\": "1", 
echo \"MEDICINALPRODUCT\": null, 
echo \"DRUGBATCHNUMB\": null, 
echo \"DRUGINDICATION\": null, 
echo \"EXPIRATIONDATE_EXTENSION\": null, 
echo \"EXPIRATIONDATE_EXTENSIONRES\": null, 
echo \"DRUGACTIONTAKEN_EXTENSION\": null, 
echo \"LASTDOSEAE\": null, 
echo \"LASTDOSEAERES\": null, 
echo \"DRUGCHARACTERIZATION\": \"Suspect\" 
echo "}," 
echo "{" 
echo \"table_name\": \"RT_PRODUCT\", 
echo \"parent_tag\": \"Product Information\", 
echo \"seq_num\": "2", 
echo \"MEDICINALPRODUCT\": null, 
echo \"DRUGBATCHNUMB\": null, 
echo \"DRUGINDICATION\": null, 
echo \"EXPIRATIONDATE_EXTENSION\": null, 
echo \"EXPIRATIONDATE_EXTENSIONRES\": null, 
echo \"DRUGACTIONTAKEN_EXTENSION\": null, 
echo \"LASTDOSEAE\": null, 
echo \"LASTDOSEAERES\": null, 
echo \"DRUGCHARACTERIZATION\": \"Concomitant\" 
echo "}" 
echo "],"
} >>RT_PRODUCT.json
cat RT_PRODUCT.json>>finaljson.json
fi

jsonlint-php RT_Indication.json
if [ $? -eq 0 ]
then
cat RT_Indication.json>>finaljson.json
echo ",">>finaljson.json
else
echo "[">RT_Indication.json
{
echo "{"
echo \"table_name\": \"RT_PRODUCT_INDICATION\", 
echo \"parent_tag\": \"Product Indication\", 
echo \"prod_seq_num\": null, 
echo \"DRUGINDICATION\": null 
echo "}" 
echo "],"
} >>RT_Indication.json
cat RT_Indication.json>>finaljson.json
fi

jsonlint-php RT_DOSE.json
if [ $? -eq 0 ]
then
cat RT_DOSE.json>>finaljson.json
echo ",">>finaljson.json
else
echo "[">RT_DOSE.json
{
echo "{"
echo \"table_name\": \"RT_Dose\", 
echo \"parent_tag\": \"Dose Information\", 
echo \"prod_seq_num\": null, 
echo \"DOSEONGOING_EXTENSION\": null, 
echo \"DRUGSTARTDATE\": null, 
echo \"DRUGSTARTDATERES\": null, 
echo \"DRUGSTRUCTUREDOSAGENUMB\": null, 
echo \"DRUGSTRUCTUREDOSAGEUNIT\": null, 
echo \"RX_FREQUENCY\": null, 
echo \"DRUGDOSAGETEXT\": null, 
echo \"DRUGADMINISTRATIONROUTE\": null, 
echo \"DRUGENDDATE\": null, 
echo \"DRUGENDDATERES\": null 
echo "}" 
echo "],"
} >>RT_DOSE.json
cat RT_DOSE.json>>finaljson.json
fi

{
echo "{"
echo \"table_name\":\"RT_PRESCRIPTION_DETAILS\", 
echo \"parent_tag\":\"PRESCRIPTION DETAILS\", 
echo \"seq_num\":null, 
echo \"RX_DM_D_NAME\":null, 
echo \"RX_STRENGTH\": null, 
echo \"RX_DOSE\": null, 
echo \"FREQUENCY\":null, 
echo \"RX_PRODUCT_NAME\":null, 
echo \"RX_QUANTITY\": null, 
echo \"RX_BATCH_NO\": null, 
echo \"RX_EXPIRY_DATE\":null 
echo "}," 
echo "{" 
echo \"table_name\": \"RT_PRESCRIPTION\", 
echo \"parent_tag\": \"PRESCRIPTION Informations\", 
echo \"RX_REFERENCE\" : null, 
echo \"RX_RECEIVED\" : null, 
echo \"RX_APPROVED\" : null, 
echo \"RX_ORDER_NUMBER\" : null, 
echo \"RX_ENTERED\" : null, 
echo \"RX_DELIVERED\" : null 
echo "},"
} >>finaljson.json
 
#general information
#rt master
#receipt date
dateofkn=$(< layout grep -i "Data de Conhecimento"|awk -F 'Data de Conhecimento' '{print $2}'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g'|sed 's/\"//g'|sed 's./.-.g'|sed 's/\./-/g'|sed '/^$/d')
#changing the date format
dateofkn=$(date_extract "$dateofkn")
dateofkn=$(bash date_formate_change_script.sh "$dateofkn")
##changing date and month -> YYYY-MM-DD to YYYY-M-D (removing '0's in day and month for 1-9)
#dateofkn=$(date_non_partial "$dateofkn")
if [[ "$dateofkn" == "--" ]]
then 
dateofkn=""
fi
if [ -z "$dateofkn" ]
then
dateofkn=null
fi
echo "Date of Knowledge:" $dateofkn
#local case id
case_number=$(< layout grep -i "Número Case Alex"|awk -F ' Número Case Alex PS' '{print $2}'|sed 's/\"//g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g'|sed '/^$/d')
if [ -z "$case_number" ]
then
case_number=null
fi
echo "Alexion case number:" $case_number

echo "{">RT_MASTER.json
{
echo \"table_name\": \"RT_MASTER\",
echo \"parent_tag\": \"patient\", 
echo \"RECEIPTDATE\": \"$dateofkn\", 
echo \"REPORTTYPE\": null, 
echo \"LOCALCASEREF_EXTENSION\": \"$case_number\", 
echo \"CASEREPORTTYPE\":\"I\", 
echo \"OCCURCOUNTRY\": \"BRAZIL\", 
echo \"STUDYNAME\": \"$product_name\" 
echo "}"
} >>RT_MASTER.json

jsonlint-php RT_MASTER.json
if [ $? -eq 0 ]
then
cat RT_MASTER.json >>finaljson.json
echo "," >>finaljson.json
else
echo "{">RT_MASTER.json
{
echo \"table_name\": \"RT_MASTER\", 
echo \"parent_tag\": \"patient\", 
echo \"RECEIPTDATE\": \"null\", 
echo \"REPORTTYPE\": \"null\", 
echo \"LOCALCASEREF_EXTENSION\": \"null\", 
echo \"CASEREPORTTYPE\":\"null\", 
echo \"OCCURCOUNTRY\": \"null\", 
echo \"STUDYNAME\": \"null\" 
echo "},"
} >>RT_MASTER.json
cat RT_MASTER.json>>finaljson.json
fi


##event data
##coordinates
causalidade_top_co=$(< pdfxml.xml grep -i "Causalidade"|awk -F 'left' '{print $1}'|awk -F 'top=' '{print $2}'|sed 's/\"//g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g')
causalidade_left_co=$(< pdfxml.xml grep -i "Causalidade"|awk -F 'width' '{print $1}'|awk -F 'left=' '{print $2}'|sed 's/\"//g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g')
drug_result_top_co=$(< pdfxml.xml grep -i "O relator considera os eventos relacionados ao uso do medicamento Alexion?"|awk -F 'left' '{print $1}'|awk -F 'top=' '{print $2}'|sed 's/\"//g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g')
reference_top_co=$(< pdfxml.xml grep -i "O médico está ciente dos eventos apresentados pelo paciente?"|awk -F 'left' '{print $1}'|awk -F 'top=' '{print $2}'|sed 's/\"//g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g')
reference_bottom_co=$(< pdfxml.xml grep -i "A Farmacovigilância pode entrar em contato com o médico?"|awk -F 'left' '{print $1}'|awk -F 'top=' '{print $2}'|sed 's/\"//g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g')
#rt event
#consider alexion drug
drugresult_applicable_check=$(lot_expiry_info_extract "$causalidade_top_co" "$drug_result_top_co" "$causalidade_left_co" "1000")
drugresult_applicable_check=$(bash checkbox_module.sh "$drugresult_applicable_check")
echo "drug result section not applicable:" "$drugresult_applicable_check"
if [ "$drugresult_applicable_check" == 0 ]
then

related_co=$(get_coordinate "$drug_result_top_co" "$reference_top_co" "Sim")
echo "drug result_top $drug_result_top_co"
echo "reference top $reference_top_co"
not_related_co=$((related_co+110))
unknown_co=$(get_coordinate "$drug_result_top_co" "$reference_top_co" "Desconhecido")
notreported_co=$(get_coordinate "$drug_result_top_co" "$reference_top_co" "Não Questionado")

related_checkbox=$(lot_expiry_info_extract "$drug_result_top_co" "$reference_top_co" "0" "$related_co")
related_checkbox=$(bash checkbox_module.sh "$related_checkbox")
not_related_checkbox=$(lot_expiry_info_extract "$drug_result_top_co" "$reference_top_co" "$related_co" "$not_related_co")
not_related_checkbox=$(bash checkbox_module.sh "$not_related_checkbox")
unknown_checkbox=$(lot_expiry_info_extract "$drug_result_top_co" "$reference_top_co" "$not_related_co" "$unknown_co")
unknown_checkbox=$(bash checkbox_module.sh "$unknown_checkbox")
not_reported_checkbox=$(lot_expiry_info_extract "$drug_result_top_co" "$reference_top_co" "$unknown_co" "$notreported_co")
not_reported_checkbox=$(bash checkbox_module.sh "$not_reported_checkbox")
if [ "$related_checkbox" == 1 ]
then
alex_drug="Related"
elif [ "$not_related_checkbox" == 1 ]
then
alex_drug="Not Related"
elif [ "$not_reported_checkbox" == 1 ]
then
alex_drug="Not Reported"
elif [ "$unknown_checkbox" == 1 ]
then
alex_drug="Unknown"
else
alex_drug=null
fi
else
echo "Drug result not applicable"
alex_drug=null
fi
echo "Does the reporter consider events related to the use of the drug Alexion?:" $alex_drug

#hopitalization
#hospitalization section not applicable
hospitalization_applicable_check=$(< layout grep -i "Hospitalização"|grep -E -o ".{0,5}Não aplicável"|grep -i "✔\|X\|■")
hospitalization_applicable_check=$(bash checkbox_module.sh "$hospitalization_applicable_check")
echo "Hospitalization section not applicable: $hospitalization_applicable_check"
if [ "$hospitalization_applicable_check" == 0 ]
then
#was patient hopitalized
sim_co=$(< layout grep -i "Hospitalização" -A100|grep -i "Paciente foi hospitalizado?" -A100|grep -i "Sim" -m1 -B100|grep -iaob "sim"|awk -F ':' '{print $1}')
sim=$(< layout grep -i "Hospitalização" -A100|grep -i "Paciente foi hospitalizado?" -A100|grep -i "Motivo da hospitalização:" -B100|grep -iv "Motivo da hospitalização:"|awk '{val=substr($0,0,'$((sim_co-20))');print val}'|grep -i "✔\|X\|■")
sim=$(bash checkbox_module.sh "$sim")
no=$(< layout grep -i "Hospitalização" -A100|grep -i "Paciente foi hospitalizado?" -A100|grep -i "Motivo da hospitalização:" -B100|grep -i "sim"|awk -F 'Não' '{print $1}'|awk -F 'Sim' '{print $2}'|grep -i "✔\|X\|■")
no=$(bash checkbox_module.sh "$no")
desconhecido=$(< layout grep -i " Hospitalização" -A100|grep -i "Paciente foi hospitalizado?"|grep -i "Desconhecido" -m1|grep -E -o ".{0,5}Desconhecido"|grep -i "✔\|X\|■")
desconhecido=$(bash checkbox_module.sh "$desconhecido")
questionado=$(< layout grep -i " Hospitalização" -A100|grep -i "Paciente foi hospitalizado?"|grep -i "Não Questionado" -m1|grep -E -o ".{0,5}Não Questionado"|grep -i "✔\|X\|■")
questionado=$(bash checkbox_module.sh "$questionado")
if [ "$sim" == 1 ]
then
hospi="Sim"
elif [ "$no" == 1 ]
then
hospi="Não"
elif [ "$desconhecido" == 1 ]
then
hospi="Desconhecido"
elif [ "$questionado" == 1 ]
then
hospi="Não Questionado"
else
hospi=null
fi
echo "Was the patient hospitalized?:" $hospi

if [[ "$hospi" == "Sim" ]]
then
hospi=Yes
#reason for hospitalization
reason_top_co=$(< pdfxml.xml grep -i "Motivo da hospitalização:" -A10000|grep -i "</page>" -B1000|grep -i "Motivo da hospitalização:"|awk -F 'left' '{print $1}'|awk -F 'top=' '{print $2}'|sed 's/\"//g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g')
reason_left_co=$(< pdfxml.xml grep -i "Motivo da hospitalização:" -A10000|grep -i "</page>" -B1000|grep -i "Motivo da hospitalização:"|awk -F 'width' '{print $1}'|awk -F 'left=' '{print $2}'|sed 's/\"//g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g')
reason_bottom_co=$((reason_top_co+30))
reason_of_hospitalization=$(get_hospitalization_reason "$reason_top_co" "$reason_bottom_co" "$reason_left_co" "1000")
reason_of_hospitalization=$(echo "$reason_of_hospitalization"|sed 's/NÃO QUESTIONADO//g'|sed 's/não questionado//g'|sed 's/\bNQ\b//g'|sed 's/\bNÃO\b//g'|sed 's/\bnq\b//g'|sed 's/\bNq\b//g'|sed 's/\bNQ\b//g'|sed 's/Não questionado//g'|sed 's/\bnão\b//g'|sed 's/\bNão\b//g'|sed 's/\bNI\b//g'|sed 's/://g'|sed 's/&#34;//g'|sed 's/\"//g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g'|sed '/^$/d')
if [ -z "$reason_of_hospitalization" ]
then
reason_of_hospitalization=null
fi
echo "Reason for hospitalization:" $reason_of_hospitalization
date_co1=$(< layout grep -i " Hospitalização" -A100|grep -i "Motivo da hospitalização:" -A100|grep -i "Data de alta:"|grep -iaob "Data de alta"|awk -F ':' '{print $1}')
date_co2=$(< layout grep -i " Hospitalização" -A100|grep -i "Motivo da hospitalização:" -A100|grep -i "Paciente não teve alta"|grep -iaob "Paciente não teve alta"|awk -F ':' '{print $1}')
#admission date
dat_of_hos=$(< layout grep -i "Hospitalização" -A1000|grep -i "Óbito" -B100|grep -i "Data de" -m1 -A100|grep -i "hospitalização"|awk '{val=substr($0,0,'$((date_co1+5))');print val}'|awk -F 'hospitalização' '{print $2}'|sed 's/://g'|sed 's/\"//g'|sed 's./.-.g'|sed 's/\./-/g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g'|sed '/^$/d')
dat_of_hos=$(date_extract "$dat_of_hos")
dat_of_hos=$(date_partial "$dat_of_hos")
if [ -z "$dat_of_hos" ]
then
dat_of_hos=null
fi
echo "Date of Hospitalization:" $dat_of_hos
datofhos_res=$(date_res "$dat_of_hos")
if [ -z "$datofhos_res" ]
then
datofhos_res=null
fi
echo "Date of hopitalization res:" $datofhos_res
#discharge date
discharge_date=$(< layout grep -i "Hospitalização" -A1000|grep -i "Óbito" -B100|grep -i "Data de" -m1 -A100|grep -i "hospitalização"|awk '{val=substr($0,'$((date_co1+10))','"$date_co2"');print val}'|sed 's/ Paciente não teve alta//g'|sed 's/X//g'|sed 's/://g'|sed 's/\"//g'|sed 's./.-.g'|sed 's/\./-/g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g'|sed '/^$/d')
discharge_date=$(date_extract "$discharge_date")
discharge_date=$(date_partial "$discharge_date")
if [ -z "$discharge_date" ]
then
discharge_date=null
fi
echo "Discharge date:" $discharge_date
discharge_res=$(date_res "$discharge_date")
if [ -z "$discharge_res" ]
then
discharge_res=null
fi
echo "discharge res:" $discharge_res
#hospital ongoing
hos_ongoing_co=$(< layout grep -i "Hospitalização" -A100|grep -i "Óbito" -B100|grep -i "paciente não teve alta"|grep -aiob "paciente não teve alta"|awk -F ':' '{print $1}')
hos_ongoing=$(< layout grep -i "Hospitalização" -A100|grep -i "Óbito" -B100|grep -i "Paciente não teve alta" -A100|awk '{val=substr($0,'"$hos_ongoing_co"',1000);print val}'|grep -i "✔\|X\|■")
hos_ongoing=$(bash checkbox_module.sh "$hos_ongoing")
if [ "$hos_ongoing" == 1 ]
then
hos_ongoing="Yes"
else
hos_ongoing="No"
fi
echo "Hospital Ongoing:" $hos_ongoing

##seriousness death
seriousness_death_cb=$(< layout grep -i "Óbito" -A1000|grep -i "Paciente foi a óbito?"|grep -i "sim" -m1|grep -E -o ".{0,10}Sim"|grep -i "✔\|X\|■")
seriousness_death_cb=$(bash checkbox_module.sh "$seriousness_death_cb")
if [ "$seriousness_death_cb" == 1 ]
then
seriousness_death="Yes"
else
seriousness_death="No"
fi
elif [[ "$hospi" == "Não" ]]
then
hospi=No
rea_hosp=null
dat_of_hos=null
datofhos_res=null
discharge_date=null
discharge_res=null
hos_ongoing=null
seriousness_death="No"
elif [[ "$hospi" == "Desconhecido" ]]
then
hospi=Unknown
rea_hosp=null
dat_of_hos=null
datofhos_res=null
discharge_date=null
discharge_res=null
hos_ongoing=null
else
echo "Hospitalization not questionable"
hospi=null
rea_hosp=null
dat_of_hos=null
datofhos_res=null
discharge_date=null
discharge_res=null
hos_ongoing=null
fi
else
echo "Hospitalization not applicable"
hospi=null
rea_hosp=null
echo "Reason of hospitalization: " "$rea_hosp"
dat_of_hos=null
datofhos_res=null
discharge_date=null
discharge_res=null
hos_ongoing=null
fi
echo "{">RT_EVENT.json
{
echo \"table_name\":\"RT_EVENT\", 
echo \"parent_tag\":\"Event\(s\)\", 
echo \"seq_num\":null, 
echo \"REACTIONSTARTDATE\":null, 
echo \"REACTIONSTARTDATERES\":null, 
echo \"PRIMARYSOURCEREACTION\":null, 
echo \"REACTIONMEDDRALLT\":null, 
echo \"REACTIONOUTCOME\":null, 
echo \"SERIOUSNESSDEATH\":\"$seriousness_death\", 
echo \"SERIOUSNESSHOSPITALIZATION\":\"$hospi\", 
echo \"SERIOUSNESSDISABLING\":null, 
echo \"SERIOUSNESSLIFETHREATENING\":null, 
echo \"SERIOUSNESSCONGENITALANOMALI\":null, 
echo \"SERIOUSNESSOTHER\":null, 
echo \"DRUGRESULT\":\"$alex_drug\", 
echo \"REACTIONENDDATE\":null, 
echo \"REACTIONENDDATERES\":null, 
echo \"HOSPITALIZATIONREASON\":\"$reason_of_hospitalization\", 
echo \"HOSPADMISSIONDATE_EXTENSION\":\"$dat_of_hos\", 
echo \"HOSPADMISSIONDATERES\":\"$datofhos_res\", 
echo \"HOSPDISCHARGEDATE_EXTENSION\":\"$discharge_date\", 
echo \"HOSPDISCHARGEDATERES\":\"$discharge_res\", 
echo \"HOSPITALIZATIONONGOING\":\"$hos_ongoing\", 
echo \"REACTIONONGOING_EXTENSION\":null 
echo "}"
} >>RT_EVENT.json
jsonlint-php RT_EVENT.json
if [ $? -eq 0 ]
then
cat RT_EVENT.json>>finaljson.json
echo ",">>finaljson.json
else
echo "{">RT_EVENT.json
{
echo \"table_name\":\"RT_EVENT\", 
echo \"parent_tag\":\"Event\(s\)\", 
echo \"seq_num\":null, 
echo \"REACTIONSTARTDATE\":null, 
echo \"REACTIONSTARTDATERES\":null, 
echo \"PRIMARYSOURCEREACTION\":null, 
echo \"REACTIONMEDDRALLT\":null, 
echo \"REACTIONOUTCOME\":null, 
echo \"SERIOUSNESSDEATH\":null, 
echo \"SERIOUSNESSHOSPITALIZATION\":null, 
echo \"SERIOUSNESSDISABLING\":null, 
echo \"SERIOUSNESSLIFETHREATENING\":null, 
echo \"SERIOUSNESSCONGENITALANOMALI\":null, 
echo \"SERIOUSNESSOTHER\":null, 
echo \"DRUGRESULT\":null, 
echo \"REACTIONENDDATE\":null, 
echo \"REACTIONENDDATERES\":null, 
echo \"HOSPITALIZATIONREASON\":null, 
echo \"HOSPADMISSIONDATE_EXTENSION\":null, 
echo \"HOSPADMISSIONDATERES\":null, 
echo \"HOSPDISCHARGEDATE_EXTENSION\":null, 
echo \"HOSPDISCHARGEDATERES\":null, 
echo \"HOSPITALIZATIONONGOING\":null, 
echo \"REACTIONONGOING_EXTENSION\":null 
echo "},"
} >>RT_EVENT.json
cat RT_EVENT.json>>finaljson.json
fi
#lab test data
jsonlint-php RT_LABTEST.json
if [ $? -eq 0 ]
then
cat RT_LABTEST.json>>finaljson.json
echo ",">>finaljson.json
else
echo "[">RT_LABTEST.json
{
echo "{"
echo  \"table_name\":\"RT_LABTEST\", 
echo \"parent_tag\":\"Labtest_Information\", 
echo \"seq_num\":null, 
echo \"TESTNAME\":null, 
echo \"TESTRESULT\":null, 
echo \"TESTRESULTUNIT\":null, 
echo \"TESTDATE\":null, 
echo \"TESTDATERES\":null, 
echo \"LOWTESTRANGE\":null, 
echo \"HIGHTESTRANGE\":null, 
echo \"MOREINFORMATION\":null 
echo "}" 
echo "],"
} >>RT_LABTEST.json
cat RT_LABTEST.json>>finaljson.json
fi

#treatment
#treatment not applicable
treatment_top_co=$(< pdfxml.xml grep -i "Detalhar os eventos apresentados, data de início, data de término e a evolução (recuperado, não recuperado, etc) de " -A10000|grep -i "</page>" -m1 -B10000|grep "Tratamento"|awk -F 'left' '{print $1}'|awk -F 'top=' '{print $2}'|sed 's/\"//g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g')
treatment_bottom_co=$(< pdfxml.xml grep -i "Descrever o tratamento adotado para os eventos, tais como medicamentos utilizados (prescritos ou auto-medicação)," -A10000|grep -i "</page>" -m1 -B10000|grep -i "Descrever o tratamento adotado para os eventos, tais como medicamentos utilizados (prescritos ou auto-medicação),"|awk -F 'left' '{print $1}'|awk -F 'top=' '{print $2}'|sed 's/\"//g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g')
treatment_left_co=$(< pdfxml.xml grep -i "Detalhar os eventos apresentados, data de início, data de término e a evolução (recuperado, não recuperado, etc) de " -A10000|grep -i "</page>" -m1 -B10000|grep "Tratamento"|awk -F 'width' '{print $1}'|awk -F 'left=' '{print $2}'|sed 's/\"//g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g')
treatment_right_co=$(get_coordinate "$treatment_top_co" "$treatment_bottom_co" "Não aplicável")
treatment_applicable_check=$(lot_expiry_info_extract "$treatment_top_co" "$treatment_bottom_co" "$treatment_left_co" "$treatment_right_co")
treatment_applicable_check=$(bash checkbox_module.sh "$treatment_applicable_check")
echo "Treatment section not applicable: $treatment_applicable_check"
if [ "$treatment_applicable_check" == 0 ]
then
after_data=$(< htmlcomb.comb grep -i "Tratamento" -A100)
echo "Treatment after data:" "$after_data"
< htmlcomb.comb grep -i "Tratamento" -A100|grep -i "Ação tomada com o produto Alexion em decorrência dos eventos" -B100|grep -v "Ação tomada com o produto Alexion em decorrência dos eventos"|grep -i "procedimentos, etc." -m1 -A100|grep -v "procedimentos, etc.">treatment_text
lines=$(< treatment_text wc -l)
for((i=1;i<=$lines;i++))
do 
value=$(< treatment_text head -1)
echo "Treatment value:" "$value"
if [[ "$value" =~ [A-Za-z] ]]
then
treatment_data="$value"
fi
sed -i "1d" treatment_text
done
echo "Treatment before splittext:" "$treatment_data"
#treatment_data=$(python3 -c "from splittextarea import split_combdata; print (split_combdata('$treatment_data'))")
treatment_data=`echo "$treatment_data"|awk -F'[|][|]' '{$1="";$2="";$3="";$4="";print}'`
echo "Treatment after splittext:" "$treatment_data"
treatment_file="$treatment_data"
treatment_data=$(echo "$treatment_data"|sed 's/\*//g'|sed 's/\"//g'|sed 's/&#34//g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g'|sed 's/\.$//g')
echo "Treatment data:" "$treatment_data"
else
echo "Treatment not applicable"
treatment_data=null
fi
echo "Treatment:" $treatment_data
#event description
after_data=$(< htmlcomb.comb grep -E 'Eventos' -A1000)
echo "Event Description after data:" "$after_data"
< htmlcomb.comb grep -E 'Eventos' -A1000|grep -i "cada evento descrito" -A10|grep -i -E "Lote:|Causalidade" -B100 -m1|grep -ive "Lote:" -e "Causalidade"|grep -v "cada evento descrito">event_des
lines=$(< event_des wc -l)
for((i=1;i<=$lines;i++))
do 
value=$(< event_des head -1)
echo "Event Description value:" "$value"
if [[ "$value" =~ [A-Za-z] ]]
then
event_data="$value"
fi
sed -i "1d" event_des
done
echo "Event Description before splittext:" "$event_data"
#event_data=$(python3 -c "from splittextarea import split_combdata; print (split_combdata('$event_data'))")
event_data=`echo "$event_data"|awk -F'[|][|]' '{$1="";$2="";$3="";$4="";print}'`
echo "Event Description after splittext:" "$event_data"
echo "$event_data">NarrativeFile.txt
echo "TREATMENT:" "$treatment_file">>NarrativeFile.txt
event_data=$(echo "$event_data"|sed 's/\*//g'|sed 's/&#34//g'|sed 's/\"//g'|sed $'s/[^[:print:]\t]//g'|sed 's/“//g'|sed 's/”//g'|sed 's/\.$//g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g')
event_data=$(echo "$event_data". "TREATMENT:""$treatment_data".)
echo "Event Description data before empty check:" "$event_data"
if [ -z "$event_data" ]
then
event_data=null
fi
echo "Event Description:" "$event_data"
#medical history
history_not_applicable=$(< layout grep -i "Histórico Médico" -A100|grep -i "Histórico Médico"|grep -E -o ".{0,10}Não aplicável"|grep -i "✔\|X\|■")
history_not_applicable=$(bash checkbox_module.sh "$history_not_applicable")
echo "Medical history not applicable: $history_not_applicable"
if [ "$history_not_applicable" == 0 ]
then
echo "Medical history applicable"
after_data=$(< htmlcomb.comb grep -i "Histórico Médico" -A100)
before_data=$(< htmlcomb.comb grep -i "Histórico Médico" -A100|grep -i "Produto Alexion" -B100 -m1)
echo "History data after:" "$after_data"
echo "History data before:" "$before_data"
history=$(< htmlcomb.comb grep -i "Histórico Médico" -A100|grep -i "Produto Alexion" -B100 -m1|grep -v "Produto Alexion"|grep -i "Alexion" -m1 -A100|grep -v "Alexion")
echo "History data 1:" "$history"

#history=$(python3 -c "from splittextarea import split_combdata; print (split_combdata('$history'))")
history=`echo "$history"|awk -F'[|][|]' '{$1="";$2="";$3="";$4="";print}'`
echo "History data 2:" "$history"
history=$(echo "$history"|sed 's/\*//g'|sed 's/&#34//g'|sed 's/\"//g'|sed $'s/[^[:print:]\t]//g'|sed 's/“//g'|sed 's/”//g'|sed 's/^[[:space:]]*//g'|sed 's/[[:space:]]*$//g')
echo "History data 3:" "$history"
else
echo "medical history not applicable"
history=null
fi
echo "Medical History:" "$history"

communication_correspondence=`echo "$contact_type"|sed "s/I/Inbound/g"|sed "s/O/Outbound/g"`
event_data="$event_data""Communication Correspondence: "$communication_correspondence
#Summary section
echo "{">RT_SUMMARY.json
{
echo \"table_name\": \"RT_SUMMARY\",
echo \"parent_tag\": \"Summary_Information\", 
echo \"PATINFO_EXTENSION\": null, 
echo \"HCPINFO_EXTENSION\": null, 
echo \"NARRATIVEINCLUDECLINICAL\": \"$event_data\", 
echo \"SENDERCOMMENT\": null 
echo "}"
} >>RT_SUMMARY.json

#relevant medical history
echo "[">RT_pat_relevant_history.json
{
echo "{"
echo \"table_name\": \"RT_PAT_RELEVANT_HISTORY\", 
echo \"parent_tag\": \"RT_PAT_RELEVANT_HISTORY\", 
echo \"seq_num\": null, 
echo \"PATIENTEPISODENAME\": \"$history\" 
echo "}" 
echo "]"
} >>RT_pat_relevant_history.json

##Reference section
echo "{">RT_references.json
{
echo \"table_name\": \"RT_REFERENCES\",
echo \"parent_tag\": \"RT_REFERENCES\", 
echo \"CASENARRATIVE\": \"$event_data\" 
echo "}"
} >>RT_references.json


sed -i 's/\bNão soube informar a indicação\b//g' finaljson.json
sed -i 's/\b(não soube informar quais)\b//g' finaljson.json
sed -i 's/\bnão soube informar\b//g' finaljson.json
sed -i 's/\bnão informou qual\b//g' finaljson.json
sed -i 's/\ba indicação\b//g' finaljson.json 
sed -i 's/\bnão infdrmou\b//g' finaljson.json
sed -i 's/\bNão houve\b//g' finaljson.json
sed -i 's/\bnão houve\b//g' finaljson.json
sed -i 's/\binfdrmou\b//g' finaljson.json
sed -i 's/\bnão informou\b//g' finaljson.json
sed -i 's/\bsoube informar\b//g' finaljson.json
sed -i 's/\bpor esquecimento\b//g' finaljson.json
sed -i 's/\binformou\b//g' finaljson.json
sed -i 's/\bmencionou\b//g' finaljson.json
sed -i 's/\bNão informado\b//g' finaljson.json
sed -i 's/\bquestionada\b//g' finaljson.json
sed -i 's/\bnão questionado\b//g' finaljson.json
sed -i 's/\bNão questionado\b//g' finaljson.json
sed -i 's/\bNÃO QUESTIONADO\b//g' finaljson.json
sed -i 's/\bNA\b//g' finaljson.json
sed -i 's/\"NSI\"/\"\"/g' finaljson.json
sed -i 's/\bnão possui\b//g' finaljson.json
sed -i 's/\baplicou\b//g' finaljson.json

jsonlint-php RT_pat_relevant_history.json
if [ $? -eq 0 ]
then
cat RT_pat_relevant_history.json>>finaljson.json
echo ",">>finaljson.json
else
echo "[">RT_pat_relevant_history.json
{
echo "{"
echo \"table_name\": \"RT_PAT_RELEVANT_HISTORY\", 
echo \"parent_tag\": \"RT_PAT_RELEVANT_HISTORY\", 
echo \"seq_num\": null, 
echo \"PATIENTEPISODENAME\": null 
echo "}" 
echo "],"
} >>RT_pat_relevant_history.json
cat RT_pat_relevant_history.json>>finaljson.json
fi

jsonlint-php RT_references.json
if [ $? -eq 0 ]
then
cat RT_references.json>>finaljson.json
echo ",">>finaljson.json
else
echo "{">RT_references.json
{
echo \"table_name\": \"RT_REFERENCES\",
echo \"parent_tag\": \"RT_REFERENCES\", 
echo \"CASENARRATIVE\": null 
echo "},"
} >>RT_references.json
cat RT_references.json>>finaljson.json
fi

jsonlint-php RT_SUMMARY.json
if [ $? -eq 0 ]
then
cat RT_SUMMARY.json>>finaljson.json
else
echo "{">RT_SUMMARY.json
{
echo \"table_name\": \"RT_SUMMARY\",
echo \"parent_tag\": \"Summary_Information\", 
echo \"PATINFO_EXTENSION\": null, 
echo \"HCPINFO_EXTENSION\": null, 
echo \"NARRATIVEINCLUDECLINICAL\": null, 
echo \"SENDERCOMMENT\": null 
echo "}"
} >>RT_SUMMARY.json
cat RT_SUMMARY.json>>finaljson.json
fi
echo "]">>finaljson.json

sed -i 's/✔//g' finaljson.json
sed -i 's/■//g' finaljson.json
#sed -i "s/'/ /g" finaljson.json
sed -i 's/\" \"/null/g' finaljson.json
sed -i 's/\"\"/null/g' finaljson.json
sed -i 's/\"null\"/null/g' finaljson.json
#sed -i "s/[^a-zA-Z0-9_.,-|*#;)(]/ /g" finaljson.json

jsonlint-php finaljson.json
echo $?
