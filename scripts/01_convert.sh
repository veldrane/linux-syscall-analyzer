#!/bin/bash

# Well, this crazy oneliner convert the raw strace output into csv
# The main goal is: 
# 	- remove multiple spaces
#	- change all semicolons to comas becouse semicolons are used like a separator
#	- Format and convert options of the syscall and running time
#
# Parameter is the raw strace output

cat $1 | tr -s ' ' | sed s/\;/\,/g | sed -e "s/\s/\;/" | sed -e "s/\s\=\s/\;/" | sed -e "s/\=\s/\;/" | sed -e "s/(/\;/" | sed -e "s/);/;/" | sed -e "s/ </;/" | sed -e 's/>//' | sed s/\"//g 
