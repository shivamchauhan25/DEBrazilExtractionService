#!/bin/bash
input_text=$1

get_checkbox_value(){

checkbox_var=$(echo "$input_text" | tr -s "\n" " "|grep "X\|☒\|\|\|\|\|\|✔\|X\|■")
[ -z "$checkbox_var" ] && echo 0 || echo 1

}

retval=$( get_checkbox_value )

if [ "$retval" == "1" ]
then
    echo 1
else
    echo 0
fi