# Multifactorial
 Code and data for "A Multifactorial Approach to Constituent Orderings"

## source data

*CoNLLU files*
 
Gold-Standard: >[Universal Dependencies](https://github.com/UniversalDependencies)

Larger files: >[CoNLL 2017 Shared Task - Automatically Annotated Raw Texts and Word Embeddings](https://lindat.mff.cuni.cz/repository/xmlui/handle/11234/1-1989)  

*Word embeddings*

 >[fastText](https://fasttext.cc/docs/en/crawl-vectors.html)
 
## Extract PP data from gold-standard UD treebanks ##
```python3 code/ud_pp.py --input PATH_TO_UD_DATA --output OUTPUT_PATH```

## Counting word frequency from Larger CoNLLU files ##
```./word_count.sh``` (modify directory within the shell script as needed)

## Extracting Head-Dependent pairs from Larger CoNLLU files ##
