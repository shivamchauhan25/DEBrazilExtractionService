#!/bin/bash
#checking file exists in the directory
if [ -f "$1" ]
then
json_lint=$(dpkg --list|grep "jsonlint")
if [ -z "$json_lint" ]
then
echo "Extraction failed. jsonlint package does not exist."
else
echo "File:" "$1" "exists"

#creating a work folder
mkdir -p work/
mkdir -p work/"work_""$2"
#creating final folder
mkdir -p final/
#copying all shell,python and processing pdf to work folder
cp -- *.sh work/"work_""$2"
cp -- *.py work/"work_""$2"
cp con_header work/"work_""$2"
cp frequency_config work/"work_""$2"
mv *"$1" work/"work_""$2"

cd work/"work_""$2" || exit
lg_path=$(cat sh_log_file_path.txt)
exec 2> "$lg_path"/"$1".log

#preparing linux executables
dos2unix -- *.sh
#calling extraction script
bash brazil_extraction.sh "checkbox_marked_$1"
#copying final json to final folder
cp finaljson.json ../../final/"$2".json
# cp NarrativeFile.txt ../final/
fi
else
echo "File" "$1" "not found"
fi
