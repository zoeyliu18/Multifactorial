#!/bin/bash

language = "$1"

#for file in "/Users/Silverlining/Desktop/ud-treebanks-v2.6/test/*.conllu"
for file in "/workspace/raw_data/'$language'/*.conllu"
do

    echo $file

    cat $file | grep "^[0-9]" | cut -f3 >> $language + '_' + lemma

done

cat $language + '_' + lemma | sort | uniq -c | sort -rn > $language + '_' + lemma_count

rm $language + '_' + lemma