# Shell Utilities
sudo apt install -y python3-pip

sudo pip3 install --upgrade pip

sudo  apt-get install -y libpq-dev
sudo  apt-get update
sudo  apt-get install python3-psycopg2
sudo  pip3 install psycopg2

sudo apt-get install -y jsonlint

sudo apt-get install dos2unix

sudo apt-get install -y poppler-utils

sudo apt-get update --fix-missing

# Extraction Script 
The main extraction script is "extraction.sh"

Executed as:

Copy the PDF in the Extractor folder

`./extraction.sh <PDF_FILE_NAME> <REQUEST_ID>`

Output: <REQUEST_ID>.json



