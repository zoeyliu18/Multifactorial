#!/bin/bash


#for file in "/Users/Silverlining/Desktop/ud-treebanks-v2.6/test/*.conllu"
for file in "/workspace/raw_data/English/*.conllu"
do

    echo $file

    cat $file | grep "^[0-9]" | cut -f3 >> lemma

done

cat lemma | sort | uniq -c | sort -rn > English_wc

rm lemma