# Multifactorial
 Code and data for "A Multifactorial Approach to Constituent Orderings"

## source data

*CoNLLU files*
 
Gold-Standard: >[Universal Dependencies](https://github.com/UniversalDependencies)

Larger files: >[CoNLL 2017 Shared Task - Automatically Annotated Raw Texts and Word Embeddings](https://lindat.mff.cuni.cz/repository/xmlui/handle/11234/1-1989)  


*Word embeddings*

 >[fastText](https://fasttext.cc/docs/en/crawl-vectors.html)
 
### Extract PP data, words, and pairs from gold-standard UD treebanks ###
```python3 code/ud_pp.py --input PATH_TO_UD_DATA --output OUTPUT_PATH```

For each language, the code above generates:
(1) Language_pp.csv
(2) Language_words.txt
(3) Language_pairs.txt

### Counting word frequency from Larger CoNLLU files ###
```./word_count.sh``` (modify directory within the shell script as needed)

Run for each language; this generates Language_wc file

### Extracting Head-Dependent pairs from Larger CoNLLU files ###
```python3 code/hd.py --input PATH_TO_LARGER_FILES --output OUTPUT_PATH --language FULL_LANGUAGE_NAME(e.g. English)```

Run for each language; this generates Language_pairs_all.txt 

### Counting Head-Dependent pair frequency ###
```cat PAIR_FILE | sort | uniq -c | sort -rn > OUTPUT_FILE```

E.g. ```cat English_pairs_all.txt | sort | uniq -c | sort -rn > English_jc```

### Getting embeddings for each word ###
Again, take English as an example ```join -j 1 <(sort English_words.txt) <(sort cc.en.300.vec) > English_em```

### Getting data for regression ###
```python3 code/factors.py --pp PATH_TO_Language_PP.csv --em PATH_TO_fastText_embeddings --new OUTPUT_PATH_TO_NEW_Language_PP.csv --regress OUTPUT_PATH_TO_Regression_Data --language FULL_LANGUAGE_NAME```

E.g. ```python3 code/factors.py --pp data/English_pp.csv --em data/cc.en.300.vec --new data/English_pp.csv --regress data/English_regression.csv --language English```

### Run Analysis ###
