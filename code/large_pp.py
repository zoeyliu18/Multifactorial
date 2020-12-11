### This script extracts V NP P tuples from CoNLL Multilingual Parsing Shared Task ###

#usr/bin/env python3

HAPPY = True

import glob, os, io, argparse, csv

### Reading CoNLL formatted file sentence by sentence ###

def conll_read_sentence(file_handle):

	sent = []

	for line in file_handle:
		line = line.strip('\n')
	
		if line.startswith('#') is False :
			toks = line.split("\t")			
		
			if len(toks) == 1:
				return sent 
			else:
				if toks[0].isdigit() == True:
					sent.append(toks)

	return None


### Get all verbs from a sentence ###

def verb_list(sentence):

	verbs = []

	for tok in sentence:
		if tok[3] == 'VERB':
			verbs.append(tok[0])

	return verbs


### Get the syntactic head of a token ###

def head(index, sentence):

	tok = sentence[int(index) - 1]

	h_idx = int(tok[6])

	if h_idx != 0:
		return sentence[h_idx - 1]

	return 'ROOT'


### Get the syntactic dependents of a token ###

def dependents(index, sentence):

	dependent = []

	for tok in sentence:
		if tok[6] == index:
			dependent.append(tok[0])

	if len(dependent) != 0:
		return dependent

	return None


### Get ALL PP dependents of the head verb ###

def extract_tuples(verb_index, sentence):

	v_d = dependents(verb_index, sentence)

	tuples = []

	if v_d is not None:

		for d in v_d:
			d_tok = sentence[int(d) - 1]
		
			if d_tok[7] == 'obl':
				d_d = dependents(d_tok[0], sentence)

				if d_d is not None:

					adp_list = []
				
					for z in d_d:
						z_tok = sentence[int(z) - 1]

						if z_tok[3] == 'ADP' and z_tok[7] == 'case':
							adp_list.append(int(z_tok[0]))

					if len(adp_list) > 0:
						adp_list.sort()

						adp = adp_list[0]

						pp_adp = sentence[int(adp) - 1][2]
						pp_np = d_tok[2]
						v_tok = sentence[int(verb_index) - 1][2]

						tuples.append(v_tok + ' ' + pp_np + ' ' + pp_adp)

	return tuples


####### Get the subtree of a syntactic head ######

def subtree_generate(index, sentence):

	idxlist = [index]
	min_idx = len(sentence)
	max_idx = 0

	while len(idxlist) != 0:
		i = idxlist.pop()
	
		if int(i) < min_idx:
			min_idx = int(i)
	
		if int(i) > max_idx:
			max_idx = int(i)
	
		i_d = dependents(i, sentence)
	
		if i_d is not None:
			for d in i_d:
				idxlist.append(d)

	subtree = sentence[min_idx - 1 : max_idx]

	subtree_idx = []

	for idx in range(min_idx - 1, max_idx):
		subtree_idx.append(int(idx))

	subtree_idx.sort() 

	return subtree, subtree_idx


#### Getting data from one language ####

def Expelliarmus(file_handle, directory, language):

	data = []

	with io.open(directory + '/' + file_handle, encoding = 'utf-8') as f:
		sent = conll_read_sentence(f)

		while sent is not None:
			verbs = verb_list(sent)

			for v in verbs:
				tuples = extract_tuples(v, sent)

				if len(tuples) != 0:
					for tok in tuples:
						data.append(tok)

			sent = conll_read_sentence(f)

	return data

if __name__ == '__main__':

	parser = argparse.ArgumentParser()
	parser.add_argument('--input', type = str, help = 'input path to UD directory')
	parser.add_argument('--output', type = str, help = 'output path')
	parser.add_argument('--language', type = str, help = 'language being computed')


	args = parser.parse_args()

	path = args.input
	os.chdir(path)


	if HAPPY:
	
		language = args.language

		tuples_out = io.open(args.output + language + '_tuples_all.txt', 'w', newline = '', encoding = 'utf-8')

		for file in os.listdir(path):
			if file.endswith('.conllu'):

				all_tuples = Expelliarmus(file, path, language)

				for tok in all_tuples:
					tuples_out.write(tok + '\n')




