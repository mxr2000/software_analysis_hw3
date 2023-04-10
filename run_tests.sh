#!/bin/bash

while IFS=',' read -ra array; do
  test+=("${array[0]}")
  result+=("${array[1]}")
done < tests.csv   

failed_dir="failed_dir$1"
passed_dir="passed_dir$1"

rm -rf "$failed_dir"
rm -rf "$passed_dir"

mkdir "$failed_dir"
mkdir "$passed_dir"


for i in `seq 1 ${#test[@]}`
do
    if ./tcas$1  ${test[$i-1]} | grep -q "${result[$i-1]/ /}"; then
        echo $i:P
        gcov ./tcas$1
        mv "tcas$1.c.gcov" "${passed_dir}/test${i}.gcov"
        :
    else
        echo $i:F
        gcov ./tcas$1
        mv "tcas$1.c.gcov" "${failed_dir}/test${i}.gcov"
    fi


done

