# Multifactorial
 Code and data for "A Multifactorial Approach to Constituent Orderings"

## source data

*CoNLLU files*
 
Gold-Standard: >[Universal Dependencies](https://github.com/UniversalDependencies)

Larger files: >[CoNLL 2017 Shared Task - Automatically Annotated Raw Texts and Word Embeddings](https://lindat.mff.cuni.cz/repository/xmlui/handle/11234/1-1989)  


*Word embeddings*

 >[fastText](https://fasttext.cc/docs/en/crawl-vectors.html)
 
### 1. Extract PP data, words, and pairs from gold-standard UD treebanks ###
```python3 code/ud_pp.py --input PATH_TO_UD_DATA --output OUTPUT_PATH```

For each language, the code above generates:
*(1) Language_pp.csv*
*(2) Language_words.txt*
*(3) Language_tuples.txt*

### 2. Counting word frequency from Larger CoNLLU files ###
```./word_count.sh``` (modify directory within the shell script as needed)

Run for each language; this generates Language_wc file

### Alternative: Use wordfreq to count ###
```python3 code/freq.py --path PATH_TO_Language_words --language FULL_LANGUAGE_NAME --code LANGUAGEU_CODE```

E.g. ```pytho3 code/freq.py --path data/ --language English --code en```

### Extracting Head-Dependent pairs from Larger CoNLLU files ###
```python3 code/hd.py --input PATH_TO_LARGER_FILES --output OUTPUT_PATH --language FULL_LANGUAGE_NAME(e.g. English)```

Run for each language; this generates ```Language_pairs_all.txt```

### 3. Counting Head-Dependent pair frequency if calculating PMI ###
```cat PAIR_FILE | sort | uniq -c | sort -rn > OUTPUT_FILE```

E.g. ```cat English_pairs_all.txt | sort | uniq -c | sort -rn > English_jc```

### 4. Getting embeddings for each word ###
Again, take English as an example ```join -j 1 <(sort English_words.txt) <(sort cc.en.300.vec) > English_em```

### 5. Train language models for selected language ###
Follow [Gulordava et al. (2018)](https://github.com/facebookresearch/colorlessgreenRNNs)

### 6. Calculate contextual predictability ###
```python3 code/context.py --data PATH_TO_TRAIN/DEV/TEST --model MODEL_NAME --pp PATH_TO_Language_pp.csv --language FULL_LANGUAGE_NAME```

E.g. ```python3 code/context.py --data model/ --model en.pt --pp data/ --language English```


### 7. Getting data for regression ###
```python3 code/factors.py --pp PATH_TO_Language_pp.csv --em PATH_TO_fastText_embeddings --regress OUTPUT_PATH_TO_Regression_Data --language FULL_LANGUAGE_NAME```

E.g. ```python3 code/factors.py --pp data/ --em data/cc.en.300.vec --language English```

This generates ```Language_regression.csv``` for each language

### 8. Run Analysis ###

See ```code/analysis.R``` for details
