### This script extracts double PP constructions from UD treebanks ###

#usr/bin/env python3

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


### Get exactly two PP dependents on the same side of the head verb ###

def extract_pp(verb_index, sentence):

	v_d = dependents(verb_index, sentence)

	pp_list = {}

	if v_d is not None:

		preverbal_pp = []
		postverbal_pp = []

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

						adp_toks = []
						for adp in adp_list:
							adp_toks.append(sentence[int(adp) - 1][2])

						adp = ' '.join(w for w in adp_toks)

						### P NP V ###

						if adp_list[-1] < int(d_tok[0]) and int(d_tok[0]) < int(verb_index):
							preverbal_pp.append([verb_index, d_tok[0], str(adp), 'prepositional', 'preverbal'])

						### P NP P V ###

						if adp_list[0] < int(d_tok[0]) and adp_list[-1] > int(d_tok[0]) and adp_list[-1] < int(verb_index):
							preverbal_pp.append([verb_index, d_tok[0], str(adp), 'circumpositional', 'preverbal'])

						### NP P V ###

						if adp_list[0] > int(d_tok[0]) and adp_list[-1] < int(verb_index):
							preverbal_pp.append([verb_index, d_tok[0], str(adp), 'postpositional', 'preverbal'])

						### V P NP ###

						if adp_list[0] > int(verb_index) and adp_list[-1] < int(d_tok[0]):
							postverbal_pp.append([verb_index, d_tok[0], str(adp), 'prepositional', 'postverbal'])

						### V P NP P ###

						if adp_list[0] > int(verb_index) and adp_list[0] < int(d_tok[0]) and adp_list[-1] > int(d_tok[0]):
							postverbal_pp.append([verb_index, d_tok[0], str(adp), 'circumpositional', 'postverbal'])

						### V NP P ###

						if adp_list[0] > int(d_tok[0]) and int(d_tok[0]) > int(verb_index):
							postverbal_pp.append([verb_index, d_tok[0], str(adp), 'postpositional', 'postverbal'])


		if len(preverbal_pp) == 2 and len(postverbal_pp) == 2:
			pp_list['Preverbal'] = preverbal_pp
			pp_list['Postverbal'] = postverbal_pp

		if len(preverbal_pp) == 2 and len(postverbal_pp) != 2:
			pp_list['Preverbal'] = preverbal_pp

		if len(preverbal_pp) != 2 and len(postverbal_pp) == 2:
			pp_list['Postverbal'] = postverbal_pp


	return pp_list


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

	data = [['Sentence', 'Context_PP1', 'Context_PP2', 'Verb', 'PP1', 'PP2', 'PP1_len', 'PP2_len', 'Adp1', 'Adp2', 'NP1', 'NP2', 'PP1_Pronom', 'PP2_Pronom', 'PP1_Type', 'PP2_Type', 'Position', 'Language']]
	pairs = []

	with io.open(directory + '/' + file_handle, encoding = 'utf-8') as f:
		sent = conll_read_sentence(f)

		while sent is not None:
			verbs = verb_list(sent)

			for v in verbs:
				pp_list = extract_pp(v, sent)

				if len(pp_list) != 0:
					for position, pps in pp_list.items():

						pp1 = ''
						pp2 = ''

						if int(pps[0][1]) < int(pps[1][1]):
							pp1 = pps[0]
							pp2 = pps[1]
						else:
							pp1 = pps[1]
							pp2 = pps[0]

						v_tok = sent[int(v) - 1][2]

						pp1_np = sent[int(pp1[1]) - 1][2]
						pp1_pronom = sent[int(pp1[1]) - 1][3]
						pp1_adp = pp1[2]
						pp1_type = pp1[3]
						pp1_subtree, pp1_subtree_idx = subtree_generate(pp1[1], sent)
						pp1_toks = ' '.join(w[1] for w in pp1_subtree)
						pp1_len = len(pp1_subtree_idx)
					
						context_pp1 = pp1_toks
						if pp1_subtree_idx[0] != 0:
							context_pp1 = ' '.join(w[1] for w in sent[ : pp1_subtree_idx[0]]) + ' ' + pp1_toks
						
						pairs.append(v_tok + ' ' + pp1_np)

						pp2_np = sent[int(pp2[1]) - 1][2]
						pp2_pronom = sent[int(pp2[1]) - 1][3]
						pp2_adp = pp2[2]
						pp2_type = pp2[3]
						pp2_subtree, pp2_subtree_idx = subtree_generate(pp2[1], sent)
						pp2_toks = ' '.join(w[1] for w in pp2_subtree)
						pp2_len = len(pp2_subtree_idx)
					
						context_pp2 = pp2_toks
						if pp1_subtree_idx[0] != 0:
							context_pp2 = ' '.join(w[1] for w in sent[ : pp1_subtree_idx[0]]) + ' ' + pp2_toks

						pairs.append(v_tok + ' ' + pp2_np)

						sent_toks = ' '.join(w[1] for w in sent)

					#data = [['Sentence', 'Context_PP1', 'Context_PP2', 'Verb', 'PP1', 'PP2', 'PP1_len', 'PP2_len', 'Adp1', 'Adp2', 'NP1', 'NP2', 'PP1_Type', 'PP2_Type', 'Position']]
						data.append([sent_toks, context_pp1, context_pp2, v_tok, pp1_toks, pp2_toks, pp1_len, pp2_len, pp1_adp, pp2_adp, pp1_np, pp2_np, pp1_pronom, pp2_pronom, pp1_type, pp2_type, position, language])

			sent = conll_read_sentence(f)

	return data, set(pairs)

if __name__ == '__main__':

	parser = argparse.ArgumentParser()
	parser.add_argument('--input', type = str, help = 'input path to UD directory')
	parser.add_argument('--output', type = str, help = 'output path')


	args = parser.parse_args()

	path = args.input
	os.chdir(path)


	for directory in glob.glob('*'):
		for file in os.listdir(directory):
			if file.endswith('.conllu'):
				
				language = directory.split('-')[0][3 : ]
				pp_data, pp_pairs = Expelliarmus(file, directory, language)

				if len(pp_data) >= 101:

					print(file)

					output = io.open(args.output + language + '_pp.csv', 'w', newline = '', encoding = 'utf-8')
					writer = csv.writer(output)

					for pp in pp_data:
						writer.writerow(pp)

					words = []
					words_out = io.open(args.output + language + '_words.txt', 'w', newline = '', encoding = 'utf-8')
				
					pairs_out = io.open(args.output + language + '_pairs.txt', 'w', newline = '', encoding = 'utf-8')
				
					for tok in pp_pairs:
						pairs_out.write(tok + '\n')

						for w in tok.split():
							words.append(w)

					for w in set(words):
						words_out.write(w + '\n')




